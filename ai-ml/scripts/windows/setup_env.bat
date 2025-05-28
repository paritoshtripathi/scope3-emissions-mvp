@echo off
echo Setting up Python environment for RAG API...

:: Install required packages
python -m pip install -r requirements.txt

:: Install the package in development mode
python -m pip install -e .

:: Create necessary directories
if not exist models\faiss_index mkdir models\faiss_index
if not exist logs mkdir logs
if not exist uploads mkdir uploads

echo Environment setup complete.