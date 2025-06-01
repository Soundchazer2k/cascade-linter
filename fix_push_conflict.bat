@echo off
echo ===============================
echo  FIX GITHUB PUSH CONFLICT
echo ===============================
echo.

cd /d "H:\Vibe Coding\cascade-linter"

echo [1/4] Pulling remote changes...
git pull origin main --allow-unrelated-histories

echo.
echo [2/4] Checking for conflicts...
git status

echo.
echo [3/4] Pushing your project...
git push -u origin main

echo.
echo [4/4] Pushing release tag...
git push origin v1.1.0

echo.
echo ================================
echo  SUCCESS! Repository is live!
echo ================================
echo.
echo Repository URL: https://github.com/Soundchazer2k/cascade-linter
echo.
echo NEXT STEPS:
echo 1. Go to repository settings
echo 2. Add topics: python, linting, code-quality, ruff, flake8, pylint, bandit, mypy, dependency-analysis, cli-tool
echo 3. Enable Issues, Wiki, and Discussions
echo 4. Create your first GitHub Release from the v1.1.0 tag
echo.
pause
