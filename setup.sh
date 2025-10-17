#!/bin/bash
# Setup script for KPI Pipeline (Mac/Linux)

echo "=================================================="
echo "KPI Pipeline - Setup Script"
echo "=================================================="
echo ""

# Check Python version
echo "[1/4] Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Create virtual environment
echo ""
echo "[2/4] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "ℹ Virtual environment already exists"
else
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[3/4] Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

# Install requirements
echo ""
echo "[4/4] Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Requirements installed"

echo ""
echo "=================================================="
echo "✓ Setup completed successfully!"
echo "=================================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the pipeline:"
echo "  python main.py"
echo ""
echo "For more information, see README.md"
echo "=================================================="



