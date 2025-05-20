@echo off
REM Setup script for Windows environment

echo Setting up development environment...

REM Create necessary directories
if not exist "models\faiss_index" mkdir models\faiss_index
if not exist "src\rag\agents" mkdir src\rag\agents
if not exist "src\rag\embeddings" mkdir src\rag\embeddings
if not exist "src\rag\indexing" mkdir src\rag\indexing
if not exist "src\rag\processors" mkdir src\rag\processors
if not exist "src\rag\api" mkdir src\rag\api
if not exist "src\config" mkdir src\config
if not exist "src\monitoring" mkdir src\monitoring
if not exist "tests\unit" mkdir tests\unit
if not exist "tests\integration" mkdir tests\integration

REM Install dependencies
python -m pip install --upgrade pip
pip install -e .

REM Copy environment file if not exists
if not exist ".env" copy ".env.example" ".env"

REM Run validation
call scripts\windows\validate.bat

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Setup completed successfully!
    echo Run 'docker-compose up --build' to start the services
) else (
    echo.
    echo Setup failed. Please fix the validation errors and try again.
    exit /b 1
)