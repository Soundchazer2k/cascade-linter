#!/bin/bash
set -e  # Exit on any error

echo "================================"
echo " CASCADE LINTER - GITHUB SETUP"
echo "================================"
echo

# Navigate to project directory
echo "[0/7] Navigating to project directory..."
cd "H:/Vibe Coding/cascade-linter" || {
    echo "ERROR: Could not navigate to project directory"
    exit 1
}

echo "[1/7] Checking Git status and committing new files..."
git add GITHUB_SETUP.md push_to_github.bat push_to_github.sh push_to_github_fixed.bat push_to_github_fixed.sh
git commit -m "docs: Add GitHub setup scripts and guide" || echo "No changes to commit"

echo
echo "[2/7] Checking if Git is configured..."
if ! git config user.name >/dev/null 2>&1; then
    echo "ERROR: Git is not configured. Please run:"
    echo "git config --global user.name 'Your Name'"
    echo "git config --global user.email 'your.email@example.com'"
    exit 1
fi

echo
echo "[3/7] Checking for existing remotes..."
if git remote | grep -q origin; then
    echo "WARNING: Remote 'origin' already exists. Removing it..."
    git remote remove origin
fi

echo
echo "[4/7] Creating release tag v1.1.0..."
git tag -d v1.1.0 >/dev/null 2>&1 || true  # Remove tag if exists
git tag -a v1.1.0 -m "Release v1.1.0: Enhanced dependency analysis with micro-improvements"

echo
echo "[5/7] MANUAL STEP REQUIRED!"
echo
echo "Please go to: https://github.com/new"
echo "1. Repository name: cascade-linter"
echo "2. Description: Professional Python code quality toolkit with cascading linter pipeline and enhanced dependency analysis"
echo "3. Choose: Public repository"
echo "4. DO NOT add README or .gitignore (you already have them)"
echo "5. License: MIT"
echo "6. Click 'Create repository'"
echo
read -p "After creating repository, enter your GitHub username: " username

echo
echo "[6/7] Adding GitHub remote and pushing..."
git remote add origin "https://github.com/$username/cascade-linter.git"

echo "Pushing to main branch..."
if ! git push -u origin main; then
    echo "ERROR: Push failed. Check:"
    echo "1. Repository was created on GitHub"
    echo "2. GitHub credentials are configured"
    echo "3. Internet connection is working"
    exit 1
fi

echo
echo "[7/7] Pushing release tags..."
git push origin v1.1.0 || echo "WARNING: Tag push failed, but main branch was pushed successfully"

echo
echo "================================"
echo " SUCCESS! Your project is live!"
echo "================================"
echo
echo "Repository URL: https://github.com/$username/cascade-linter"
echo
echo "NEXT STEPS:"
echo "1. Go to repository settings and add topics:"
echo "   python, linting, code-quality, ruff, flake8, pylint, bandit, mypy, dependency-analysis, cli-tool"
echo "2. Enable Issues, Wiki, and Discussions"
echo "3. Create GitHub Release from v1.1.0 tag"
echo "4. Share with the Python community!"
echo
echo "Thank you for contributing to open source! 🚀"
read -p "Press Enter to finish..."
