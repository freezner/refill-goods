#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상품 재고 모니터링 시스템
도매 웹사이트의 상품 품절 상태를 체크하고 알림을 발송하는 프로그램
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """메인 함수"""
    try:
        from gui import main as gui_main
        print("상품 재고 모니터링 시스템을 시작합니다...")
        gui_main()
    except ImportError as e:
        print(f"필요한 모듈을 불러올 수 없습니다: {e}")
        print("requirements.txt의 패키지들을 설치해주세요:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"프로그램 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
