@echo off
echo Starting Scope3 RAG API initialization...

:: Setup logging
set LOG_DIR=logs
set LOG_FILE=%LOG_DIR%\rag_api.log
if not exist %LOG_DIR% mkdir %LOG_DIR%

:: Function to log with timestamp
call :log "Cleaning up existing knowledge base..."

:: Clean up existing KB files
if exist kb_store.db del /F kb_store.db
if exist models\faiss_index\* del /F /Q models\faiss_index\*

:: Initialize knowledge base
call :log "Initializing knowledge base..."
python -m src.rag.kb.init_kb
if errorlevel 1 (
    call :log "ERROR: Knowledge base initialization failed"
    exit /b 1
)

call :log "Knowledge base initialization successful"

:: Start the API
call :log "Starting RAG API..."
set PYTHONUNBUFFERED=1
set FLASK_APP=src.rag.api.app
set FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000

goto :eof

:log
echo [%date% %time%] %~1 >> %LOG_FILE%
echo [%date% %time%] %~1
goto :eof