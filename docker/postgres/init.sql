-- PostgreSQL initialization script
-- Runs automatically on first container startup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE support_db TO support_user;
GRANT ALL ON SCHEMA public TO support_user;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
END $$;