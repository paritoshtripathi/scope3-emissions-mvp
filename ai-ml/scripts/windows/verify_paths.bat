@echo off
REM Path verification script for Windows environment

echo Running path verification...

REM Change to ai-ml directory
cd %~dp0\..\..

REM Run verification
python scripts\windows\verify_paths.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Path verification completed successfully!
) else (
    echo.
    echo Path verification failed. Please fix the issues above.
    exit /b 1
)