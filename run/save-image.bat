@echo off
chcp 65001 >nul
echo ========================================
echo   Docker 이미지를 tar 파일로 저장
echo ========================================
echo.

cd /d "%~dp0.."

:: 이미지가 없으면 먼저 빌드
docker images webrtc_clear-webrtc-server --format "{{.Repository}}" | findstr /r "." >nul
if errorlevel 1 (
    echo 이미지가 없습니다. 먼저 빌드합니다...
    docker-compose build
)

echo Docker 이미지를 tar 파일로 저장 중...
docker save -o run\webrtc-server.tar webrtc_clear-webrtc-server:latest

echo.
echo ========================================
echo   저장 완료: run\webrtc-server.tar
echo ========================================
pause
