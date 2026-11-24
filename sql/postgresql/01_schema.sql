CREATE SCHEMA IF NOT EXISTS integration;
CREATE TABLE IF NOT EXISTS integration.events (event_id VARCHAR(64) PRIMARY KEY, event_type VARCHAR(80) NOT NULL, event_timestamp TIMESTAMPTZ NOT NULL, customer_id VARCHAR(64) NOT NULL, amount NUMERIC(14,2) NOT NULL CHECK (amount >= 0), source VARCHAR(80) NOT NULL, ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW());
CREATE INDEX IF NOT EXISTS ix_events_timestamp ON integration.events(event_timestamp);
CREATE INDEX IF NOT EXISTS ix_events_customer_timestamp ON integration.events(customer_id, event_timestamp DESC);
