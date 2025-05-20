@echo off
echo Starting development environment...

REM Check Docker is running
echo Checking Docker...
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not running! Please start Docker Desktop first.
    exit /b 1
)

REM Setup Neo4j
echo Setting up Neo4j...
call %~dp0setup_neo4j.bat

REM Verify Neo4j
echo Verifying Neo4j setup...
call %~dp0verify_neo4j.bat
if %errorlevel% neq 0 (
    echo Neo4j verification failed! Please check the errors above.
    exit /b 1
)

REM Set environment variables
echo Setting up environment...
set NEO4J_URI=bolt://localhost:7687
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=scope3password

echo.
echo Development environment is ready!
echo.
echo You can now run the application with:
echo python ai-ml/run.py
echo.
echo Available endpoints:
echo - Neo4j Browser: http://localhost:7474
echo - API Docs: http://localhost:5000/api/v1/docs
echo.
echo Press any key to start the application...
pause > nul

python ai-ml/run.py