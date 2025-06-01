@echo off
echo ===============================
echo  CLEANUP REPOSITORY - REMOVE SETUP FILES
echo ===============================
echo.

cd /d "H:\Vibe Coding\cascade-linter"

echo [1/4] Removing development setup files...
git rm push_to_github.bat
git rm push_to_github.sh
git rm push_to_github_fixed.bat
git rm push_to_github_fixed.sh
git rm manual_push.bat
git rm fix_push_conflict.bat
git rm complete_push.bat

echo.
echo [2/4] Updating .gitignore to prevent future setup files...
echo. >> .gitignore
echo # Development Setup Scripts (not needed by users) >> .gitignore
echo *_push*.bat >> .gitignore
echo *_push*.sh >> .gitignore
echo setup_*.bat >> .gitignore
echo setup_*.sh >> .gitignore

echo.
echo [3/4] Committing cleanup...
git add .gitignore
git commit -m "cleanup: Remove development setup scripts

- Remove push/setup batch files (not needed by end users)
- Update .gitignore to prevent similar files in future
- Keep GITHUB_SETUP.md for contributors
- Focus repository on the actual linting tool"

echo.
echo [4/4] Pushing cleanup to GitHub...
git push origin main

echo.
echo ================================
echo  CLEANUP COMPLETE!
echo ================================
echo.
echo Repository is now clean and professional
echo Only essential files remain for users
pause
