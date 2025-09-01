import os
import time
import uuid
from datetime import datetime
from typing import List, Optional
import fitz
import pytesseract
from PIL import Image
import io

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone as LangchainPinecone
from pinecone import Pinecone
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug: Print Pinecone configuration
print(f"DEBUG: PINECONE_API_KEY (first 10 chars): {os.getenv('PINECONE_API_KEY', 'NOT_SET')[:10]}...")
print(f"DEBUG: PINECONE_ENVIRONMENT: {os.getenv('PINECONE_ENVIRONMENT', 'NOT_SET')}")
print(f"DEBUG: PINECONE_INDEX_NAME: {os.getenv('PINECONE_INDEX_NAME', 'NOT_SET')}")

# Force the correct environment
PINECONE_ENV = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1-aws')
print(f"Using Pinecone environment: {PINECONE_ENV}")

# Initialize FastAPI app
app = FastAPI(title="AI Medical Insurance Coverage Checker")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should specify the exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
else:
    # Use SQLite for local testing
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    page_count = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)

class Query(Base):
    __tablename__ = "queries"
    
    id = Column(String, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    latency_ms = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is running"}

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Pinecone setup
print("DEBUG: About to initialize Pinecone...")
print(f"DEBUG: PINECONE_API_KEY (first 10 chars): {os.getenv('PINECONE_API_KEY', 'NOT_SET')[:10]}...")
print(f"DEBUG: PINECONE_ENVIRONMENT: {os.getenv('PINECONE_ENVIRONMENT', 'NOT_SET')}")

# Initialize Pinecone with new API
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Ensure Pinecone index exists
index_name = os.getenv("PINECONE_INDEX_NAME", "docsage-lite")
try:
    if index_name not in pc.list_indexes().names():
        print(f"Index '{index_name}' does not exist. Creating it...")
        # Note: Creating indexes requires specific configuration based on your plan
        # For now, we'll just use the existing index
        print(f"Please create the index '{index_name}' manually in your Pinecone dashboard")
    else:
        print(f"Using existing Pinecone index: {index_name}")
except Exception as e:
    print(f"Warning: Could not check Pinecone index: {e}")

# Initialize Pinecone vectorstore
try:
    # Use LangChain Pinecone with environment variables
    vectorstore = LangchainPinecone.from_existing_index(
        index_name=index_name,
        embedding=embeddings
    )
    print(f"✅ Successfully initialized Pinecone vectorstore with index: {index_name}")
except Exception as e:
    print(f"Warning: Could not initialize Pinecone vectorstore: {e}")
    vectorstore = None

# Pydantic models
class AskRequest(BaseModel):
    question: str
    k: Optional[int] = 4

class AskResponse(BaseModel):
    answer: str
    latency_ms: float
    sources: List[dict]

class IngestResponse(BaseModel):
    document_id: str
    pages: int
    chunks: int

def extract_text_from_page(page, page_num):
    """Extract text from a PDF page, with Tesseract fallback if needed"""
    # Try PyMuPDF text extraction first
    text = page.get_text("text").strip()
    
    if not text:
        # Fallback to Tesseract OCR
        try:
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Use Tesseract
            tesseract_cmd = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            text = pytesseract.image_to_string(img).strip()
            
            if text:
                print(f"Used Tesseract fallback for page {page_num + 1}")
        except Exception as e:
            print(f"Tesseract fallback failed for page {page_num + 1}: {e}")
            text = f"[Page {page_num + 1} - OCR failed]"
    
    return text

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read PDF content
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        
        document_id = str(uuid.uuid4())
        page_count = len(doc)
        
        # Extract text from each page
        all_texts = []
        for page_num in range(page_count):
            page = doc.load_page(page_num)
            text = extract_text_from_page(page, page_num)
            if text:
                all_texts.append(f"Page {page_num + 1}:\n{text}")
        
        # Combine all text
        full_text = "\n\n".join(all_texts)
        
        if not full_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from PDF")
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(full_text)
        
        # Create embeddings and store in Pinecone
        if vectorstore:
            metadatas = [
                {
                    "source": file.filename,
                    "page": i // 2 + 1,  # Approximate page number
                    "document_id": document_id
                }
                for i in range(len(chunks))
            ]
            
            # Add chunks to vectorstore
            vectorstore.add_texts(chunks, metadatas=metadatas)
        
        # Store document info in database
        db = SessionLocal()
        try:
            doc_record = Document(
                id=document_id,
                filename=file.filename,
                page_count=page_count,
                uploaded_at=datetime.utcnow()
            )
            db.add(doc_record)
            db.commit()
        finally:
            db.close()
        
        return IngestResponse(
            document_id=document_id,
            pages=page_count,
            chunks=len(chunks)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    if not vectorstore:
        raise HTTPException(status_code=500, detail="Vector store not available")
    
    start_time = time.time()
    
    try:
        # Retrieve relevant chunks
        docs = vectorstore.similarity_search(request.question, k=request.k)
        
        # Build context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create sources list
        sources = []
        for doc in docs:
            if hasattr(doc, 'metadata'):
                sources.append({
                    "page": doc.metadata.get("page", "Unknown"),
                    "source": doc.metadata.get("source", "Unknown")
                })
        
        # Build prompt
        prompt = f"""Answer only using the provided context. Cite pages like [pX]. If unsure, say you don't know.

Context:
{context}

Question: {request.question}

Answer:"""
        
        # Get response from OpenAI
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content.strip()
        latency_ms = (time.time() - start_time) * 1000
        
        # Store query in database
        db = SessionLocal()
        try:
            query_record = Query(
                id=str(uuid.uuid4()),
                question=request.question,
                answer=answer,
                latency_ms=latency_ms,
                created_at=datetime.utcnow()
            )
            db.add(query_record)
            db.commit()
        finally:
            db.close()
        
        return AskResponse(
            answer=answer,
            latency_ms=latency_ms,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
