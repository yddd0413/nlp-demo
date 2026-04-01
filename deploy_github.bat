@echo off
echo ========================================
echo   一键部署到GitHub
echo ========================================
echo.

set /p REPO="请输入你的GitHub仓库URL (如: https://github.com/用户名/仓库名.git): "

echo.
echo [1] 初始化Git仓库...
git init

echo.
echo [2] 添加文件...
git add .

echo.
echo [3] 提交...
git commit -m "Add NLP demo app"

echo.
echo [4] 推送到GitHub...
git branch -M main
git remote add origin %REPO%
git push -u origin main

echo.
echo ========================================
echo   推送完成！
echo ========================================
echo.
echo 接下来：
echo 1. 访问 https://share.streamlit.io
echo 2. 用GitHub登录
echo 3. 点击 "New app" 选择你的仓库
echo 4. 点击 "Deploy"
echo.
pause
