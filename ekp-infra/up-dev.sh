#!/bin/bash

echo "Starting EKP Development Environment..."

cd "$(dirname "$0")"

echo "Creating init-db directory if not exists..."
mkdir -p init-db

echo "Starting all services with Docker Compose..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "Checking service status..."
docker-compose ps

echo ""
echo "=========================================="
echo "EKP Development Environment is starting!"
echo "=========================================="
echo ""
echo "Services:"
echo "  - PostgreSQL (pgvector): localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Kafka: localhost:9092"
echo "  - AI Service: http://localhost:8000"
echo "  - Business Service: http://localhost:8080"
echo ""
echo "API Documentation:"
echo "  - AI Service Swagger: http://localhost:8000/docs"
echo "  - Business Service Swagger: http://localhost:8080/swagger-ui.html"
echo ""
echo "To view logs: docker-compose logs -f [service_name]"
echo "To stop: ./down-dev.sh"
