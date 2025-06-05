# 🗃️ Data Insertion Guide for Banking Platform

This guide explains how to insert initial data into your PostgreSQL database for the banking platform project.

---

## 1. Prerequisites

- PostgreSQL server is running.
- Database and tables are created using your `Banking_databse.sql` schema.
- The `uuid-ossp` extension is enabled for UUID generation:
  ```sql
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  ```

---

## 2. Insert User Records

1. **Prepare user data**  
   Create SQL `INSERT` statements for at least 6 users. Example:
   ```sql
   INSERT INTO users (username, email, password_hash, first_name, last_name, phone, date_of_birth, ssn_hash, address, role, is_active, email_verified)
   VALUES
   ('jdoe', 'jdoe@example.com', 'hashed_pw1', 'John', 'Doe', '+1234567890', '1990-01-01', 'ssn_hash1', '{"street":"123 Main St","city":"New York","zip":"10001"}', 'CUSTOMER', TRUE, TRUE),
   ('asmith', 'asmith@example.com', 'hashed_pw2', 'Alice', 'Smith', '+1234567891', '1985-05-12', 'ssn_hash2', '{"street":"456 Oak Ave","city":"Los Angeles","zip":"90001"}', 'CUSTOMER', TRUE, TRUE),
   -- Add more users as needed
   ;
   ```
   > **Tip:** Replace `hashed_pwX` and `ssn_hashX` with actual hashed values.

2. **Run the SQL**  
   Execute the above statements in your PostgreSQL client or admin tool.

---

## 3. Insert Bank Records

1. **Prepare bank data**  
   Insert at least one bank to reference in accounts:
   ```sql
   INSERT INTO banks (bank_name, routing_number, swift_code, address, contact_info)
   VALUES
   ('First National Bank', '123456789', 'FNBNUS33', '{"street":"1 Bank St","city":"Finance City"}', '{"phone":"+1234567890"}');
   ```

2. **Get the `bank_id`**  
   ```sql
   SELECT bank_id FROM banks LIMIT 1;
   ```

---

## 4. Insert Account Records

1. **Get user IDs**  
   ```sql
   SELECT user_id, username FROM users;
   ```
   Copy the UUIDs for each user.

2. **Prepare account data**  
   Use the user and bank UUIDs in your `INSERT` statements. Example:
   ```sql
   INSERT INTO accounts (
     account_number, user_id, bank_id, account_type, account_status, balance, available_balance
   ) VALUES
   ('10000001', 'user-uuid-1', 'bank-uuid', 'CHECKING', 'ACTIVE', 5000.00, 5000.00),
   ('10000002', 'user-uuid-2', 'bank-uuid', 'SAVINGS', 'ACTIVE', 3000.00, 3000.00),
   -- Add more accounts as needed
   ;
   ```
   > Replace `user-uuid-X` and `bank-uuid` with actual UUIDs.

3. **Run the SQL**  
   Execute the account insertion script (e.g., `insert_acoounts` file).

---

## 5. Insert Additional Data (Optional)

- **Cards, Beneficiaries, Transactions, etc.:**  
  Repeat the process: get the necessary foreign keys, prepare `INSERT` statements, and execute them.

---

## 6. Verify Data

- Check your data with:
  ```sql
  SELECT * FROM users;
  SELECT * FROM banks;
  SELECT * FROM accounts;
  ```

---

## 7. Automation (Optional)

- Place your data insertion scripts in the `databaseService/` folder.
- Use a tool like `psql` to run all scripts in order:
  ```bash
  psql -U your_user -d your_db -f Banking_databse.sql
  psql -U your_user -d your_db -f insert_users.sql
  psql -U your_user -d your_db -f insert_banks.sql
  psql -U your_user -d your_db -f insert_acoounts
  ```

---

**Now your database is seeded with initial data for development and testing!**