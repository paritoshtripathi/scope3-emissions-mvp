@echo off
REM Script to fix common setup issues

REM Change to ai-ml directory
cd %~dp0\..\..

echo Attempting to fix common setup issues...

REM Create .env if missing
if not exist ".env" (
    echo Creating .env from template...
    copy ".env.example" ".env"
)

REM Install/upgrade pip
python -m pip install --upgrade pip

REM Install package in development mode
echo Installing package...
pip install -e .

REM Create required directories
echo Creating required directories...
mkdir src\rag\agents 2>nul
mkdir src\rag\embeddings 2>nul
mkdir src\rag\indexing 2>nul
mkdir src\rag\models 2>nul
mkdir src\rag\processors 2>nul
mkdir src\rag\retrieval 2>nul
mkdir src\rag\api 2>nul
mkdir src\config 2>nul
mkdir src\monitoring 2>nul
mkdir tests\unit 2>nul
mkdir tests\integration 2>nul
mkdir models\faiss_index 2>nul

REM Download models
echo Downloading required models...
python -c "from sentence_transformers import SentenceTransformer; models = ['sentence-transformers/all-mpnet-base-v2', 'sentence-transformers/all-MiniLM-L6-v2', 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2', 'BAAI/bge-large-en-v1.5']; [SentenceTransformer(m) for m in models]"

REM Run validation
echo Running validation...
call scripts\windows\validate.bat

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Common issues have been fixed!
) else (
    echo.
    echo ❌ Some issues could not be fixed automatically.
    echo Please check the validation errors above.
    exit /b 1
)