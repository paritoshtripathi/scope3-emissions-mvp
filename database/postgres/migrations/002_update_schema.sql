-- Add missing columns to existing table
ALTER TABLE ingestion_log
ADD COLUMN IF NOT EXISTS category TEXT,
ADD COLUMN IF NOT EXISTS file_path TEXT;

-- Create uploaded_records table if not exists
CREATE TABLE IF NOT EXISTS uploaded_records (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES ingestion_log(id),
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
