@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   WebRTC 서버 설정 및 실행 스크립트
echo ========================================
echo.

:: 현재 디렉터리를 배치 파일 위치로 변경
cd /d "%~dp0"

:: 1. Python 설치 확인
echo [1/4] Python 설치 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo    https://www.python.org/downloads/ 에서 Python을 설치해주세요.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo ✅ %%i 감지됨
echo.

:: 2. 가상 환경 생성
echo [2/4] Python 가상 환경 확인 중...
if exist "venv" (
    echo ⚠️  venv 폴더가 이미 존재합니다. 기존 환경을 사용합니다.
) else (
    echo 가상 환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 가상 환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
    echo ✅ 가상 환경 생성 완료
)
echo.

:: 3. 가상 환경 활성화 및 패키지 설치
echo [3/4] 필요한 라이브러리 설치 중...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 가상 환경 활성화에 실패했습니다.
    pause
    exit /b 1
)

pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ 라이브러리 설치에 실패했습니다.
    pause
    exit /b 1
)
echo ✅ 라이브러리 설치 완료
echo.

:: 4. SSL 인증서 생성
echo [4/4] SSL 인증서 확인 중...
if exist "cert.pem" (
    if exist "key.pem" (
        echo ⚠️  SSL 인증서가 이미 존재합니다. 기존 인증서를 사용합니다.
    ) else (
        echo SSL 인증서 생성 중...
        python gen_cert.py
    )
) else (
    echo SSL 인증서 생성 중...
    python gen_cert.py
)
if errorlevel 1 (
    echo ❌ SSL 인증서 생성에 실패했습니다.
    pause
    exit /b 1
)
echo ✅ SSL 인증서 준비 완료
echo.

:: 서버 실행
echo ========================================
echo   ✅ 설정 완료! 서버를 시작합니다.
echo ========================================
echo.
echo 접속 URL:
echo   - 뷰어:   https://localhost:3000
echo   - 카메라: https://localhost:3000/public/camera.html
echo.
echo 서버를 종료하려면 Ctrl+C를 누르세요.
echo ========================================
echo.

python server.py

pause
