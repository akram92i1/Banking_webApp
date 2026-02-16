-- =====================================================
-- Read-Only User for AI Banking Agent
-- Executed as: postgres superuser
-- Purpose: Create a restricted user that can ONLY read data
-- =====================================================

\c my_finance_db;

-- Create read-only user if it doesn't exist
DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_roles WHERE rolname = 'ai_agent_readonly'
    ) THEN
        CREATE ROLE ai_agent_readonly LOGIN PASSWORD 'readonly_agent_secure_2024';
        RAISE NOTICE 'Role ai_agent_readonly created.';
    ELSE
        RAISE NOTICE 'Role ai_agent_readonly already exists.';
    END IF;
END
$$;

SET search_path TO public;

-- Allow connection to the database
GRANT CONNECT ON DATABASE my_finance_db TO ai_agent_readonly;

-- Allow usage of the public schema (but NOT create)
GRANT USAGE ON SCHEMA public TO ai_agent_readonly;

-- Grant SELECT only on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_agent_readonly;

-- Grant SELECT on any future tables created in public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO ai_agent_readonly;

-- Explicitly revoke any write permissions (safety net)
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA public FROM ai_agent_readonly;

\echo 'Read-only AI agent user created successfully.'
