@echo off
chcp 65001 >nul
echo ========================================
echo   Docker 이미지를 tar 파일로 저장
echo ========================================
echo.

cd /d "%~dp0.."

:: 프로젝트 루트의 docker-compose.yml로 빌드
echo [1/2] Docker 이미지 빌드 중...
docker-compose build

echo [2/2] Docker 이미지를 tar 파일로 저장 중...
docker tag webrtc_clear-webrtc-server:latest webrtc-server:latest
docker save -o run\webrtc-server.tar webrtc-server:latest

echo.
echo ========================================
echo   저장 완료: run\webrtc-server.tar
echo   run 폴더를 압축하여 배포하세요.
echo ========================================
pause
