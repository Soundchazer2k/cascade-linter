@echo off
setlocal enabledelayedexpansion

echo ================================
echo  CASCADE LINTER - GITHUB SETUP
echo ================================
echo.

REM Navigate to project directory
echo [0/7] Navigating to project directory...
cd /d "H:\Vibe Coding\cascade-linter"
if !errorlevel! neq 0 (
    echo ERROR: Could not navigate to project directory
    pause
    exit /b 1
)

echo [1/7] Checking Git status and committing new files...
git add GITHUB_SETUP.md push_to_github.bat push_to_github.sh
git commit -m "docs: Add GitHub setup scripts and guide"

echo.
echo [2/7] Checking if Git is configured...
git config user.name >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Git is not configured. Please run:
    echo git config --global user.name "Your Name"
    echo git config --global user.email "your.email@example.com"
    pause
    exit /b 1
)

echo.
echo [3/7] Checking for existing remotes...
git remote | findstr origin >nul 2>&1
if !errorlevel! equ 0 (
    echo WARNING: Remote 'origin' already exists. Removing it...
    git remote remove origin
)

echo.
echo [4/7] Creating release tag v1.1.0...
git tag -d v1.1.0 >nul 2>&1
git tag -a v1.1.0 -m "Release v1.1.0: Enhanced dependency analysis with micro-improvements"
if !errorlevel! neq 0 (
    echo ERROR: Could not create tag
    pause
    exit /b 1
)

echo.
echo [5/7] MANUAL STEP REQUIRED!
echo.
echo Please go to: https://github.com/new
echo 1. Repository name: cascade-linter
echo 2. Description: Professional Python code quality toolkit with cascading linter pipeline and enhanced dependency analysis
echo 3. Choose: Public repository
echo 4. DO NOT add README or .gitignore (you already have them)
echo 5. License: MIT
echo 6. Click "Create repository"
echo.
set /p username="After creating repository, enter your GitHub username: "

echo.
echo [6/7] Adding GitHub remote and pushing...
git remote add origin https://github.com/!username!/cascade-linter.git
if !errorlevel! neq 0 (
    echo ERROR: Could not add remote
    pause
    exit /b 1
)

echo Pushing to main branch...
git push -u origin main
if !errorlevel! neq 0 (
    echo ERROR: Push failed. Check:
    echo 1. Repository was created on GitHub
    echo 2. GitHub credentials are configured
    echo 3. Internet connection is working
    pause
    exit /b 1
)

echo.
echo [7/7] Pushing release tags...
git push origin v1.1.0
if !errorlevel! neq 0 (
    echo WARNING: Tag push failed, but main branch was pushed successfully
)

echo.
echo ================================
echo  SUCCESS! Your project is live!
echo ================================
echo.
echo Repository URL: https://github.com/!username!/cascade-linter
echo.
echo NEXT STEPS:
echo 1. Go to repository settings and add topics:
echo    python, linting, code-quality, ruff, flake8, pylint, bandit, mypy, dependency-analysis, cli-tool
echo 2. Enable Issues, Wiki, and Discussions
echo 3. Create GitHub Release from v1.1.0 tag
echo 4. Share with the Python community!
echo.
echo Thank you for contributing to open source! 🚀
pause
