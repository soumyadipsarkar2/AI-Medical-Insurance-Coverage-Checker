# 🏥 AI Medical Insurance Coverage Checker

An intelligent AI-powered application that helps users understand their medical insurance policies by uploading PDF documents and asking questions about coverage, copays, and benefits.

## 🚀 Live Demo

[Deploy on Render](#deployment) - Coming Soon!

## ✨ Features

- **📄 PDF Processing**: Fast text extraction with PyMuPDF + Tesseract OCR fallback
- **🤖 AI-Powered Q&A**: LangChain + OpenAI GPT-4o-mini for intelligent document querying
- **🔍 Vector Search**: Pinecone vector database for semantic document search
- **🎨 User-Friendly UI**: Clean Streamlit interface for easy document upload and question asking
- **💾 Database Storage**: PostgreSQL for document and query history
- **🐳 Dockerized**: Everything runs with Docker Compose
- **☁️ Cloud Ready**: Easy deployment to Render, Heroku, or any cloud platform

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

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Pinecone API key

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-medical-insurance-coverage-checker.git
cd ai-medical-insurance-coverage-checker
```

### 2. Set up Environment Variables

#### Option A: Use the Setup Script (Recommended)

```bash
# Run the automated setup script
./setup.sh

# Then edit the .env file with your actual API keys
nano backend/.env
```

#### Option B: Manual Setup

```bash
# Copy and edit the environment file
cp backend/env.example backend/.env

# Edit backend/.env with your API keys:
# - OPENAI_API_KEY=sk-your-openai-api-key
# - PINECONE_API_KEY=pcn-your-pinecone-api-key
# - PINECONE_ENVIRONMENT=us-east-1-aws
# - PINECONE_INDEX_NAME=docsage-lite
```

### 3. Start the Application

```bash
docker compose up --build
```

### 4. Open the App

- **Frontend**: http://localhost:8502
- **Backend API**: http://localhost:8001

## 📖 Usage

### 1. Upload Insurance Policy PDF
- Open http://localhost:8502
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

## 🚀 Deployment

### Render Deployment

The repository includes a `render.yaml` file for automated deployment. Here's how to deploy:

#### Option 1: Blueprint Deployment (Recommended)

1. **Sign up for Render** at https://render.com
2. **Click "New +"** and select **"Blueprint"**
3. **Connect your GitHub repository**
4. **Render will automatically**:
   - Create the web service
   - Create the PostgreSQL database
   - Link them together
   - Set up the infrastructure

5. **Add your API keys** in the Environment section:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PINECONE_API_KEY`: Your Pinecone API key

6. **Deploy!** Your app will be available at: `https://ai-medical-insurance-checker.onrender.com`

#### Option 2: Manual Deployment

1. **Sign up for Render** at https://render.com
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name**: `ai-medical-insurance-checker`
   - **Environment**: `Docker`
   - **Branch**: `main`
   - **Build Command**: `docker build -t ai-medical-insurance-checker .`
   - **Start Command**: `docker run -p 10000:8501 ai-medical-insurance-checker`

5. **Create PostgreSQL Database**:
   - Go back to dashboard and create a new PostgreSQL service
   - Name: `ai-medical-insurance-db`
   - Plan: `Starter`

6. **Add Environment Variables:**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PINECONE_API_KEY`: Your Pinecone API key
   - `DATABASE_URL`: Copy from PostgreSQL service

### Environment Variables

```env
OPENAI_API_KEY=sk-your-openai-api-key
PINECONE_API_KEY=pcn-your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=docsage-lite
DATABASE_URL=postgresql://user:password@host:port/database
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you have any questions or need help:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the documentation

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) for the RAG framework
- [OpenAI](https://openai.com/) for the AI models
- [Pinecone](https://pinecone.io/) for vector search
- [Streamlit](https://streamlit.io/) for the web interface
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API

---

**Made with ❤️ for better healthcare understanding**
