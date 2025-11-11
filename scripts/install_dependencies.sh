#!/bin/bash

# Install Dependencies Script
#
# CHỨC NĂNG:
# - Tự động detect venv hoặc global Python
# - Install faker và tqdm vào đúng environment
#
# USAGE:
# chmod +x scripts/install_dependencies.sh
# ./scripts/install_dependencies.sh

set -e

echo ""
echo "============================================================"
echo "📦 INSTALL DEPENDENCIES"
echo "============================================================"
echo ""

# Get script directory và project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# Change to project root
cd "$PROJECT_ROOT"
echo "📁 Working directory: $PROJECT_ROOT"
echo ""

# Check if venv exists
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo "🐍 Virtual environment detected!"
    echo "Activating venv..."
    source "$PROJECT_ROOT/venv/bin/activate"

    PYTHON_CMD="python"
    PIP_CMD="pip"

    echo "✅ venv activated"
    echo "Python: $(which python)"
    echo "Pip: $(which pip)"
else
    echo "⚠️  No virtual environment found"
    echo "Installing to global Python..."

    PYTHON_CMD="python3"
    PIP_CMD="pip3"

    echo "Python: $(which python3)"
    echo "Pip: $(which pip3)"
fi

echo ""
echo "📦 Installing dependencies..."
echo "  - bcrypt==4.0.1 (fix passlib compatibility)"
echo "  - faker==22.0.0"
echo "  - tqdm==4.66.1"
echo ""

# Install bcrypt 4.0.1 first (important for passlib compatibility)
echo "Installing bcrypt 4.0.1..."
if $PIP_CMD install bcrypt==4.0.1; then
    echo "✅ bcrypt installed"
else
    echo "⚠️  bcrypt installation warning (continuing...)"
fi

# Install other dependencies
if $PIP_CMD install faker==22.0.0 tqdm==4.66.1; then
    echo ""
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "Installed packages:"
    $PIP_CMD list | grep -E "faker|tqdm|bcrypt"
else
    echo ""
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "============================================================"
echo "🎉 INSTALLATION COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Start Docker: docker-compose up -d"
echo "  2. Generate data: python scripts/generate_dummy_data.py"
echo ""
echo "Or use one-click script:"
echo "  ./scripts/setup_and_generate.sh"
echo ""
echo "============================================================"
echo ""
