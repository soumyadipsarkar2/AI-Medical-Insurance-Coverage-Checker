# 🏥 AI Medical Insurance Coverage Checker

A minimal, dockerized MVP that provides a RAG + OCR pipeline for insurance policy PDFs. Upload your insurance documents and ask questions about coverage, copays, and benefits.

## 🚀 Features

- **PDF Processing**: Fast text extraction with PyMuPDF + Tesseract OCR fallback
- **RAG Pipeline**: LangChain + Pinecone + OpenAI for intelligent document querying
- **Clean UI**: Streamlit interface for easy document upload and question asking
- **Database Storage**: PostgreSQL for document and query history
- **Dockerized**: Everything runs with Docker Compose

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Streamlit  │    │   FastAPI   │    │ PostgreSQL  │
│   Frontend  │◄──►│   Backend   │◄──►│   Database  │
│   (8501)    │    │   (8000)    │    │   (5432)    │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │   Pinecone  │
                   │ Vector DB   │
                   └─────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Pinecone API key

## 🚀 Quick Start

### 1. Set up environment variables
```bash
# Copy and edit the environment file
cp backend/env.example backend/.env
# Edit backend/.env with your API keys
```

### 2. Start the application
```bash
docker compose up --build
```

### 3. Open the app
- **Frontend**: http://localhost:8502
- **Backend API**: http://localhost:8001


## 📋 Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Pinecone API key

## 📖 Usage

### 1. Upload Insurance Policy PDF
- Open http://localhost:8501
- Click "Choose a PDF file" and select your insurance policy
- Click "Process PDF" to extract text and create embeddings
- View processing stats (pages, chunks, document ID)

### 2. Ask Questions
- Once a document is loaded, use the question input
- Ask about coverage, copays, deductibles, etc.
- Get AI-powered answers with page citations
- View response time and source information

### 3. Example Questions
- "Is MRI covered under this policy?"
- "What's the copay for emergency room visits?"
- "What's the annual deductible?"
- "Are prescription drugs covered?"
- "What's the out-of-pocket maximum?"

## 🔧 API Endpoints

### Backend (FastAPI)

- `GET /health` - Health check
- `POST /ingest` - Upload and process PDF
- `POST /ask` - Ask questions about uploaded documents

### Request/Response Examples

#### Upload PDF
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@policy.pdf"
```

Response:
```json
{
  "document_id": "uuid-here",
  "pages": 15,
  "chunks": 45
}
```

#### Ask Question
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"question": "Is MRI covered?", "k": 4}'
```

Response:
```json
{
  "answer": "Yes, MRI is covered under this policy with a $50 copay...",
  "latency_ms": 1250.5,
  "sources": [
    {"page": 8, "source": "policy.pdf"},
    {"page": 9, "source": "policy.pdf"}
  ]
}
```

## 🐳 Docker Services

- **db**: PostgreSQL 16 database
- **backend**: FastAPI application with OCR and RAG capabilities
- **frontend**: Streamlit web interface

## 🔍 How It Works

### 1. PDF Processing
- **Primary**: PyMuPDF for fast text extraction
- **Fallback**: Tesseract OCR for scanned/empty text pages
- **Chunking**: LangChain RecursiveCharacterTextSplitter (1000 chars, 200 overlap)

### 2. Vector Search
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)
- **Vector DB**: Pinecone with cosine similarity
- **Retrieval**: Top-k chunks based on question relevance

### 3. AI Generation
- **Model**: GPT-4o-mini with 0.2 temperature
- **Context**: Retrieved chunks only
- **Citations**: Page references like [p3]
- **Prompt**: Structured to use only provided context

## 📊 Database Schema

### Documents Table
```sql
CREATE TABLE documents (
    id VARCHAR PRIMARY KEY,
    filename VARCHAR NOT NULL,
    page_count INTEGER NOT NULL,
    uploaded_at TIMESTAMP NOT NULL
);
```

### Queries Table
```sql
CREATE TABLE queries (
    id VARCHAR PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    latency_ms FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

## 🚨 Troubleshooting

### Common Issues

1. **Pinecone Index Creation Fails**
   - Check API key and environment
   - Ensure you have quota for new indexes

2. **OCR Fallback Not Working**
   - Verify Tesseract is installed in container
   - Check TESSERACT_CMD path

3. **Database Connection Issues**
   - Wait for PostgreSQL to fully start
   - Check health check status

4. **Memory Issues with Large PDFs**
   - Increase Docker memory limits
   - Consider chunking very large documents

### Logs
```bash
# View all service logs
docker compose logs

# View specific service logs
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

## 🔒 Security Notes

- API keys are stored in environment variables
- No authentication implemented (MVP)
- Database runs in isolated Docker network
- Consider adding auth for production use

## 📈 Performance

- **Text Extraction**: ~1-2 seconds per page (PyMuPDF)
- **OCR Fallback**: +2-3 seconds per empty page
- **Question Answering**: ~1-3 seconds depending on complexity
- **Vector Search**: ~100-500ms for retrieval

## 🚀 Production Considerations

- Add authentication and user management
- Implement rate limiting
- Add monitoring and logging
- Use managed PostgreSQL service
- Implement document versioning
- Add backup and recovery procedures

## 📝 License

This is a demo project. Please ensure compliance with OpenAI, Pinecone, and other service terms of use.

## 🤝 Contributing

This is a minimal MVP. For production use, consider:
- Adding comprehensive error handling
- Implementing retry mechanisms
- Adding unit and integration tests
- Implementing proper logging
- Adding API documentation with OpenAPI/Swagger
