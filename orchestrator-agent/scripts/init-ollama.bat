@echo off
REM Initialize Ollama with required models (Windows version)
REM Run this in PowerShell or CMD

setlocal enabledelayedexpansion

set "OLLAMA_HOST=http://localhost:11434"
set "MAX_RETRIES=30"
set "RETRY_COUNT=0"

echo [INIT] Starting Ollama model initialization...
echo [INIT] Ollama Host: %OLLAMA_HOST%

:WaitForOllama
echo [INIT] Waiting for Ollama service to be ready...
REM Test if Ollama is running
powershell -Command "try { $response = Invoke-WebRequest -Uri '%OLLAMA_HOST%/api/tags' -UseBasicParsing; exit 0 } catch { exit 1 }"

if errorlevel 1 (
    set /a RETRY_COUNT=!RETRY_COUNT! + 1
    if !RETRY_COUNT! lss %MAX_RETRIES% (
        echo [INIT] Attempt !RETRY_COUNT!/%MAX_RETRIES% - Waiting for Ollama...
        timeout /t 2 /nobreak
        goto WaitForOllama
    ) else (
        echo [INIT] ✗ Timeout waiting for Ollama service
        goto End
    )
)

echo [INIT] ✓ Ollama service is ready

REM Pull Phi4 Model
echo [INIT] Pulling phi4 model...
powershell -Command "Invoke-WebRequest -Uri '%OLLAMA_HOST%/api/pull' -Method Post -Headers @{'Content-Type'='application/json'} -Body '{\"name\": \"phi4\", \"stream\": false}' -UseBasicParsing" > nul 2>&1
if errorlevel 0 (
    echo [INIT] ✓ Phi4 model pulled successfully
) else (
    echo [INIT] ✗ Failed to pull phi4 model
)

REM Pull Llama2 Model
echo [INIT] Pulling llama2 model...
powershell -Command "Invoke-WebRequest -Uri '%OLLAMA_HOST%/api/pull' -Method Post -Headers @{'Content-Type'='application/json'} -Body '{\"name\": \"llama2\", \"stream\": false}' -UseBasicParsing" > nul 2>&1
if errorlevel 0 (
    echo [INIT] ✓ Llama2 model pulled successfully
) else (
    echo [INIT] ✗ Failed to pull llama2 model
)

echo [INIT] ✓ Ollama initialization complete!

:End
endlocal
