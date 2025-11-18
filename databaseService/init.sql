CREATE USER bank_database_admin WITH ENCRYPTED PASSWORD 'admin123';
GRANT ALL PRIVILEGES ON DATABASE my_finance_db TO bank_database_admin;
