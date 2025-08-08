-- Banking Application Database Schema
-- PostgreSQL Implementation
-- Use my_finance_db as the target database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE account_type AS ENUM ('CHECKING', 'SAVINGS', 'CREDIT', 'LOAN');
CREATE TYPE account_status AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'CLOSED');
CREATE TYPE transaction_type AS ENUM ('DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'PAYMENT', 'FEE');
CREATE TYPE transaction_status AS ENUM ('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED');
CREATE TYPE user_role AS ENUM ('CUSTOMER', 'EMPLOYEE', 'MANAGER', 'ADMIN');

-- Users table (customers and employees)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    ssn_hash VARCHAR(255), -- Hashed SSN for security
    address JSONB, -- Flexible address structure
    role user_role DEFAULT 'CUSTOMER',
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    failed_login_attempts INTEGER DEFAULT 0,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Banks table (for multi-bank support)
CREATE TABLE banks (
    bank_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bank_name VARCHAR(200) NOT NULL,
    routing_number VARCHAR(9) UNIQUE NOT NULL,
    swift_code VARCHAR(11),
    address JSONB,
    contact_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Accounts table
CREATE TABLE accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_number VARCHAR(20) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(user_id),
    bank_id UUID NOT NULL REFERENCES banks(bank_id),
    account_type account_type NOT NULL,
    account_status account_status DEFAULT 'ACTIVE',
    balance DECIMAL(15,2) DEFAULT 0.00,
    available_balance DECIMAL(15,2) DEFAULT 0.00,
    credit_limit DECIMAL(15,2) DEFAULT 0.00,
    interest_rate DECIMAL(5,4) DEFAULT 0.0000,
    overdraft_limit DECIMAL(10,2) DEFAULT 0.00,
    minimum_balance DECIMAL(10,2) DEFAULT 0.00,
    account_metadata JSONB, -- Additional account-specific data
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table (partitioned by date for performance)
CREATE TABLE transactions (
    transaction_id UUID  DEFAULT uuid_generate_v4(),
    from_account_id UUID REFERENCES accounts(account_id),
    to_account_id UUID REFERENCES accounts(account_id),
    transaction_type transaction_type NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    description TEXT,
    reference_number VARCHAR(50),
    UNIQUE (reference_number, created_at),
    transaction_status transaction_status DEFAULT 'PENDING',
    processed_at TIMESTAMP WITH TIME ZONE,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    fee_amount DECIMAL(10,2) DEFAULT 0.00,
    exchange_rate DECIMAL(10,6) DEFAULT 1.000000,
    merchant_info JSONB, -- For payment transactions
    location_info JSONB, -- GPS, IP address, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP UNIQUE ,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id,created_at),
    
    -- Ensure at least one account is specified
    CONSTRAINT check_account_specified CHECK (
        from_account_id IS NOT NULL OR to_account_id IS NOT NULL
    ),
    -- Ensure positive amounts
    CONSTRAINT check_positive_amount CHECK (amount > 0)
) PARTITION BY RANGE (created_at);

-- Create monthly partitions for transactions (example for 2025)
CREATE TABLE transactions_2025_07 PARTITION OF transactions
    FOR VALUES FROM ('2025-07-01') TO ('2025-08-01');
CREATE TABLE transactions_2025_08 PARTITION OF transactions
    FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
-- Continue creating partitions as needed...

-- Account holders (for joint accounts)
CREATE TABLE account_holders (
    account_id UUID REFERENCES accounts(account_id),
    user_id UUID REFERENCES users(user_id),
    relationship VARCHAR(50) DEFAULT 'PRIMARY', -- PRIMARY, JOINT, AUTHORIZED_USER
    permissions JSONB, -- What actions this holder can perform
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (account_id, user_id)
);

-- Cards table (debit/credit cards)
CREATE TABLE cards (
    card_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(account_id),
    card_number_hash VARCHAR(255) NOT NULL, -- Hashed card number
    card_type VARCHAR(20) NOT NULL, -- DEBIT, CREDIT
    expiry_date DATE NOT NULL,
    cvv_hash VARCHAR(255),
    card_status VARCHAR(20) DEFAULT 'ACTIVE',
    daily_limit DECIMAL(10,2) DEFAULT 1000.00,
    monthly_limit DECIMAL(12,2) DEFAULT 10000.00,
    is_contactless BOOLEAN DEFAULT TRUE,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    blocked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Beneficiaries (for transfers)
CREATE TABLE beneficiaries (
    beneficiary_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    nickname VARCHAR(100),
    account_number VARCHAR(20) NOT NULL,
    routing_number VARCHAR(9),
    bank_name VARCHAR(200),
    beneficiary_name VARCHAR(200) NOT NULL,
    relationship VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs
CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_number ON accounts(account_number);
CREATE INDEX idx_transactions_from_account ON transactions(from_account_id);
CREATE INDEX idx_transactions_to_account ON transactions(to_account_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_transactions_status ON transactions(transaction_status);
CREATE INDEX idx_cards_account_id ON cards(account_id);
CREATE INDEX idx_beneficiaries_user_id ON beneficiaries(user_id);

-- Row Level Security (RLS)
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE cards ENABLE ROW LEVEL SECURITY;

-- Create the role for RLS policies
CREATE ROLE authenticated_users;
-- RLS Policies (example for accounts)
CREATE POLICY account_isolation ON accounts
    FOR ALL TO authenticated_users
    USING (
        user_id = current_setting('app.current_user_id')::UUID OR
        EXISTS (
            SELECT 1 FROM account_holders ah 
            WHERE ah.account_id = accounts.account_id 
            AND ah.user_id = current_setting('app.current_user_id')::UUID
        )
    );

-- Trigger function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE VIEW account_summary AS
SELECT 
    a.account_id,
    a.account_number,
    a.account_type,
    a.balance,
    a.available_balance,
    u.first_name,
    u.last_name,
    u.email,
    b.bank_name
FROM accounts a
JOIN users u ON a.user_id = u.user_id
JOIN banks b ON a.bank_id = b.bank_id
WHERE a.account_status = 'ACTIVE';

CREATE VIEW recent_transactions AS
SELECT 
    t.transaction_id,
    t.transaction_type,
    t.amount,
    t.description,
    t.transaction_status,
    t.created_at,
    fa.account_number AS from_account,
    ta.account_number AS to_account
FROM transactions t
LEFT JOIN accounts fa ON t.from_account_id = fa.account_id
LEFT JOIN accounts ta ON t.to_account_id = ta.account_id
WHERE t.created_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY t.created_at DESC; 