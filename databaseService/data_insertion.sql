-- Step 1: Insert users and bank, return their IDs
WITH user1 AS (
  INSERT INTO users (
    username, email, password_hash, first_name, last_name,
    phone, date_of_birth, ssn_hash, address, role, is_active, email_verified
  )
  VALUES (
    'jdoe', 'jdoe@example.com', 'hashed_pw1', 'John', 'Doe',
    '+1234567890', '1990-01-01', 'ssn_hash1',
    '{"street":"123 Main St","city":"New York","zip":"10001"}',
    'CUSTOMER', TRUE, TRUE
  )
  RETURNING user_id
),
user2 AS (
  INSERT INTO users (
    username, email, password_hash, first_name, last_name,
    phone, date_of_birth, ssn_hash, address, role, is_active, email_verified
  )
  VALUES (
    'asmith', 'asmith@example.com', 'hashed_pw2', 'Alice', 'Smith',
    '+1234567891', '1985-05-12', 'ssn_hash2',
    '{"street":"456 Oak Ave","city":"Los Angeles","zip":"90001"}',
    'CUSTOMER', TRUE, TRUE
  )
  RETURNING user_id
),
bank1 AS (
  INSERT INTO banks (
    bank_name, routing_number, swift_code, address, contact_info
  )
  VALUES (
    'First National Bank', '123456789', 'FNBNUS33',
    '{"street":"1 Bank St","city":"Finance City"}',
    '{"phone":"+1234567890"}'
  )
  RETURNING bank_id
)

-- Step 2: Insert accounts for users
INSERT INTO accounts (
  account_number, user_id, bank_id, account_type,
  account_status, balance, available_balance
)
VALUES
(
  '10000001', (SELECT user_id FROM user1), (SELECT bank_id FROM bank1),
  'CHECKING', 'ACTIVE', 52006.00, 5000.00
),
(
  '10000002', (SELECT user_id FROM user2), (SELECT bank_id FROM bank1),
  'SAVINGS', 'ACTIVE', 3050.12, 3000.00
);

WITH acc1 AS (
  SELECT account_id FROM accounts WHERE account_number = '10000001'
),
acc2 AS (
  SELECT account_id FROM accounts WHERE account_number = '10000002'
)
INSERT INTO cards (
  account_id, card_number_hash, card_type,
  expiry_date, cvv_hash, card_status, 
  daily_limit, monthly_limit, is_contactless,
  issued_at, created_at
)
VALUES
(
  (SELECT account_id FROM acc1), 'hashed_card_1', 'VISA',
  '2025-12-31', 'hashed_cvv_1', 'ACTIVE',
  5000.00, 15000.00, TRUE,
  NOW(), NOW()
),
(
 (SELECT account_id FROM acc2), 'hashed_card_2', 'VISA',
  '2025-12-31', 'hashed_cvv_2', 'ACTIVE',
  7000.00, 21000.00, TRUE,
  NOW(), NOW()
);

-- Step 4: Insert transactions for accounts
WITH account1 AS (
  SELECT account_id FROM accounts WHERE account_number = '10000001'
),
account2 AS (
  SELECT account_id FROM accounts WHERE account_number = '10000002'
)
INSERT INTO transactions (
 from_account_id, to_account_id, transaction_type, amount, currency, description, reference_number, transaction_status, created_at, updated_at
)
VALUES
( (SELECT account_id FROM account1), (SELECT account_id FROM account2), 'DEPOSIT',     500.00, 'USD' ,'Transfer to savings', 'TXN1001', 'COMPLETED', '2025-07-03 10:00:00+00', '2025-07-03 10:00:00+00'),
((SELECT account_id FROM account1), (SELECT account_id FROM account2),'WITHDRAWAL',  200.00,  'USD','Transfer to savings', 'TXN1001', 'COMPLETED', '2025-07-02 10:00:00+00', '2025-07-03 10:00:00+00'),
((SELECT account_id FROM account2), (SELECT account_id FROM account1) ,'TRANSFER',    500.00, 'USD' ,'Transfer to savings', 'TXN1001', 'COMPLETED', '2025-07-01 10:00:00+00', '2025-07-03 10:00:00+00');
