# 🖥️ Intel Mac 호환성 가이드

## 📋 개요

이 가이드는 Intel Mac 사용자들이 StockMonitor 애플리케이션을 실행할 수 있도록 도와줍니다.

## 🔍 시스템 요구사항

- **MacOS 버전**: Ventura 13.7.x 이상
- **프로세서**: Intel x86_64 (Core i3/i5/i7/i9, Xeon 등)
- **메모리**: 최소 4GB RAM
- **저장공간**: 최소 100MB

## 🚀 설치 방법

### 방법 1: 미리 빌드된 실행 파일 사용 (권장)

1. **Apple Silicon Mac 사용자**: `StockMonitor-MacOS.zip` 다운로드
2. **Intel Mac 사용자**: `StockMonitor-Intel-MacOS.zip` 다운로드

### 방법 2: 소스에서 직접 빌드

#### Intel Mac에서 빌드하기

```bash
# 1. 저장소 클론
git clone <repository-url>
cd refill-goods

# 2. Python 가상환경 생성 (Python 3.11+ 권장)
python3 -m venv venv
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. Intel Mac용 빌드 스크립트 실행
./build_intel_macos.sh
```

#### Apple Silicon Mac에서 빌드하기

```bash
# 1. 저장소 클론
git clone <repository-url>
cd refill-goods

# 2. Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. Apple Silicon용 빌드 스크립트 실행
./build_macos_app.sh
```

## 🔧 빌드 스크립트 설명

### `build_intel_macos.sh`
- **용도**: Intel Mac 전용 .app 번들 생성
- **실행 환경**: Intel Mac에서만 실행 가능
- **출력**: `dist/StockMonitor.app` (Intel x86_64 바이너리)

### `build_macos_app.sh`
- **용도**: Apple Silicon Mac용 .app 번들 생성
- **실행 환경**: Apple Silicon Mac에서만 실행 가능
- **출력**: `dist/StockMonitor.app` (ARM64 바이너리)

## 📱 실행 방법

### .app 번들 실행
1. **Finder에서**: `StockMonitor.app` 더블클릭
2. **Applications 폴더**: 드래그하여 설치 후 실행
3. **Dock에 추가**: 아이콘을 Dock에 드래그

### 터미널에서 실행
```bash
# Apple Silicon Mac
open "dist/StockMonitor.app"

# Intel Mac
open "dist/StockMonitor.app"
```

## ⚠️ 주의사항

1. **아키텍처 불일치**: Intel Mac에서 Apple Silicon용 앱을 실행할 수 없음
2. **Rosetta 2**: Apple Silicon Mac에서 Intel 앱 실행 시 성능 저하 가능
3. **빌드 환경**: 각 아키텍처에 맞는 환경에서 빌드해야 함

## 🐛 문제 해결

### 일반적인 오류

#### "앱을 열 수 없습니다" 오류
```bash
# 보안 설정 확인
sudo spctl --master-disable

# 또는 System Preferences > Security & Privacy에서 허용
```

#### "손상된 앱" 오류
```bash
# 앱 검증 해제
xattr -cr "dist/StockMonitor.app"
```

#### "권한이 없습니다" 오류
```bash
# 실행 권한 부여
chmod +x "dist/StockMonitor.app/Contents/MacOS/StockMonitor"
```

### 빌드 오류

#### PyInstaller 오류
```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Tkinter 오류
```bash
# MacOS용 Tkinter 설치
brew install python-tk
```

## 📞 지원

문제가 발생하면 다음을 확인해주세요:

1. **시스템 정보**: `uname -m` 명령어로 아키텍처 확인
2. **MacOS 버전**: `sw_vers` 명령어로 버전 확인
3. **Python 버전**: `python3 --version` 명령어로 버전 확인
4. **로그 확인**: Console.app에서 오류 메시지 확인

## 🔄 업데이트

새로운 버전이 출시되면:

1. 저장소를 최신 상태로 업데이트
2. 의존성 재설치: `pip install -r requirements.txt`
3. 빌드 스크립트 재실행
4. 기존 .app 번들 교체

---

**💡 팁**: Intel Mac과 Apple Silicon Mac 모두에서 실행하려면 각각의 환경에서 빌드하여 두 버전을 모두 제공하는 것이 좋습니다.
