-- Assure-toi que la base cible est celle définie par POSTGRES_DB (ex: my_finance_db)
-- et que les tables sont déjà créées dans les scripts précédents

-- Donner les privilèges sur les tables existantes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bank_database_admin;

-- Donner les privilèges sur les séquences (UUID, auto-incrément, etc.)
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bank_database_admin;

-- Grant All privileges on the database
GRANT ALL PRIVILEGES ON DATABASE my_finance_db TO bank_database_admin;
-- Donner les privilèges par défaut pour les futures tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bank_database_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bank_database_admin;
