@echo off
echo Setting up Neo4j database...

REM Check if Neo4j is running
echo Checking Neo4j status...
docker ps | findstr "neo4j" > nul
if %errorlevel% equ 0 (
    echo Neo4j is already running
) else (
    echo Starting Neo4j container...
    docker-compose up -d neo4j
    echo Waiting for Neo4j to be ready...
    timeout /t 15
)

REM Verify Neo4j connection
echo Verifying Neo4j connection...
curl -v telnet://localhost:7687 2>&1 | findstr "Connected"
if %errorlevel% equ 0 (
    echo Neo4j is accessible at bolt://localhost:7687
) else (
    echo Neo4j connection failed. Please check:
    echo 1. Docker is running
    echo 2. Neo4j container is healthy: docker ps
    echo 3. Ports 7474 ^(HTTP^) and 7687 ^(Bolt^) are not in use
)

REM Display Neo4j status
echo.
echo Neo4j Container Status:
docker ps --filter "name=neo4j"

echo.
echo Neo4j Browser: http://localhost:7474
echo Default credentials: neo4j/scope3password
echo Bolt URL: bolt://localhost:7687