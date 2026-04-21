#!/bin/bash
# AWS Resource Manager Setup Script

set -e

echo "🚀 AWS Resource Manager Setup"
echo "==============================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make scripts executable
chmod +x aws_resource_manager.sh

# Test import
echo "🧪 Testing imports..."
python -c "import boto3; import requests; print('✓ All dependencies loaded successfully')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure AWS credentials: aws configure"
echo "2. Create config.yml from config.example.yml"
echo "3. Test: python aws_resource_manager.py --help"