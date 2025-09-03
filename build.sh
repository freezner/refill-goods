#!/bin/bash

echo "🚀 StockMonitor 빌드 시작..."
echo "================================"

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "가상환경을 활성화합니다..."
    source venv/bin/activate
else
    echo "❌ 가상환경을 찾을 수 없습니다."
    echo "python3 -m venv venv 명령어로 생성해주세요."
    exit 1
fi

# 통합 빌드 스크립트 실행
echo "통합 빌드 시스템을 시작합니다..."
python3 build_all.py
