-- Update ingestion_log table
ALTER TABLE ingestion_log 
ADD COLUMN IF NOT EXISTS category VARCHAR(255),
ADD COLUMN IF NOT EXISTS file_path TEXT;

-- Create table for uploaded records
CREATE TABLE IF NOT EXISTS uploaded_records (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES ingestion_log(id),
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_uploaded_records_file_id ON uploaded_records(file_id);