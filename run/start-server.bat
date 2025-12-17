@echo off
chcp 65001 >nul
echo ========================================
echo   WebRTC Minimal Server 시작
echo ========================================
echo.

cd /d "%~dp0.."

echo [1/3] 기존 컨테이너 정리 중...
docker-compose down 2>nul

echo [2/3] 이미지 빌드 및 컨테이너 시작...
docker-compose up -d --build

echo [3/3] 컨테이너 상태 확인...
docker ps --filter "name=webrtc-minimal"

echo.
echo ========================================
echo   서버가 시작되었습니다!
echo   - 로컬: https://localhost:3000
echo   - 외부: https://[PC의 IP]:3000
echo ========================================
echo.
pause
