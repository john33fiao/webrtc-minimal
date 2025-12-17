@echo off
chcp 65001 >nul
echo ========================================
echo   WebRTC Minimal Server 로그
echo ========================================
echo   (Ctrl+C로 종료)
echo.

docker logs -f webrtc-minimal
