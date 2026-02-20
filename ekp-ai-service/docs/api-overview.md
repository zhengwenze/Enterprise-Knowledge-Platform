# EKP API Overview

This document provides an overview of the Enterprise Knowledge Platform API endpoints.

## Services

### AI Service (Port 8000)

The AI Service handles document processing and question answering using RAG (Retrieval-Augmented Generation).

**Base URL**: `http://localhost:8000`

**Swagger UI**: `http://localhost:8000/docs`

**ReDoc**: `http://localhost:8000/redoc`

### Business Service (Port 8080)

The Business Service handles user management and business logic.

**Base URL**: `http://localhost:8080`

**Swagger UI**: `http://localhost:8080/swagger-ui.html`

## API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check service health status |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents` | Upload a new document (PDF) |
| GET | `/api/v1/documents` | List all documents (paginated) |
| GET | `/api/v1/documents/{id}` | Get document details |
| DELETE | `/api/v1/documents/{id}` | Delete a document |

### Question Answering

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/qa` | Ask a question and get an answer |
| GET | `/api/v1/qa/{session_id}` | Get Q&A session details |
| GET | `/api/v1/qa/history` | Get Q&A history (paginated) |

## Request/Response Examples

### Upload Document

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

**Response**:
```json
{
  "id": 1,
  "title": "document.pdf",
  "status": "PENDING",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Ask Question

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/qa" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of this document?",
    "top_k": 5
  }'
```

**Response**:
```json
{
  "session_id": 1,
  "question": "What is the main topic of this document?",
  "answer": "The main topic of this document is...",
  "sources": [
    {
      "chunk_id": 1,
      "document_id": 1,
      "document_title": "document.pdf",
      "content": "Relevant text chunk...",
      "relevance_score": 0.95
    }
  ],
  "response_time_ms": 1500
}
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "ValidationError",
  "message": "Invalid input parameters",
  "details": {
    "field": "question",
    "reason": "Question cannot be empty"
  }
}
```

## Authentication

Authentication will be implemented in Phase 2. Currently, all endpoints are open.

## Rate Limiting

Rate limiting will be implemented in Phase 2. Current limits:
- Document Upload: 10 per minute
- Q&A: 30 per minute

## Pagination

List endpoints support pagination with `skip` and `limit` parameters:

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 10, max: 100)

Example:
```
GET /api/v1/documents?skip=0&limit=20
```
