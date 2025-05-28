#!/bin/bash

echo "Starting Scope3 RAG API initialization..."

# Setup logging
LOG_FILE="/app/logs/rag_api.log"
mkdir -p /app/logs

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if KB already exists
if [ -f "/app/kb_store.db" ] && [ -d "/app/models/faiss_index" ] && [ "$(ls -A /app/models/faiss_index)" ]; then
    log "Existing knowledge base found, skipping initialization..."
else
    log "No existing knowledge base found, starting initialization..."
    
    # Check if KB files exist
    if [ ! -d "/app/kb" ]; then
        log "ERROR: KB directory not found"
        exit 1
    fi

    # Check for required PDF files
    required_files=(
        "/app/kb/combined_scope3_knowledge.txt"
        "/app/kb/Category 1-Purchased Goods and Services.pdf"
        "/app/kb/Category 2-Capital Goods.pdf"
        "/app/kb/Category 3-Fuel- and Energy-Related Activities.pdf"
        "/app/kb/Category 4-Upstream Transportation  and Distribution.pdf"
        "/app/kb/Imp-1-Scope3_Calculation_Guidance.pdf"
        "/app/kb/Intro_GHGP_Tech.pdf"
        "/app/kb/SBT_Value_Chain_Report-1.pdf"
        "/app/kb/Scope-3-Proposals-Summary-Draft.pdf"
    )

    missing_files=0
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log "ERROR: Missing required file: $file"
            missing_files=1
        fi
    done

    if [ $missing_files -eq 1 ]; then
        log "ERROR: Some required knowledge base files are missing"
        exit 1
    fi

    # Initialize knowledge base
    log "Initializing knowledge base..."
    python -m src.rag.kb.init_kb 2>&1 | tee -a "$LOG_FILE"

    # Check initialization status
    if [ $? -ne 0 ]; then
        log "ERROR: Knowledge base initialization failed"
        exit 1
    fi
    
    log "Knowledge base initialization successful"
fi

# Start the API with proper logging
log "Starting RAG API..."
export PYTHONUNBUFFERED=1
python -m flask run --host=0.0.0.0 --port=5000 2>&1 | tee -a "$LOG_FILE"