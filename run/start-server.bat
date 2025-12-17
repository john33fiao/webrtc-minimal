@echo off
chcp 65001 >nul
echo ========================================
echo   WebRTC Minimal Server 시작
echo ========================================
echo.

cd /d "%~dp0"

:: 이미지가 없으면 tar 파일에서 로드
docker images webrtc-server:latest --format "{{.Repository}}" | findstr /r "." >nul
if errorlevel 1 (
    if exist "webrtc-server.tar" (
        echo [1/4] Docker 이미지 로드 중...
        docker load -i webrtc-server.tar
    ) else (
        echo [오류] webrtc-server.tar 파일이 없습니다.
        echo        이미지 파일을 run 폴더에 넣어주세요.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Docker 이미지 확인 완료
)

echo [2/4] 기존 컨테이너 정리 중...
docker-compose down 2>nul

echo [3/4] 컨테이너 시작...
docker-compose up -d

echo [4/4] 컨테이너 상태 확인...
docker ps --filter "name=webrtc-minimal"

echo.
echo ========================================
echo   서버가 시작되었습니다!
echo   - 로컬: https://localhost:3000
echo   - 외부: https://[PC의 IP]:3000
echo ========================================
echo.
pause
