#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StockMonitor - 빠른 빌드 스크립트
=================================

간단한 명령줄 인수로 빠르게 빌드할 수 있습니다.
"""

import sys
import subprocess
from pathlib import Path

def quick_build():
    """빠른 빌드 실행"""
    if len(sys.argv) < 2:
        print("🚀 StockMonitor - 빠른 빌드")
        print("=" * 40)
        print("사용법:")
        print("  python quick_build.py [platform]")
        print("")
        print("플랫폼 옵션:")
        print("  current  - 현재 시스템용")
        print("  windows  - Windows용")
        print("  macos    - MacOS용")
        print("  linux    - Linux용")
        print("  all      - 모든 플랫폼용")
        print("")
        print("예시:")
        print("  python quick_build.py current")
        print("  python quick_build.py macos")
        return
    
    platform = sys.argv[1].lower()
    
    # 플랫폼 매핑
    platform_map = {
        'current': '1',
        'windows': '2',
        'macos': '3',
        'linux': '4',
        'all': '5'
    }
    
    if platform not in platform_map:
        print(f"❌ 지원되지 않는 플랫폼: {platform}")
        print("사용 가능한 플랫폼: current, windows, macos, linux, all")
        return
    
    choice = platform_map[platform]
    
    # 가상환경 확인
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print("❌ 가상환경을 찾을 수 없습니다.")
        print("python3 -m venv venv 명령어로 생성해주세요.")
        return
    
    # PyInstaller 확인
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller가 설치되지 않았습니다.")
        print("pip install pyinstaller 명령어로 설치해주세요.")
        return
    
    print(f"🔨 {platform} 플랫폼용 빠른 빌드 시작...")
    
    # 통합 빌드 스크립트 실행
    try:
        # 자동으로 선택된 옵션으로 빌드 실행
        cmd = [sys.executable, "build_all.py"]
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
        
        # 선택된 옵션 전송
        process.communicate(input=f"{choice}\n")
        
        if process.returncode == 0:
            print(f"✅ {platform} 플랫폼용 빌드 완료!")
        else:
            print(f"❌ {platform} 플랫폼용 빌드 실패!")
            
    except Exception as e:
        print(f"❌ 빌드 중 오류 발생: {e}")

if __name__ == "__main__":
    quick_build()
