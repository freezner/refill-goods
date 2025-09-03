#!/bin/bash

echo "상품 재고 모니터링 시스템 - MacOS 빌드 스크립트"
echo "================================================"

# Python 가상환경 확인
if ! command -v python3 &> /dev/null; then
    echo "오류: Python3가 설치되지 않았습니다."
    echo "Python 3.7 이상을 설치해주세요."
    exit 1
fi

echo "Python 버전 확인 중..."
python3 --version

# 필요한 패키지 설치
echo ""
echo "필요한 패키지를 설치합니다..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "오류: 패키지 설치에 실패했습니다."
    exit 1
fi

# PyInstaller로 실행 파일 생성
echo ""
echo "실행 파일을 생성합니다..."
pyinstaller build_config.spec

if [ $? -ne 0 ]; then
    echo "오류: 빌드에 실패했습니다."
    exit 1
fi

echo ""
echo "빌드가 완료되었습니다!"
echo "실행 파일 위치: dist/StockMonitor/StockMonitor"
echo ""
echo "사용 방법:"
echo "1. dist/StockMonitor 폴더를 원하는 위치로 복사"
echo "2. StockMonitor를 더블클릭하여 실행"
echo "3. 처음 실행 시 이메일 설정을 완료하세요"
echo ""
echo "참고: MacOS에서 처음 실행 시 보안 경고가 나타날 수 있습니다."
echo "시스템 환경설정 > 보안 및 개인정보보호에서 허용해주세요."
echo ""
