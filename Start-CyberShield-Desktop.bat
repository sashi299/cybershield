@echo off
title CyberShield Desktop - Snapdragon On-Device AI
echo ========================================================
echo   CYBERSHIELD DESKTOP
echo   On-Device AI Security Guard for Snapdragon HP PCs
echo ========================================================
echo.
echo [1/2] Starting CyberShield local AI backend server (FastAPI)...
start "CyberShield-Backend" /min python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
timeout /t 2 /nobreak >nul

echo [2/2] Launching CyberShield Desktop Interface...
start "" "http://localhost:8000"

echo.
echo CyberShield is running locally with On-Device AI models!
echo Text Model: DistilBERT (ONNX INT8)
echo Vision Model: MobileNet-v2 (ONNX)
echo.
echo Press any key to stop the backend and close.
pause >nul
taskkill /F /IM python.exe /T 2>nul
echo Done!
