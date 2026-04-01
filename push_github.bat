@echo off
echo ========================================
echo   推送代码到GitHub
echo ========================================
echo.

git init
git add .
git commit -m "Add NLP demo app"
git branch -M main

echo.
echo 请先在GitHub创建仓库：
echo 1. 打开 https://github.com/new
echo 2. 仓库名填: nlp-demo
echo 3. 点击 Create repository
echo.
pause

git remote add origin https://github.com/yddd0413/nlp-demo.git
git push -u origin main

echo.
echo ========================================
echo 推送完成！
echo.
echo 接下来部署到Streamlit Cloud:
echo 1. 打开 https://share.streamlit.io
echo 2. 用GitHub登录
echo 3. 点击 "New app"
echo 4. 选择 yddd0413/nlp-demo
echo 5. 点击 "Deploy"
echo ========================================
pause
