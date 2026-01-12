#!/bin/bash
# Quick Start Script for Dash Dashboard

echo ""
echo "============================================================"
echo "🚀 Dash Dashboard - Quick Start"
echo "============================================================"
echo ""

# Check if in right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    echo "   Please run this script from the dashboard directory"
    exit 1
fi

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ Ready to start!"
echo "============================================================"
echo ""
echo "Starting Dash Dashboard..."
echo ""

# Start the app
python app.py
