-- =====================================================
-- Authorization Script for Banking Database (Docker-safe)
-- Executed as: postgres superuser
-- Purpose: Grant full privileges to "bank_database_admin"
-- =====================================================

-- Ensure we are connected to the correct database
\c my_finance_db;

-- Create user if it doesn't exist
DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_roles WHERE rolname = 'bank_database_admin'
    ) THEN
        CREATE ROLE bank_database_admin LOGIN PASSWORD 'admin123';
        RAISE NOTICE 'Role bank_database_admin created.';
    ELSE
        RAISE NOTICE 'Role bank_database_admin already exists.';
    END IF;
END
$$;

-- Set the schema context
SET search_path TO public;

-- Grant full privileges on the database
GRANT ALL PRIVILEGES ON DATABASE my_finance_db TO bank_database_admin;

-- Grant privileges on all existing tables, sequences, and functions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bank_database_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bank_database_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO bank_database_admin;

-- Allow the user to create, alter, and drop tables
GRANT CREATE, CONNECT, TEMPORARY ON DATABASE my_finance_db TO bank_database_admin;
GRANT USAGE, CREATE ON SCHEMA public TO bank_database_admin;

-- Change ownership of all existing tables to the user (optional)
DO
$$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE format('ALTER TABLE public.%I OWNER TO bank_database_admin;', r.tablename);
    END LOOP;
END
$$;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON TABLES TO bank_database_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON SEQUENCES TO bank_database_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON FUNCTIONS TO bank_database_admin;

-- Confirmation output
\echo '✅ Privileges successfully granted to bank_database_admin.'
