-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE rag_vectors TO rag_user;

-- Create schema for vector storage if needed
CREATE SCHEMA IF NOT EXISTS vectors;
GRANT ALL ON SCHEMA vectors TO rag_user;
