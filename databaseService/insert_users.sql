INSERT INTO users (username, email, password_hash, first_name, last_name, phone, date_of_birth, ssn_hash, address, role, is_active, email_verified)
VALUES
('jdoe', 'jdoe@example.com', 'hashed_pw1', 'John', 'Doe', '+1234567890', '1990-01-01', 'ssn_hash1', '{"street":"123 Main St","city":"New York","zip":"10001"}', 'CUSTOMER', TRUE, TRUE),
('asmith', 'asmith@example.com', 'hashed_pw2', 'Alice', 'Smith', '+1234567891', '1985-05-12', 'ssn_hash2', '{"street":"456 Oak Ave","city":"Los Angeles","zip":"90001"}', 'CUSTOMER', TRUE, TRUE),
-- Add more users as needed
;