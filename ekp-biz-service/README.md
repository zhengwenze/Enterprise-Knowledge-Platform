# EKP Business Service

Enterprise Knowledge Platform - Business Service

## Project Overview

Business service for the Enterprise Knowledge Platform, handling user management, document metadata, and business logic.

## Tech Stack

- **Language**: Java 21
- **Framework**: Spring Boot 3.2
- **Database**: PostgreSQL
- **ORM**: Spring Data JPA
- **Migration**: Flyway
- **Build**: Maven

## Project Structure

```
ekp-biz-service/
├── src/main/
│   ├── java/com/ekp/
│   │   ├── controller/    # REST controllers
│   │   ├── entity/        # JPA entities
│   │   ├── repository/    # Data repositories
│   │   ├── service/       # Business services
│   │   └── EkpBizServiceApplication.java
│   └── resources/
│       ├── application.yml    # Configuration
│       └── db/migration/      # Flyway migrations
├── pom.xml                # Maven configuration
└── Dockerfile             # Docker image
```

## Quick Start

### Prerequisites
- Java 21
- Maven 3.9+
- PostgreSQL

### Running

```bash
# Build and run
mvn spring-boot:run

# Or build JAR and run
mvn clean package
java -jar target/ekp-biz-service-0.0.1-SNAPSHOT.jar
```

### API Documentation

After starting the service:
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **OpenAPI Spec**: http://localhost:8080/api-docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

## Configuration

Application properties (see `application.yml`):

| Property | Description | Default |
|----------|-------------|---------|
| server.port | Server port | 8080 |
| spring.datasource.url | Database URL | jdbc:postgresql://localhost:5432/ekp_db |
| spring.datasource.username | Database user | ekp_user |
| spring.datasource.password | Database password | ekp_password |

## Database Schema

The service uses Flyway for database migrations. Key tables:

- **users**: User accounts
- **documents**: Document metadata
- **document_chunks**: Text chunks
- **document_vectors**: Vector embeddings
- **qa_sessions**: Q&A history
- **qa_sources**: Answer sources

## Development

### Build

```bash
mvn clean install
```

### Test

```bash
mvn test
```

## Docker

```bash
# Build image
docker build -t ekp-biz-service .

# Run container
docker run -p 8080:8080 ekp-biz-service
```
