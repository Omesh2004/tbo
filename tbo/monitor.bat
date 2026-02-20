@echo off
REM Travel Data Pipeline - Service Monitor for Windows

echo.
echo ======================================
echo Travel Data Pipeline - Service Monitor
echo ======================================
echo.

REM Check if services are running
docker-compose ps | find "Up" > nul
if errorlevel 1 (
    echo Services are not running. Starting...
    docker-compose up -d
    timeout /t 5
)

echo.
echo [Service Status]
docker-compose ps

echo.
echo [Kafka Topics]
docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092

echo.
echo [Travel Pipeline Logs - Last 50 lines]
docker-compose logs --tail=50 travel-pipeline

echo.
echo ✅ Monitor Complete
pause
