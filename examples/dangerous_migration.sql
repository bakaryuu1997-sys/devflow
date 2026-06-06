ALTER TABLE users DROP COLUMN phone;
DELETE FROM sessions;
TRUNCATE TABLE audit_logs;
