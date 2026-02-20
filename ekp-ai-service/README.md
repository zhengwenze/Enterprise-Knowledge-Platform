# EKP AI Service

Enterprise Knowledge Platform - AI Service

## Project Overview

AI service for the Enterprise Knowledge Platform, providing RAG (Retrieval-Augmented Generation) capabilities including document processing, vector storage, and intelligent Q&A.

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **ML/LLM**: LangChain, Sentence Transformers
- **Database**: PostgreSQL with pgvector
- **ORM**: SQLAlchemy

## Project Structure

```
ekp-ai-service/
├── src/
│   ├── api/v1/           # API endpoints
│   │   ├── documents.py  # Document management
│   │   ├── qa.py         # Question answering
│   │   └── health.py     # Health check
│   ├── models/           # SQLAlchemy models
│   ├── config.py         # Configuration settings
│   ├── database.py       # Database connection
│   └── main.py           # FastAPI application
├── docs/                 # Documentation
├── openapi.yaml          # OpenAPI specification
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
└── Dockerfile            # Docker image
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL with pgvector extension

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

### Running

```bash
# Development mode
python src/main.py

# Or with uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

After starting the service:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/documents` | Upload document |
| GET | `/api/v1/documents` | List documents |
| GET | `/api/v1/documents/{id}` | Get document details |
| DELETE | `/api/v1/documents/{id}` | Delete document |
| POST | `/api/v1/qa` | Ask question |
| GET | `/api/v1/qa/{session_id}` | Get Q&A session |
| GET | `/api/v1/qa/history` | Get Q&A history |

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | - |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| OPENAI_API_KEY | OpenAI API key | - |
| EMBEDDING_MODEL | Sentence transformer model | BAAI/bge-large-zh |

## Development

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/
```

### Testing

```bash
pytest tests/
```

## Docker

```bash
# Build image
docker build -t ekp-ai-service .

# Run container
docker run -p 8000:8000 ekp-ai-service
```
