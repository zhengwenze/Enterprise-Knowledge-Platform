# EKP Infrastructure

Enterprise Knowledge Platform - Infrastructure Configuration

## Project Overview

Infrastructure configuration for the Enterprise Knowledge Platform, including Docker Compose and Kubernetes configurations.

## Tech Stack

- **Container**: Docker
- **Orchestration**: Docker Compose
- **Database**: PostgreSQL 16 with pgvector
- **Cache**: Redis 7
- **Message Queue**: Kafka

## Services

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5432 | Database with pgvector extension |
| Redis | 6379 | Cache and session storage |
| Zookeeper | 2181 | Kafka coordination |
| Kafka | 9092 | Message queue |
| AI Service | 8000 | Python FastAPI service |
| Business Service | 8080 | Spring Boot service |

## Quick Start

### Start All Services

```bash
# Linux/Mac
./up-dev.sh

# Windows PowerShell
docker-compose up -d
```

### Stop All Services

```bash
# Linux/Mac
./down-dev.sh

# Windows PowerShell
docker-compose down
```

### View Logs

```bash
docker-compose logs -f [service_name]
```

### Check Status

```bash
docker-compose ps
```

## Service URLs

After starting:

- **AI Service Swagger**: http://localhost:8000/docs
- **Business Service Swagger**: http://localhost:8080/swagger-ui.html
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Kafka**: localhost:9092

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
POSTGRES_DB=ekp_db
POSTGRES_USER=ekp_user
POSTGRES_PASSWORD=ekp_password

# Redis
REDIS_URL=redis://redis:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9093

# AI Service
OPENAI_API_KEY=your-api-key
EMBEDDING_MODEL=BAAI/bge-large-zh
```

### Database Initialization

The `init-db/` directory contains SQL scripts that run on first startup:

- `01-init-extensions.sql`: Enables pgvector extension

## Architecture

See [architecture.md](architecture.md) for detailed system architecture.

## Development

### Rebuild Services

```bash
docker-compose up -d --build
```

### Reset Database

```bash
docker-compose down -v
docker-compose up -d
```

## Production Considerations

For production deployment:

1. Use external managed services for PostgreSQL, Redis, and Kafka
2. Configure proper secrets management
3. Set up SSL/TLS certificates
4. Configure resource limits
5. Implement proper backup strategies
