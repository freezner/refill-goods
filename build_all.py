#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StockMonitor - 통합 빌드 및 패키징 스크립트
============================================

이 스크립트는 Windows, MacOS, Linux를 위한 실행 파일과 패키지를 생성합니다.
"""

import os
import sys
import platform
import subprocess
import shutil
import zipfile
from pathlib import Path

class BuildManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.venv_dir = self.project_root / "venv"
        
        # 플랫폼 정보
        self.system = platform.system()
        self.machine = platform.machine()
        
        # 빌드 설정
        self.build_configs = {
            'Windows': {
                'spec_file': 'build_config.spec',
                'output_name': 'StockMonitor.exe',
                'package_name': 'StockMonitor-Windows.zip'
            },
            'Darwin': {  # MacOS
                'spec_file': 'build_config.spec',
                'output_name': 'StockMonitor.app',
                'package_name': 'StockMonitor-MacOS.zip'
            },
            'Linux': {
                'spec_file': 'build_config.spec',
                'output_name': 'StockMonitor',
                'package_name': 'StockMonitor-Linux.zip'
            }
        }
    
    def print_banner(self):
        """배너 출력"""
        print("=" * 60)
        print("🚀 StockMonitor - 통합 빌드 및 패키징 시스템")
        print("=" * 60)
        print(f"시스템: {self.system} {self.machine}")
        print(f"프로젝트 경로: {self.project_root}")
        print("=" * 60)
    
    def check_requirements(self):
        """필수 요구사항 확인"""
        print("\n🔍 필수 요구사항 확인 중...")
        
        # Python 버전 확인
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 이상이 필요합니다.")
            return False
        
        # 가상환경 확인
        if not self.venv_dir.exists():
            print("❌ 가상환경을 찾을 수 없습니다.")
            print("   python3 -m venv venv 명령어로 생성해주세요.")
            return False
        
        # PyInstaller 확인
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__} 확인됨")
        except ImportError:
            print("❌ PyInstaller가 설치되지 않았습니다.")
            print("   pip install pyinstaller 명령어로 설치해주세요.")
            return False
        
        print("✅ 모든 요구사항이 충족되었습니다.")
        return True
    
    def activate_venv(self):
        """가상환경 활성화"""
        if self.system == "Windows":
            activate_script = self.venv_dir / "Scripts" / "activate.bat"
            if activate_script.exists():
                os.environ['VIRTUAL_ENV'] = str(self.venv_dir)
                os.environ['PATH'] = str(self.venv_dir / "Scripts") + os.pathsep + os.environ['PATH']
        else:
            activate_script = self.venv_dir / "bin" / "activate"
            if activate_script.exists():
                os.environ['VIRTUAL_ENV'] = str(self.venv_dir)
                os.environ['PATH'] = str(self.venv_dir / "bin") + os.pathsep + os.environ['PATH']
        
        print(f"✅ 가상환경 활성화됨: {self.venv_dir}")
    
    def clean_build_dirs(self):
        """빌드 디렉토리 정리"""
        print("\n🧹 빌드 디렉토리 정리 중...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   삭제됨: {dir_path}")
        
        print("✅ 빌드 디렉토리 정리 완료")
    
    def build_for_platform(self, platform_name):
        """특정 플랫폼용 빌드"""
        config = self.build_configs[platform_name]
        spec_file = self.project_root / config['spec_file']
        
        if not spec_file.exists():
            print(f"❌ {spec_file} 파일을 찾을 수 없습니다.")
            return False
        
        print(f"\n🔨 {platform_name}용 빌드 시작...")
        
        try:
            # PyInstaller 실행
            cmd = [
                sys.executable, "-m", "PyInstaller",
                str(spec_file),
                "--noconfirm"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print(f"✅ {platform_name} 빌드 성공!")
                return True
            else:
                print(f"❌ {platform_name} 빌드 실패:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ {platform_name} 빌드 중 오류 발생: {e}")
            return False
    
    def create_package(self, platform_name):
        """패키지 생성"""
        config = self.build_configs[platform_name]
        package_path = self.project_root / config['package_name']
        
        print(f"\n📦 {platform_name} 패키지 생성 중...")
        
        try:
            # 기존 패키지 삭제
            if package_path.exists():
                package_path.unlink()
            
            # ZIP 파일 생성
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if platform_name == "Darwin":
                    # MacOS .app 번들
                    app_dir = self.dist_dir / config['output_name']
                    if app_dir.exists():
                        for root, dirs, files in os.walk(app_dir):
                            for file in files:
                                file_path = Path(root) / file
                                arc_name = file_path.relative_to(self.dist_dir)
                                zipf.write(file_path, arc_name)
                                print(f"   추가됨: {arc_name}")
                else:
                    # Windows/Linux 실행 파일
                    exe_path = self.dist_dir / config['output_name']
                    if exe_path.exists():
                        zipf.write(exe_path, exe_path.name)
                        print(f"   추가됨: {exe_path.name}")
                    
                    # 추가 파일들
                    additional_files = ['README.md', 'INSTALL.md', 'email_setup_guide.md']
                    for file_name in additional_files:
                        file_path = self.project_root / file_name
                        if file_path.exists():
                            zipf.write(file_path, file_name)
                            print(f"   추가됨: {file_name}")
            
            # 파일 크기 표시
            size_mb = package_path.stat().st_size / (1024 * 1024)
            print(f"✅ 패키지 생성 완료: {package_path.name} ({size_mb:.1f} MB)")
            return True
            
        except Exception as e:
            print(f"❌ 패키지 생성 실패: {e}")
            return False
    
    def show_build_menu(self):
        """빌드 메뉴 표시"""
        print("\n🎯 빌드 옵션을 선택하세요:")
        print("1. 현재 시스템용 빌드")
        print("2. Windows용 빌드")
        print("3. MacOS용 빌드")
        print("4. Linux용 빌드")
        print("5. 모든 플랫폼용 빌드")
        print("6. 패키지만 생성 (기존 빌드 파일 사용)")
        print("0. 종료")
        
        while True:
            try:
                choice = input("\n선택 (0-6): ").strip()
                if choice in ['0', '1', '2', '3', '4', '5', '6']:
                    return choice
                else:
                    print("❌ 유효하지 않은 선택입니다. 0-6 중에서 선택해주세요.")
            except KeyboardInterrupt:
                print("\n\n👋 빌드를 취소했습니다.")
                sys.exit(0)
    
    def build_current_platform(self):
        """현재 플랫폼용 빌드"""
        if self.system == "Windows":
            return self.build_for_platform("Windows")
        elif self.system == "Darwin":
            return self.build_for_platform("Darwin")
        elif self.system == "Linux":
            return self.build_for_platform("Linux")
        else:
            print(f"❌ 지원되지 않는 플랫폼: {self.system}")
            return False
    
    def build_all_platforms(self):
        """모든 플랫폼용 빌드"""
        results = {}
        
        for platform_name in self.build_configs.keys():
            print(f"\n{'='*20} {platform_name} 빌드 {'='*20}")
            
            # 빌드 디렉토리 정리
            self.clean_build_dirs()
            
            # 빌드 실행
            success = self.build_for_platform(platform_name)
            results[platform_name] = success
            
            if success:
                # 패키지 생성
                self.create_package(platform_name)
            
            print(f"{'='*20} {platform_name} 완료 {'='*20}")
        
        return results
    
    def run(self):
        """메인 실행 함수"""
        self.print_banner()
        
        # 요구사항 확인
        if not self.check_requirements():
            print("\n❌ 빌드를 계속할 수 없습니다.")
            return
        
        # 가상환경 활성화
        self.activate_venv()
        
        while True:
            choice = self.show_build_menu()
            
            if choice == '0':
                print("\n👋 빌드를 종료합니다.")
                break
            
            elif choice == '1':
                print("\n🔨 현재 시스템용 빌드 시작...")
                self.clean_build_dirs()
                if self.build_current_platform():
                    self.create_package(self.system)
                else:
                    print("❌ 빌드에 실패했습니다.")
            
            elif choice == '2':
                print("\n🔨 Windows용 빌드 시작...")
                self.clean_build_dirs()
                if self.build_for_platform("Windows"):
                    self.create_package("Windows")
                else:
                    print("❌ Windows 빌드에 실패했습니다.")
            
            elif choice == '3':
                print("\n🔨 MacOS용 빌드 시작...")
                self.clean_build_dirs()
                if self.build_for_platform("Darwin"):
                    self.create_package("Darwin")
                else:
                    print("❌ MacOS 빌드에 실패했습니다.")
            
            elif choice == '4':
                print("\n🔨 Linux용 빌드 시작...")
                self.clean_build_dirs()
                if self.build_for_platform("Linux"):
                    self.create_package("Linux")
                else:
                    print("❌ Linux 빌드에 실패했습니다.")
            
            elif choice == '5':
                print("\n🔨 모든 플랫폼용 빌드 시작...")
                results = self.build_all_platforms()
                
                print("\n📊 빌드 결과 요약:")
                for platform_name, success in results.items():
                    status = "✅ 성공" if success else "❌ 실패"
                    print(f"  {platform_name}: {status}")
            
            elif choice == '6':
                print("\n📦 기존 빌드 파일로 패키지 생성...")
                if self.dist_dir.exists():
                    for platform_name in self.build_configs.keys():
                        self.create_package(platform_name)
                else:
                    print("❌ 빌드 파일이 없습니다. 먼저 빌드를 실행해주세요.")
            
            # 계속할지 확인
            if choice != '0':
                try:
                    input("\n계속하려면 Enter를 누르세요...")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 빌드를 종료합니다.")
                    break

if __name__ == "__main__":
    try:
        build_manager = BuildManager()
        build_manager.run()
    except KeyboardInterrupt:
        print("\n\n👋 빌드를 취소했습니다.")
    except EOFError:
        print("\n\n👋 입력이 종료되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)
