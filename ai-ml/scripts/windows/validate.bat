@echo off
REM Validation script for Windows environment

echo Running RAG system validation...

REM Change to ai-ml directory
cd %~dp0\..\..

REM Run validation
python scripts\windows\validate.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Validation completed successfully!
) else (
    echo.
    echo Validation failed. Please fix the issues above.
    echo Run 'scripts\windows\fix_common_issues.bat' to attempt automatic fixes.
    exit /b 1
)