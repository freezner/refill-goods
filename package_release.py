#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
릴리즈 패키지 생성 스크립트
Windows와 MacOS용 실행 파일을 패키징합니다.
"""

import os
import shutil
import zipfile
import platform
import subprocess
import sys
from pathlib import Path

def run_command(command, shell=False):
    """명령어를 실행하고 결과를 반환합니다."""
    try:
        if shell:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"오류: {result.stderr}")
            return False
        
        print(f"성공: {result.stdout}")
        return True
    except Exception as e:
        print(f"명령어 실행 실패: {e}")
        return False

def create_zip_archive(source_dir, output_file):
    """폴더를 ZIP 파일로 압축합니다."""
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        
        print(f"ZIP 파일 생성 완료: {output_file}")
        return True
    except Exception as e:
        print(f"ZIP 파일 생성 실패: {e}")
        return False

def build_windows():
    """Windows용 실행 파일을 빌드합니다."""
    print("Windows용 실행 파일을 빌드합니다...")
    
    if platform.system() != "Windows":
        print("경고: Windows가 아닌 시스템에서 Windows 빌드를 시도합니다.")
    
    # PyInstaller 실행
    if not run_command([sys.executable, "-m", "PyInstaller", "build_config.spec"]):
        return False
    
    # dist 폴더 확인
    dist_dir = Path("dist/StockMonitor")
    if not dist_dir.exists():
        print("오류: dist/StockMonitor 폴더를 찾을 수 없습니다.")
        return False
    
    # ZIP 파일 생성
    zip_file = "StockMonitor-Windows.zip"
    if create_zip_archive(dist_dir, zip_file):
        print(f"Windows 패키지 생성 완료: {zip_file}")
        return True
    
    return False

def build_macos():
    """MacOS용 실행 파일을 빌드합니다."""
    print("MacOS용 실행 파일을 빌드합니다...")
    
    if platform.system() != "Darwin":
        print("경고: MacOS가 아닌 시스템에서 MacOS 빌드를 시도합니다.")
    
    # PyInstaller 실행
    if not run_command([sys.executable, "-m", "PyInstaller", "build_config.spec"]):
        return False
    
    # dist 폴더 확인
    dist_dir = Path("dist/StockMonitor")
    if not dist_dir.exists():
        print("오류: dist/StockMonitor 폴더를 찾을 수 없습니다.")
        return False
    
    # ZIP 파일 생성
    zip_file = "StockMonitor-MacOS.zip"
    if create_zip_archive(dist_dir, zip_file):
        print(f"MacOS 패키지 생성 완료: {zip_file}")
        return True
    
    return False

def build_linux():
    """Linux용 소스 패키지를 생성합니다."""
    print("Linux용 소스 패키지를 생성합니다...")
    
    # 소스 파일들을 포함한 ZIP 생성
    source_files = [
        "main.py", "gui.py", "monitor.py", "stock_checker.py", 
        "email_sender.py", "config.py", "requirements.txt", 
        "README.md", "INSTALL.md", "env_example.txt"
    ]
    
    zip_file = "StockMonitor-Linux-Source.zip"
    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in source_files:
                if os.path.exists(file):
                    zipf.write(file)
                else:
                    print(f"경고: {file} 파일을 찾을 수 없습니다.")
        
        print(f"Linux 소스 패키지 생성 완료: {zip_file}")
        return True
    except Exception as e:
        print(f"Linux 패키지 생성 실패: {e}")
        return False

def cleanup():
    """빌드 과정에서 생성된 임시 파일들을 정리합니다."""
    print("임시 파일들을 정리합니다...")
    
    # PyInstaller 생성 파일들 정리
    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["*.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"삭제됨: {dir_name}")
    
    # .spec 파일들 정리 (build_config.spec 제외)
    for spec_file in Path(".").glob("*.spec"):
        if spec_file.name != "build_config.spec":
            spec_file.unlink()
            print(f"삭제됨: {spec_file}")

def main():
    """메인 함수"""
    print("상품 재고 모니터링 시스템 - 릴리즈 패키지 생성")
    print("=" * 50)
    
    # 현재 시스템 확인
    current_system = platform.system()
    print(f"현재 시스템: {current_system}")
    
    # 필요한 패키지 설치 확인
    try:
        import PyInstaller
        print("PyInstaller 설치 확인됨")
    except ImportError:
        print("PyInstaller를 설치합니다...")
        if not run_command([sys.executable, "-m", "pip", "install", "pyinstaller"]):
            print("오류: PyInstaller 설치에 실패했습니다.")
            return
    
    # 빌드 옵션 선택
    print("\n빌드할 플랫폼을 선택하세요:")
    print("1. Windows")
    print("2. MacOS")
    print("3. Linux (소스)")
    print("4. 모든 플랫폼")
    print("5. 현재 시스템에 맞는 플랫폼")
    
    try:
        choice = input("선택 (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n빌드가 취소되었습니다.")
        return
    
    success_count = 0
    
    if choice == "1" or choice == "4":
        if build_windows():
            success_count += 1
    
    if choice == "2" or choice == "4":
        if build_macos():
            success_count += 1
    
    if choice == "3" or choice == "4":
        if build_linux():
            success_count += 1
    
    if choice == "5":
        if current_system == "Windows":
            if build_windows():
                success_count += 1
        elif current_system == "Darwin":
            if build_macos():
                success_count += 1
        else:
            if build_linux():
                success_count += 1
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("빌드 결과 요약:")
    print(f"성공: {success_count}개 플랫폼")
    
    if success_count > 0:
        print("\n생성된 파일들:")
        for file in os.listdir("."):
            if file.startswith("StockMonitor-") and file.endswith(".zip"):
                file_size = os.path.getsize(file) / (1024 * 1024)  # MB
                print(f"  {file} ({file_size:.1f} MB)")
        
        print("\n배포 준비가 완료되었습니다!")
        print("생성된 ZIP 파일들을 사용자에게 배포할 수 있습니다.")
    else:
        print("빌드에 실패했습니다. 오류 메시지를 확인해주세요.")
    
    # 정리 옵션
    try:
        cleanup_choice = input("\n임시 파일들을 정리하시겠습니까? (y/N): ").strip().lower()
        if cleanup_choice in ['y', 'yes']:
            cleanup()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
