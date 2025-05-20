@echo off
REM Cleanup script for ai-ml layer

REM Change to ai-ml directory
cd %~dp0\..\..

echo Cleaning up ai-ml layer...

REM Remove old directories
rd /s /q rag 2>nul
rd /s /q agents 2>nul
rd /s /q examples 2>nul
rd /s /q postman 2>nul
rd /s /q output 2>nul

REM Remove old Python files
del /s /q *.pyc 2>nul
rd /s /q __pycache__ 2>nul

REM Remove test cache
rd /s /q .pytest_cache 2>nul
del /s /q .coverage 2>nul
rd /s /q htmlcov 2>nul

REM Create required directories
mkdir src\rag\embeddings 2>nul
mkdir src\rag\processors 2>nul
mkdir src\rag\indexing 2>nul
mkdir src\rag\models 2>nul
mkdir src\rag\retrieval 2>nul
mkdir src\rag\api 2>nul
mkdir src\config 2>nul
mkdir src\monitoring 2>nul
mkdir tests\unit 2>nul
mkdir tests\integration 2>nul
mkdir models\faiss_index 2>nul

REM Run validation
call scripts\windows\validate.bat

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Cleanup completed successfully!
) else (
    echo.
    echo ❌ Some issues remain. Please check validation output.
    exit /b 1
)