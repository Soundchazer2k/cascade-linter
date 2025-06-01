@echo off
echo ===============================
echo  MANUAL GITHUB SETUP - FIXED
echo ===============================
echo.

cd /d "H:\Vibe Coding\cascade-linter"

echo [1/4] Checking current remotes...
git remote -v

echo.
echo [2/4] Removing any existing remotes...
git remote remove origin 2>nul || echo "No origin remote to remove"

echo.
echo [3/4] MANUAL STEP: Create Repository on GitHub
echo.
echo Go to: https://github.com/new
echo 1. Repository name: cascade-linter
echo 2. Make it PUBLIC
echo 3. DO NOT add README or .gitignore
echo 4. Click "Create repository"
echo.
pause

echo.
echo [4/4] Adding remote and pushing...
git remote add origin https://github.com/Soundchazer2k/cascade-linter.git
echo Remote added. Now pushing...

git push -u origin main
if %errorlevel% equ 0 (
    echo SUCCESS! Main branch pushed.
    git push origin v1.1.0
    if %errorlevel% equ 0 (
        echo SUCCESS! Tag pushed.
    ) else (
        echo Tag push failed, but that's OK.
    )
) else (
    echo FAILED! Check if repository exists at:
    echo https://github.com/Soundchazer2k/cascade-linter
)

echo.
echo Repository should be at: https://github.com/Soundchazer2k/cascade-linter
pause
