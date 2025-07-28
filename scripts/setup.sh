#!/bin/bash
# SetForge Setup Script
# Automated setup and validation for SetForge

set -e  # Exit on any error

echo "🚀 SetForge Setup Script"
echo "========================"

# Move to project root directory
cd "$(dirname "$0")/.."

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Check if Python 3.8+ is available
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Python 3.8+ detected"
else
    echo "❌ Python 3.8+ required but not found"
    echo "Please install Python 3.8 or newer"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
echo "Installing core dependencies..."
pip install aiohttp PyYAML

# Try to install optional dependencies
echo "Installing optional dependencies..."
if pip install sentence-transformers torch numpy; then
    echo "✅ Semantic validation dependencies installed"
else
    echo "⚠️  Could not install semantic validation dependencies"
    echo "   SetForge will work but semantic validation will be disabled"
fi

# Install development dependencies (optional)
echo "Installing development dependencies..."
if pip install pytest pytest-asyncio black; then
    echo "✅ Development dependencies installed"
else
    echo "⚠️  Could not install development dependencies (optional)"
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x src/setforge.py src/setforge_cli.py src/examples.py

# Create default config if it doesn't exist
if [ ! -f "config/config.yaml" ]; then
    echo "Creating default configuration..."
    python3 src/setforge_cli.py create-config config/config.yaml
    echo "✅ Default configuration created"
else
    echo "✅ Configuration file already exists"
fi

# Run basic validation
echo "Running setup validation..."
if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from src.config import Config
    from src.text_processor import TextProcessor
    from src.qa_generator import QAGenerator
    from src.validator import QAValidator
    from src.exporter import DatasetExporter
    print('✅ All core modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"; then
    echo "✅ Core modules validation passed"
else
    echo "❌ Core modules validation failed"
    exit 1
fi

# Check for API key
echo "Checking API configuration..."
if [ -n "$DIGITALOCEAN_API_KEY" ]; then
    echo "✅ DIGITALOCEAN_API_KEY environment variable is set"
elif grep -q 'api_key: ""' config/config.yaml; then
    echo "⚠️  API key not configured"
    echo "   Set DIGITALOCEAN_API_KEY environment variable or edit config/config.yaml"
    echo "   Example: export DIGITALOCEAN_API_KEY='your-api-key'"
else
    echo "✅ API key appears to be configured in config/config.yaml"
fi

# Run example if requested
if [ "$1" = "--run-example" ]; then
    echo "Running examples..."
    python3 src/examples.py
fi

echo ""
echo "🎉 SetForge Setup Complete!"
echo "=========================="
echo ""
echo "Next steps:"
echo "1. Set your API key:"
echo "   export DIGITALOCEAN_API_KEY='your-api-key'"
echo ""
echo "2. Test with your files:"
echo "   python3 src/setforge.py input_directory/ output.jsonl"
echo ""
echo "3. Run examples:"
echo "   python3 src/examples.py"
echo ""
echo "4. Get help:"
echo "   python3 src/setforge.py --help"
echo "   python3 src/setforge_cli.py --help"
echo ""
echo "For detailed documentation, see docs/README.md"
