@echo off
chcp 65001
echo ========================================
echo   Push to GitHub
echo ========================================
echo.

git init
git add .
git commit -m "Add NLP demo app"
git branch -M main

echo.
echo Please create repo first at: https://github.com/new
echo Repo name: nlp-demo
echo.
pause

git remote add origin https://github.com/yddd0413/nlp-demo.git
git push -u origin main

echo.
echo ========================================
echo Done! Now deploy:
echo 1. Go to https://share.streamlit.io
echo 2. Login with GitHub
echo 3. Click "New app"
echo 4. Select yddd0413/nlp-demo
echo 5. Click "Deploy"
echo ========================================
pause
