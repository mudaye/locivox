#!/bin/bash

# Locivox Setup Script
# Automates the installation process

set -e  # Exit on error

echo "╔══════════════════════════════════════╗"
echo "║     Locivox Setup Script v0.1.0      ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION found, but version $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Check FFmpeg
echo "🔍 Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed."
    echo "   Install it with:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu: sudo apt install ffmpeg"
    echo "   - Windows: choco install ffmpeg"
    echo ""
    read -p "Continue without FFmpeg? (not recommended) [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ FFmpeg detected"
fi
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip and installing setuptools..."
pip install --upgrade pip setuptools wheel > /dev/null
echo "✅ pip and setuptools upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "╔══════════════════════════════════════╗"
echo "║          Setup Successful!           ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "🚀 To get started:"
echo ""
echo "   1. Activate the virtual environment:"
echo "      source venv/bin/activate"
echo ""
echo "   2. Run Locivox:"
echo "      python src/cli.py"
echo ""
echo "   3. Check the README for more options:"
echo "      cat README.md"
echo ""
echo "Happy transcribing! 🎤"
