@echo off
chcp 65001 >nul
echo 🚀 StockMonitor 빌드 시작...
echo ================================

REM 가상환경 활성화
if exist "venv\Scripts\activate.bat" (
    echo 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
) else (
    echo ❌ 가상환경을 찾을 수 없습니다.
    echo python -m venv venv 명령어로 생성해주세요.
    pause
    exit /b 1
)

REM 통합 빌드 스크립트 실행
echo 통합 빌드 시스템을 시작합니다...
python build_all.py
pause
