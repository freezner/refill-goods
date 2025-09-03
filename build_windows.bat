@echo off
echo 상품 재고 모니터링 시스템 - Windows 빌드 스크립트
echo ================================================

REM Python 가상환경 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python이 설치되지 않았습니다.
    echo Python 3.7 이상을 설치해주세요.
    pause
    exit /b 1
)

echo Python 버전 확인 중...
python --version

REM 필요한 패키지 설치
echo.
echo 필요한 패키지를 설치합니다...
pip install -r requirements.txt

if errorlevel 1 (
    echo 오류: 패키지 설치에 실패했습니다.
    pause
    exit /b 1
)

REM PyInstaller로 실행 파일 생성
echo.
echo 실행 파일을 생성합니다...
pyinstaller build_config.spec

if errorlevel 1 (
    echo 오류: 빌드에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo 빌드가 완료되었습니다!
echo 실행 파일 위치: dist\StockMonitor\StockMonitor.exe
echo.
echo 사용 방법:
echo 1. dist\StockMonitor 폴더를 원하는 위치로 복사
echo 2. StockMonitor.exe를 더블클릭하여 실행
echo 3. 처음 실행 시 이메일 설정을 완료하세요
echo.
pause
