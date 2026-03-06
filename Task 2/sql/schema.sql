-- Create custom types
CREATE TYPE channel_type AS ENUM ('phone', 'chat', 'email', 'sms');
CREATE TYPE outcome_type AS ENUM ('resolved', 'escalated', 'failed');

-- Create main table
CREATE TABLE call_records (
    id BIGSERIAL PRIMARY KEY,
    customer_phone VARCHAR(20) NOT NULL,
    channel channel_type NOT NULL,
    transcript TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    outcome outcome_type NOT NULL,
    confidence_score NUMERIC(3, 2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    csat_score SMALLINT CHECK (csat_score >= 1 AND csat_score <= 5),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration INTEGER NOT NULL,
    intent_type VARCHAR(50) NOT NULL
);

-- Index for querying recent calls by phone number (supports get_recent function)
CREATE INDEX idx_call_records_phone_timestamp 
ON call_records (customer_phone, timestamp DESC);

-- Index for analytics queries filtering by timestamp (supports time-range queries)
CREATE INDEX idx_call_records_timestamp 
ON call_records (timestamp DESC);

-- Index for analytics on intent types and outcomes (supports resolution rate calculations)
CREATE INDEX idx_call_records_intent_outcome 
ON call_records (intent_type, outcome, timestamp);
