# 🚀 StockMonitor - 통합 빌드 및 패키징 가이드

## 📋 개요

이 가이드는 StockMonitor 애플리케이션을 다양한 플랫폼용으로 빌드하고 패키징하는 방법을 설명합니다.

## 🎯 지원 플랫폼

- **Windows**: `.exe` 실행 파일
- **MacOS**: `.app` 번들 (Intel + Apple Silicon 호환)
- **Linux**: 실행 파일

## 🛠️ 빌드 방법

### **방법 1: 통합 빌드 시스템 (권장)**

#### **대화형 빌드**
```bash
# 가상환경 활성화
source venv/bin/activate  # MacOS/Linux
# 또는
venv\Scripts\activate.bat  # Windows

# 통합 빌드 시스템 실행
python build_all.py
```

**빌드 옵션:**
1. **현재 시스템용 빌드** - 현재 OS에 맞는 실행 파일 생성
2. **Windows용 빌드** - Windows .exe 파일 생성
3. **MacOS용 빌드** - MacOS .app 번들 생성
4. **Linux용 빌드** - Linux 실행 파일 생성
5. **모든 플랫폼용 빌드** - 모든 플랫폼용 파일 생성
6. **패키지만 생성** - 기존 빌드 파일로 ZIP 패키지 생성

#### **빠른 빌드**
```bash
# 현재 시스템용
python quick_build.py current

# MacOS용
python quick_build.py macos

# Windows용
python quick_build.py windows

# Linux용
python quick_build.py linux

# 모든 플랫폼용
python quick_build.py all
```

### **방법 2: 플랫폼별 스크립트**

#### **MacOS용**
```bash
# Apple Silicon Mac용 .app 번들
./build_macos_app.sh

# Intel Mac용 .app 번들 (Intel Mac에서 실행)
./build_intel_macos.sh
```

#### **Windows용**
```bash
# Windows용 .exe 파일
build_windows.bat
```

#### **Unix/Linux/MacOS용**
```bash
# Unix 계열 시스템용
./build.sh
```

## 📦 생성되는 파일들

### **빌드 결과물**
- `dist/StockMonitor/` - Windows/Linux 실행 파일
- `dist/StockMonitor.app/` - MacOS .app 번들

### **패키지 파일**
- `StockMonitor-Windows.zip` - Windows 배포용
- `StockMonitor-MacOS.zip` - MacOS 배포용
- `StockMonitor-Linux.zip` - Linux 배포용

## 🔧 사전 요구사항

### **1. Python 환경**
```bash
# Python 3.8+ 설치 확인
python3 --version

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # MacOS/Linux
# 또는
venv\Scripts\activate.bat  # Windows
```

### **2. 의존성 설치**
```bash
# 필수 패키지 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install pyinstaller pillow requests beautifulsoup4 schedule python-dotenv
```

### **3. MacOS 특별 요구사항**
```bash
# Tkinter 지원 Python 설치 (Homebrew)
brew install python-tk

# 또는 시스템 Python 사용
python3 -c "import tkinter; print('Tkinter OK')"
```

## 🚀 빌드 프로세스

### **1. 환경 확인**
```bash
# 가상환경 활성화
source venv/bin/activate

# PyInstaller 확인
python -c "import PyInstaller; print('PyInstaller OK')"
```

### **2. 빌드 실행**
```bash
# 대화형 빌드
python build_all.py

# 또는 빠른 빌드
python quick_build.py macos
```

### **3. 결과 확인**
```bash
# 생성된 파일 확인
ls -la dist/

# MacOS .app 번들 테스트
open "dist/StockMonitor.app"

# Windows .exe 파일 테스트
# dist/StockMonitor.exe
```

## 🔍 문제 해결

### **일반적인 오류**

#### **"PyInstaller를 찾을 수 없습니다"**
```bash
pip install pyinstaller
```

#### **"Tkinter를 찾을 수 없습니다" (MacOS)**
```bash
brew install python-tk
```

#### **"가상환경을 찾을 수 없습니다"**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **빌드 실패**
```bash
# 빌드 디렉토리 정리
rm -rf build dist

# 의존성 재설치
pip install --upgrade -r requirements.txt

# 다시 빌드
python build_all.py
```

### **플랫폼별 문제**

#### **MacOS**
- **Apple Silicon**: `build_macos_app.sh` 사용
- **Intel**: `build_intel_macos.sh` 사용 (Intel Mac에서 실행)
- **권한 오류**: `chmod +x *.sh` 실행

#### **Windows**
- **PowerShell 정책**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **경로 문제**: `build.bat` 사용

#### **Linux**
- **Tkinter**: `sudo apt-get install python3-tk` (Ubuntu/Debian)
- **권한**: `chmod +x *.sh` 실행

## 📊 빌드 성능 최적화

### **1. 병렬 빌드**
```bash
# 모든 플랫폼 동시 빌드 (메모리 사용량 주의)
python build_all.py
# 옵션 5 선택
```

### **2. 캐시 활용**
```bash
# 빌드 디렉토리 유지 (재빌드 시 빠름)
# build/ 디렉토리 삭제하지 않음
```

### **3. 의존성 최적화**
```bash
# 불필요한 패키지 제거
pip uninstall unused-package

# 가상환경 정리
pip cache purge
```

## 🎯 배포 전략

### **1. 단일 플랫폼 배포**
```bash
# MacOS만
python quick_build.py macos

# Windows만
python quick_build.py windows
```

### **2. 크로스 플랫폼 배포**
```bash
# 모든 플랫폼
python quick_build.py all

# 또는 대화형으로
python build_all.py
# 옵션 5 선택
```

### **3. CI/CD 통합**
```bash
# 자동화된 빌드
python quick_build.py current

# 결과 확인
ls -la *.zip
```

## 💡 팁과 모범 사례

### **1. 빌드 전 체크리스트**
- [ ] 가상환경 활성화됨
- [ ] PyInstaller 설치됨
- [ ] 모든 의존성 설치됨
- [ ] 충분한 디스크 공간
- [ ] 네트워크 연결 (첫 빌드 시)

### **2. 빌드 후 체크리스트**
- [ ] 실행 파일 생성됨
- [ ] 패키지 파일 생성됨
- [ ] 실행 테스트 완료
- [ ] 파일 크기 적절함
- [ ] 아키텍처 확인됨

### **3. 성능 최적화**
- **빈도**: 자주 변경되지 않는 코드는 캐시 활용
- **의존성**: 최소한의 패키지만 포함
- **아이콘**: 적절한 크기의 아이콘 사용
- **메모리**: 대용량 빌드 시 충분한 RAM 확보

## 🔄 업데이트 및 유지보수

### **1. 정기 업데이트**
```bash
# 의존성 업데이트
pip install --upgrade -r requirements.txt

# PyInstaller 업데이트
pip install --upgrade pyinstaller
```

### **2. 빌드 스크립트 업데이트**
```bash
# 최신 버전 확인
git pull origin main

# 빌드 스크립트 권한 갱신
chmod +x *.sh *.py
```

### **3. 문제 보고**
빌드 문제가 발생하면 다음 정보를 포함하여 보고:
- OS 및 버전
- Python 버전
- 오류 메시지
- 빌드 로그
- 시스템 정보

---

**🚀 이제 StockMonitor를 쉽고 빠르게 빌드할 수 있습니다!**

**💡 권장사항**: 처음에는 `python build_all.py`로 대화형 빌드를 사용하고, 익숙해지면 `python quick_build.py [platform]`으로 빠른 빌드를 사용하세요.
