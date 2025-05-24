
# 📊 Banking Application Database Schema - Attributes List

## 🧑‍💼 `users`
| Attribute            | Type               | Description                            |
|---------------------|--------------------|----------------------------------------|
| user_id             | UUID               | Primary Key                            |
| username            | VARCHAR(50)        | Unique username                        |
| email               | VARCHAR(100)       | Unique email                           |
| password_hash       | VARCHAR(255)       | Hashed password                        |
| first_name          | VARCHAR(100)       | User's first name                      |
| last_name           | VARCHAR(100)       | User's last name                       |
| phone               | VARCHAR(20)        | Phone number                           |
| date_of_birth       | DATE               | Date of birth                          |
| ssn_hash            | VARCHAR(255)       | Hashed SSN                             |
| address             | JSONB              | Address in JSON format                 |
| role                | user_role (ENUM)   | Role: CUSTOMER, EMPLOYEE, etc.         |
| is_active           | BOOLEAN            | Account active flag                    |
| email_verified      | BOOLEAN            | Email verification status              |
| failed_login_attempts | INTEGER          | Number of failed logins                |
| last_login_at       | TIMESTAMP TZ       | Last login timestamp                   |
| created_at          | TIMESTAMP TZ       | Creation timestamp                     |
| updated_at          | TIMESTAMP TZ       | Last updated timestamp                 |

## 🏦 `banks`
| Attribute         | Type        | Description                      |
|------------------|-------------|----------------------------------|
| bank_id          | UUID        | Primary Key                      |
| bank_name        | VARCHAR(200)| Name of the bank                 |
| routing_number   | VARCHAR(9)  | Bank routing number              |
| swift_code       | VARCHAR(11) | SWIFT/BIC code                   |
| address          | JSONB       | Bank address                     |
| contact_info     | JSONB       | Contact information              |
| created_at       | TIMESTAMP TZ| Creation timestamp               |

## 💰 `accounts`
| Attribute          | Type                | Description                          |
|-------------------|---------------------|--------------------------------------|
| account_id        | UUID                | Primary Key                          |
| account_number    | VARCHAR(20)         | Unique account number                |
| user_id           | UUID                | FK to `users`                        |
| bank_id           | UUID                | FK to `banks`                        |
| account_type      | account_type (ENUM) | CHECKING, SAVINGS, etc.              |
| account_status    | account_status      | ACTIVE, CLOSED, etc.                 |
| balance           | DECIMAL(15,2)       | Current balance                      |
| available_balance | DECIMAL(15,2)       | Available for withdrawal             |
| credit_limit      | DECIMAL(15,2)       | Credit limit                         |
| interest_rate     | DECIMAL(5,4)        | Interest rate                        |
| overdraft_limit   | DECIMAL(10,2)       | Overdraft limit                      |
| minimum_balance   | DECIMAL(10,2)       | Minimum balance                      |
| account_metadata  | JSONB               | Additional metadata                  |
| opened_at         | TIMESTAMP TZ        | Account opened date                  |
| closed_at         | TIMESTAMP TZ        | Closed date                          |
| created_at        | TIMESTAMP TZ        | Creation timestamp                   |
| updated_at        | TIMESTAMP TZ        | Last update                          |

## 🔄 `transactions`
| Attribute          | Type                    | Description                       |
| ------------------ | ----------------------- | --------------------------------- |
| transaction_id     | UUID                    | Primary Key                       |
| from_account_id    | UUID                    | FK to `accounts` (optional)       |
| to_account_id      | UUID                    | FK to `accounts` (optional)       |
| transaction_type   | transaction_type (ENUM) | DEPOSIT, TRANSFER, etc.           |
| amount             | DECIMAL(15,2)           | Transaction amount                |
| currency           | VARCHAR(3)              | Currency (default: USD)           |
| description        | TEXT                    | Description                       |
| reference_number   | VARCHAR(50)             | Unique transaction reference      |
| transaction_status | transaction_status      | Status (PENDING, COMPLETED, etc.) |
| processed_at       | TIMESTAMP TZ            | Time processed                    |
| scheduled_at       | TIMESTAMP TZ            | Time scheduled                    |
| fee_amount         | DECIMAL(10,2)           | Fee amount                        |
| exchange_rate      | DECIMAL(10,6)           | Exchange rate                     |
| merchant_info      | JSONB                   | Merchant details                  |
| location_info      | JSONB                   | Location (GPS, IP, etc.)          |
| created_at         | TIMESTAMP TZ            | Creation time                     |
| updated_at         | TIMESTAMP TZ            | Last update                       |

## 👥 `account_holders`
| Attribute    | Type     | Description                     |
|-------------|----------|---------------------------------|
| account_id  | UUID     | FK to `accounts`                |
| user_id     | UUID     | FK to `users`                   |
| relationship| VARCHAR(50) | PRIMARY, JOINT, etc.         |
| permissions | JSONB    | Actions permitted               |
| added_at    | TIMESTAMP TZ | Timestamp                    |

## 💳 `cards`
| Attribute         | Type             | Description                         |
|------------------|------------------|-------------------------------------|
| card_id          | UUID             | Primary Key                         |
| account_id       | UUID             | FK to `accounts`                    |
| card_number_hash | VARCHAR(255)     | Hashed card number                  |
| card_type        | VARCHAR(20)      | DEBIT or CREDIT                     |
| expiry_date      | DATE             | Expiration date                     |
| cvv_hash         | VARCHAR(255)     | Hashed CVV                          |
| card_status      | VARCHAR(20)      | Status (e.g., ACTIVE)               |
| daily_limit      | DECIMAL(10,2)    | Daily limit                         |
| monthly_limit    | DECIMAL(12,2)    | Monthly limit                       |
| is_contactless   | BOOLEAN          | Contactless enabled?                |
| issued_at        | TIMESTAMP TZ     | Issue date                          |
| blocked_at       | TIMESTAMP TZ     | Blocked date                        |
| created_at       | TIMESTAMP TZ     | Creation time                       |

## 🧾 `beneficiaries`
| Attribute        | Type         | Description                     |
|-----------------|--------------|---------------------------------|
| beneficiary_id  | UUID         | Primary Key                     |
| user_id         | UUID         | FK to `users`                   |
| nickname        | VARCHAR(100) | Beneficiary nickname            |
| account_number  | VARCHAR(20)  | Account number of beneficiary   |
| routing_number  | VARCHAR(9)   | Routing number                  |
| bank_name       | VARCHAR(200) | Bank name                       |
| beneficiary_name| VARCHAR(200) | Full name of beneficiary        |
| relationship    | VARCHAR(100) | Relationship type               |
| is_verified     | BOOLEAN      | Is verified?                    |
| created_at      | TIMESTAMP TZ | Timestamp                       |

## 📜 `audit_logs`
| Attribute      | Type         | Description                    |
|---------------|--------------|--------------------------------|
| audit_id      | UUID         | Primary Key                    |
| user_id       | UUID         | FK to `users`                  |
| action        | VARCHAR(100) | Performed action               |
| table_name    | VARCHAR(50)  | Table affected                 |
| record_id     | UUID         | Affected record ID             |
| old_values    | JSONB        | Previous values (if any)       |
| new_values    | JSONB        | New values                     |
| ip_address    | INET         | IP of request                  |
| user_agent    | TEXT         | Browser/device info            |
| created_at    | TIMESTAMP TZ | Time of action                 |
