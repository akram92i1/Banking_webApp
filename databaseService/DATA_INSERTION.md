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

1. **Get the `user_id` and the `username`**                       The query will return each of the `user_id` and `username` from the `users` table
   ```sql 
   SELECT user_id, username FROM users;
   ```

2. **Prepare account data**  
   Use the user and bank UUIDs in your `INSERT` statements. Example:
   ```sql
   INSERT INTO accounts (
    account_number, user_id, bank_id, account_type, account_status, balance, available_balance
   ) VALUES
   ('10000001', 'Returned_user_id', 'Returned_bank_id', 'CHECKING', 'ACTIVE', 52006.00, 5000.00),
   ('10000002', 'Returned_user_id', 'Returned_bank_id', 'SAVINGS', 'ACTIVE', 3050.12, 3000.00),

   -- Add more accounts as needed
   ;
   ```
   > Replace `Returned_user_id` and `Returned_bank_id` with actual UUIDs.

3. **Run the SQL**  
   Execute the account insertion script (e.g., `insert_acoounts` file).

---

## 5. Insert Additional Data (Optional)

- **Cards, Beneficiaries, Transactions, etc.:**  
  Repeat the process: get the necessary foreign keys, prepare `INSERT` statements, and execute them.

  - **Insert Cards Example:**
    ```sql
    INSERT INTO cards (
      card_id, account_id, card_number_hash, card_type, expiry_date, cvv_hash, card_status, daily_limit, monthly_limit, is_contactless, issued_at, created_at
    ) VALUES
    ('c1a1b2c3-d4e5-4711-aaaa-111111111111', '941a7d1c-94ab-42fd-be83-af8523f6dab2', 'hashed_cardnum_1', 'DEBIT', '2028-07-01', 'hashed_cvv_1', 'ACTIVE', 2000.00, 20000.00, TRUE, NOW(), NOW());
    ```

  - **Insert Transactions Example:**  
    > **Note:** Make sure you have created the correct partition for the `created_at` date before inserting.
    ```sql
    INSERT INTO transactions (
      transaction_id, from_account_id, to_account_id, transaction_type, amount, currency, description, reference_number, transaction_status, created_at, updated_at
    ) VALUES
    ('11111111-aaaa-aaaa-aaaa-111111111111', '941a7d1c-94ab-42fd-be83-af8523f6dab2', 'e433f7e4-bbf5-4d78-a622-cc1fd18b546e', 'TRANSFER', 500.00, 'USD', 'Transfer to savings', 'TXN1001', 'COMPLETED', '2025-07-03 10:00:00+00', '2025-07-03 10:00:00+00');
    ```

  - **Insert Beneficiaries Example:**
    ```sql
    INSERT INTO beneficiaries (
      beneficiary_id, user_id, nickname, account_number, routing_number, bank_name, beneficiary_name, relationship, is_verified, created_at
    ) VALUES
    ('b1b2c3d4-e5f6-4711-aaaa-111111111111', '593b2d80-49b0-47f3-ae24-1d434eaf09d5', 'My Savings', '10000002', '123456789', 'First National Bank', 'Alice Smith', 'FRIEND', TRUE, NOW());
    ```

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