-- Runs once on first postgres container creation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
SET timezone = 'UTC';
