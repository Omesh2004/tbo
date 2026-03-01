#!/bin/bash
# Initialize Ollama with required models
# This script runs inside the ollama container on startup

set -e

HOST="${OLLAMA_HOST:-0.0.0.0:11434}"
MODEL_ENDPOINT="http://localhost:11434"

echo "[INIT] Starting Ollama model initialization..."
echo "[INIT] Ollama Host: $HOST"

# Wait for Ollama to be ready
echo "[INIT] Waiting for Ollama service to be ready..."
for i in {1..30}; do
    if curl -s "$MODEL_ENDPOINT/api/tags" > /dev/null 2>&1; then
        echo "[INIT] ✓ Ollama service is ready"
        break
    fi
    echo "[INIT] Attempt $i/30 - Waiting for Ollama..."
    sleep 2
done

# Pull Phi4 Model
echo "[INIT] Pulling phi4 model..."
if curl -s -X POST "$MODEL_ENDPOINT/api/pull" \
    -H "Content-Type: application/json" \
    -d '{"name": "phi4", "stream": false}' > /dev/null 2>&1; then
    echo "[INIT] ✓ Phi4 model pulled successfully"
else
    echo "[INIT] ✗ Failed to pull phi4 model"
fi

# Pull Llama2 Model
echo "[INIT] Pulling llama2 model..."
if curl -s -X POST "$MODEL_ENDPOINT/api/pull" \
    -H "Content-Type: application/json" \
    -d '{"name": "llama2", "stream": false}' > /dev/null 2>&1; then
    echo "[INIT] ✓ Llama2 model pulled successfully"
else
    echo "[INIT] ✗ Failed to pull llama2 model"
fi

# Verify models are loaded
echo "[INIT] Verifying loaded models..."
curl -s "$MODEL_ENDPOINT/api/tags" | grep -q "phi4" && echo "[INIT] ✓ Phi4 verified" || echo "[INIT] ! Phi4 not found"
curl -s "$MODEL_ENDPOINT/api/tags" | grep -q "llama2" && echo "[INIT] ✓ Llama2 verified" || echo "[INIT] ! Llama2 not found"

echo "[INIT] ✓ Ollama initialization complete!"
