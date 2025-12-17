@echo off
chcp 65001 >nul
echo ========================================
echo   Windows 방화벽 포트 3000 열기
echo   (관리자 권한 필요)
echo ========================================
echo.

:: 관리자 권한 확인
net session >nul 2>&1
if errorlevel 1 (
    echo 관리자 권한이 필요합니다.
    echo 이 파일을 우클릭하여 "관리자 권한으로 실행"을 선택하세요.
    echo.
    pause
    exit /b 1
)

netsh advfirewall firewall add rule name="WebRTC Server Port 3000" dir=in action=allow protocol=tcp localport=3000

echo.
echo ========================================
echo   방화벽 규칙이 추가되었습니다.
echo   이제 외부에서 접속할 수 있습니다.
echo ========================================
pause
