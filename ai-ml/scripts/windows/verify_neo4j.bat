@echo off
echo Verifying Neo4j setup...

REM Check Neo4j container status
echo Checking Neo4j container...
docker ps --filter "name=neo4j" --format "{{.Status}}" | findstr "Up" > nul
if %errorlevel% equ 0 (
    echo Neo4j container is running
) else (
    echo Neo4j container is not running
    exit /b 1
)

REM Check Neo4j ports
echo Checking Neo4j ports...
netstat -an | findstr "7474" > nul
if %errorlevel% equ 0 (
    echo Port 7474 (HTTP) is open
) else (
    echo Port 7474 (HTTP) is not accessible
)

netstat -an | findstr "7687" > nul
if %errorlevel% equ 0 (
    echo Port 7687 (Bolt) is open
) else (
    echo Port 7687 (Bolt) is not accessible
)

REM Check Neo4j browser access
echo Checking Neo4j browser access...
curl -s http://localhost:7474 > nul
if %errorlevel% equ 0 (
    echo Neo4j browser is accessible
) else (
    echo Neo4j browser is not accessible
)

echo.
echo Neo4j Connection Details:
echo Browser URL: http://localhost:7474
echo Bolt URL: bolt://localhost:7687
echo Username: neo4j
echo Password: scope3password

echo.
echo Container Logs:
docker logs neo4j --tail 10