#!/bin/bash
# Orchestrator Agent Setup Script

echo "=================================================="
echo "Orchestrator Agent - Setup Script"
echo "=================================================="

# Check Python version
echo ""
echo "[1/5] Checking Python version..."
python --version || { echo "Python not found. Please install Python 3.11+"; exit 1; }

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "[3/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
echo ""
echo "[4/5] Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file (fill in your configuration)"
else
    echo "✓ .env file already exists"
fi

# Create directories
echo ""
echo "[5/5] Creating necessary directories..."
mkdir -p app/__pycache__ app/ml/__pycache__ app/integrations/__pycache__

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Ensure Ollama is running: ollama serve"
echo "3. Pull required models:"
echo "   - ollama pull phi4"
echo "   - ollama pull llama2"
echo "4. Start the application:"
echo "   python -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "=================================================="
