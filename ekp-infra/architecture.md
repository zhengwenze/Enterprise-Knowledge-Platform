# EKP System Architecture

## Overview

Enterprise Knowledge Platform (EKP) is a RAG-based intelligent Q&A system designed for enterprise knowledge management.

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Application]
        API_CLIENT[API Clients]
    end

    subgraph "Gateway Layer"
        GATEWAY[API Gateway<br/>:80/443]
    end

    subgraph "Application Layer"
        BIZ[Biz Service<br/>Spring Boot<br/>:8080]
        AI[AI Service<br/>FastAPI<br/>:8000]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL<br/>+ pgvector<br/>:5432)]
        REDIS[(Redis<br/>:6379)]
        KAFKA[Kafka<br/>:9092]
    end

    subgraph "External Services"
        LLM[LLM API<br/>OpenAI/Azure]
        STORAGE[Object Storage<br/>S3/MinIO]
    end

    WEB --> GATEWAY
    API_CLIENT --> GATEWAY
    GATEWAY --> BIZ
    GATEWAY --> AI
    
    BIZ --> PG
    BIZ --> REDIS
    BIZ --> KAFKA
    
    AI --> PG
    AI --> REDIS
    AI --> KAFKA
    AI --> LLM
    AI --> STORAGE
```

## Component Details

### 1. ekp-biz-service (Business Service)

**Technology Stack:**
- Java 21
- Spring Boot 3.2
- Spring Data JPA
- Flyway (Database Migration)

**Responsibilities:**
- User authentication and authorization
- Document metadata management
- Q&A session management
- Business logic orchestration

**API Endpoints:**
- `GET /health` - Health check
- `POST /api/v1/users` - User management
- `GET /api/v1/documents` - Document listing
- `GET /api/v1/qa/sessions` - Q&A history

### 2. ekp-ai-service (AI Service)

**Technology Stack:**
- Python 3.11
- FastAPI
- LangChain
- Sentence Transformers
- pgvector

**Responsibilities:**
- Document processing (PDF parsing, chunking)
- Text embedding generation
- Vector storage and retrieval
- RAG-based question answering

**API Endpoints:**
- `GET /health` - Health check
- `POST /api/v1/documents` - Document upload
- `POST /api/v1/qa` - Question answering
- `GET /api/v1/qa/{session_id}` - Q&A session details

### 3. ekp-infra (Infrastructure)

**Components:**
- Docker Compose configuration
- PostgreSQL with pgvector extension
- Redis for caching
- Kafka for async messaging

## Data Flow

### Document Upload Flow

```mermaid
sequenceDiagram
    participant User
    participant Biz as Biz Service
    participant AI as AI Service
    participant DB as PostgreSQL
    participant Kafka
    
    User->>AI: Upload PDF document
    AI->>DB: Create document record (PENDING)
    AI->>Kafka: Publish document.uploaded event
    AI-->>User: Return document_id
    
    Note over AI,Kafka: Async Processing
    AI->>AI: Parse PDF content
    AI->>AI: Split into chunks
    AI->>AI: Generate embeddings
    AI->>DB: Store chunks & vectors
    AI->>DB: Update document status (COMPLETED)
```

### Question Answering Flow

```mermaid
sequenceDiagram
    participant User
    participant AI as AI Service
    participant DB as PostgreSQL
    participant LLM as LLM API
    
    User->>AI: POST /api/v1/qa (question)
    AI->>AI: Generate question embedding
    AI->>DB: Vector similarity search
    DB-->>AI: Return relevant chunks
    AI->>AI: Build RAG prompt
    AI->>LLM: Generate answer
    LLM-->>AI: Return answer
    AI->>DB: Store Q&A session
    AI-->>User: Return answer with sources
```

## Technology Decisions

| Component | Technology | Rationale |
|-----------|------------|-----------|
| AI Service | Python/FastAPI | Rich ML ecosystem, async support |
| Biz Service | Java/Spring Boot | Enterprise-grade, strong typing |
| Database | PostgreSQL + pgvector | ACID compliance, native vector support |
| Cache | Redis | High performance, versatile data structures |
| Message Queue | Kafka | High throughput, durability |
| Embedding | BAAI/bge-large-zh | Chinese language support, high quality |

## Deployment Architecture

```mermaid
graph LR
    subgraph "Development"
        DEV[Docker Compose]
    end
    
    subgraph "Production"
        K8S[Kubernetes Cluster]
        LB[Load Balancer]
        ING[Ingress Controller]
    end
    
    DEV --> K8S
    K8S --> LB
    K8S --> ING
```

## Security Considerations

1. **Authentication**: JWT-based authentication
2. **Authorization**: Role-based access control (RBAC)
3. **Data Encryption**: TLS for transit, encryption at rest
4. **API Security**: Rate limiting, input validation

## Performance Targets

| Metric | Target |
|--------|--------|
| Q&A Latency | < 2 seconds |
| Concurrent Users | 5+ users |
| Document Processing | < 30 seconds per document |
| Vector Search | < 100ms |
