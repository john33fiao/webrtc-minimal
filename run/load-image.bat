@echo off
chcp 65001 >nul
echo ========================================
echo   tar 파일에서 Docker 이미지 로드
echo ========================================
echo.

cd /d "%~dp0"

if not exist "webrtc-server.tar" (
    echo [오류] webrtc-server.tar 파일이 없습니다.
    echo        먼저 save-image.bat을 실행하거나 tar 파일을 복사해주세요.
    pause
    exit /b 1
)

echo Docker 이미지 로드 중...
docker load -i webrtc-server.tar

echo.
echo ========================================
echo   로드 완료!
echo   start-server.bat으로 서버를 시작하세요.
echo ========================================
pause
