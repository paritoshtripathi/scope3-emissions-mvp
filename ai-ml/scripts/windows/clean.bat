@echo off
REM Cleanup script for Windows

REM Remove Python cache files
del /s /q *.pyc
del /s /q *.pyo
del /s /q *.pyd
rd /s /q __pycache__
rd /s /q .pytest_cache
rd /s /q htmlcov
del /q .coverage

REM Remove build artifacts
rd /s /q build
rd /s /q dist
rd /s /q *.egg-info

echo Cleanup completed successfully!