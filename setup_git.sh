#!/bin/bash
# Git Setup Script for Data to Video Encoder Project

echo "================================================"
echo "  Data to Video Encoder - Git Setup Script"
echo "================================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

echo "✓ Git is installed"
echo ""

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✓ Repository initialized"
else
    echo "✓ Git repository already exists"
fi

echo ""
echo "📝 Setting up repository files..."

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Project specific
output_frames/
output_advanced/
frames/
basic_*_frames/
advanced_*_frames/
*.raw
*.wav
*.mp4
*.avi
*.mkv
reconstructed_*
test_*.bin
test_*.txt

# Test files
*.bin
*.zip
*.tar.gz
*.7z

# Temporary files
*.tmp
*.temp
*.log
EOF
    echo "✓ .gitignore created"
fi

echo ""
echo "📋 Current files in directory:"
ls -la

echo ""
echo "➕ Adding files to git..."
git add .

echo ""
echo "📊 Git status:"
git status

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Review the files to be committed:"
echo "   git status"
echo ""
echo "2. Make your first commit:"
echo "   git commit -m 'Initial commit: Data to Video Encoder'"
echo ""
echo "3. Create a GitHub repository, then add remote:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo ""
echo "4. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "================================================"
