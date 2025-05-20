-- Add RAG support to existing tables
ALTER TABLE ingestion_log
ADD COLUMN rag_processed BOOLEAN DEFAULT FALSE,
ADD COLUMN rag_processing_details JSONB;

-- Create index for RAG processed files
CREATE INDEX idx_rag_processed ON ingestion_log(rag_processed);

-- Add comment for documentation
COMMENT ON COLUMN ingestion_log.rag_processed IS 'Indicates if the file has been processed by RAG system';
COMMENT ON COLUMN ingestion_log.rag_processing_details IS 'JSON containing RAG processing metadata and results';