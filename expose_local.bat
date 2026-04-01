@echo off
echo ========================================
echo   本地服务 + Ngrok外网暴露
echo ========================================
echo.

echo [1] 安装pyngrok...
pip install pyngrok -q

echo.
echo [2] 启动Streamlit服务...
echo.
echo 注意：启动后请查看终端输出的外网链接
echo 链接格式如: https://xxxx.ngrok.io
echo.

start "" streamlit run nlp_app.py

timeout /t 5 /nobreak > nul

echo.
echo [3] 启动Ngrok隧道...
ngrok http 8501

pause
