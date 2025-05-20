@echo off
REM Test execution script for Windows

REM Change to ai-ml directory
cd %~dp0\..\..

REM Run pytest with coverage
pytest tests/ --cov=src --cov-report=html -v

REM Open coverage report if tests pass
if %ERRORLEVEL% EQU 0 (
    echo Tests completed successfully!
    echo Opening coverage report...
    start htmlcov\index.html
) else (
    echo Tests failed with errors.
    exit /b 1
)