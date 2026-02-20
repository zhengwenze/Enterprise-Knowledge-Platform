-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create initial tables will be handled by Flyway migrations in biz-service
-- and SQLAlchemy models in ai-service
