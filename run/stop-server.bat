@echo off
chcp 65001 >nul
echo ========================================
echo   WebRTC Minimal Server 종료
echo ========================================
echo.

cd /d "%~dp0"

docker-compose down

echo.
echo 서버가 종료되었습니다.
pause
