#!/bin/bash
echo "================================"
echo " CASCADE LINTER - GITHUB SETUP"
echo "================================"
echo

echo "[1/6] Checking Git status..."
git status

echo
echo "[2/6] Creating release tag v1.1.0..."
git tag -a v1.1.0 -m "Release v1.1.0: Enhanced dependency analysis with micro-improvements"

echo
echo "[3/6] Ready to push to GitHub!"
echo
echo "IMPORTANT: Go to https://github.com/new and create a repository named 'cascade-linter'"
echo "- Choose: Public repository"
echo "- DO NOT add README (you already have one)"
echo "- DO NOT add .gitignore (you already have one)"
echo "- License: MIT"
echo
read -p "Press Enter after creating the GitHub repository..."

echo
echo "[4/6] Adding GitHub remote..."
read -p "Enter your GitHub username: " username
git remote add origin https://github.com/$username/cascade-linter.git

echo
echo "[5/6] Pushing to GitHub..."
git branch -M main
git push -u origin main

echo
echo "[6/6] Pushing release tags..."
git push origin v1.1.0

echo
echo "================================"
echo " SUCCESS! Your project is live!"
echo "================================"
echo
echo "Repository URL: https://github.com/$username/cascade-linter"
echo
echo "NEXT STEPS:"
echo "1. Go to your repository settings"
echo "2. Add description: 'Professional Python code quality toolkit with cascading linter pipeline and enhanced dependency analysis'"
echo "3. Add topics: python, linting, code-quality, ruff, flake8, pylint, bandit, mypy, dependency-analysis, cli-tool"
echo "4. Enable Issues, Wiki, and Discussions"
echo "5. Create your first GitHub Release from the v1.1.0 tag"
echo
read -p "Press Enter to finish..."
