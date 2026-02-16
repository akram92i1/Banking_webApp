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

-- Add Row-Level Security (RLS) policies for tables that have RLS enabled.
-- Without these policies, RLS blocks all rows for non-owner users by default.
DO
$$
DECLARE
    tbl RECORD;
BEGIN
    FOR tbl IN (
        SELECT c.relname AS table_name
        FROM pg_class c
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE c.relrowsecurity = true
          AND c.relkind = 'r'
          AND n.nspname = 'public'
    ) LOOP
        -- Drop existing policy if it exists, then create
        EXECUTE format('DROP POLICY IF EXISTS ai_readonly_select ON %I', tbl.table_name);
        EXECUTE format('CREATE POLICY ai_readonly_select ON %I FOR SELECT TO ai_agent_readonly USING (true)', tbl.table_name);
        RAISE NOTICE 'Created RLS SELECT policy on %', tbl.table_name;
    END LOOP;
END
$$;

\echo 'Read-only AI agent user created successfully.'
