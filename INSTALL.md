# 설치 가이드

## Windows 사용자

### 방법 1: 실행 파일 직접 다운로드 (권장)
1. 릴리즈 페이지에서 `StockMonitor-Windows.zip` 다운로드
2. 압축 해제 후 `StockMonitor.exe` 실행
3. 이메일 설정 완료 후 사용

### 방법 2: 소스에서 빌드
1. Python 3.7 이상 설치
2. `build_windows.bat` 더블클릭
3. 빌드 완료 후 `dist\StockMonitor\StockMonitor.exe` 실행

## MacOS 사용자

### 방법 1: 실행 파일 직접 다운로드 (권장)
1. 릴리즈 페이지에서 `StockMonitor-MacOS.zip` 다운로드
2. 압축 해제 후 `StockMonitor` 실행
3. 보안 경고 시 "열기" 클릭
4. 이메일 설정 완료 후 사용

### 방법 2: 소스에서 빌드
1. Python 3.7 이상 설치
2. 터미널에서 `./build_macos.sh` 실행
3. 빌드 완료 후 `dist/StockMonitor/StockMonitor` 실행

## Linux 사용자

### 소스에서 실행
```bash
# 의존성 설치
pip3 install -r requirements.txt

# 프로그램 실행
python3 main.py
```

## 이메일 설정

### Gmail 사용 시
1. Gmail 계정에서 2단계 인증 활성화
2. 앱 비밀번호 생성
3. 프로그램에서 다음 정보 입력:
   - SMTP 서버: `smtp.gmail.com`
   - 포트: `587`
   - 이메일: `your_email@gmail.com`
   - 비밀번호: `앱 비밀번호`
   - 수신자: `받을_이메일@example.com`

### 다른 이메일 제공업체
- SMTP 서버와 포트는 이메일 제공업체에 문의
- 일반적으로 포트 587 또는 465 사용

## 문제 해결

### Windows에서 실행되지 않는 경우
- Visual C++ 재배포 가능 패키지 설치
- Windows Defender에서 실행 파일 허용
- 관리자 권한으로 실행

### MacOS에서 실행되지 않는 경우
- 시스템 환경설정 > 보안 및 개인정보보호에서 "열기" 허용
- Gatekeeper 설정 확인
- 터미널에서 직접 실행 시도

### 이메일 발송 실패
- 이메일 계정 설정 확인
- 2단계 인증 및 앱 비밀번호 설정 확인
- 방화벽 설정 확인
- 네트워크 연결 상태 확인

## 시스템 요구사항

- **Windows**: Windows 10 이상 (64비트 권장)
- **MacOS**: macOS 10.14 이상
- **Linux**: Ubuntu 18.04 이상 또는 호환 배포판
- **Python**: 3.7 이상 (소스 빌드 시)
- **메모리**: 최소 512MB, 권장 1GB 이상
- **디스크 공간**: 최소 100MB

## 지원

문제가 발생하거나 질문이 있으시면:
1. README.md의 문제 해결 섹션 확인
2. GitHub 이슈 등록
3. 로그 파일 확인 (프로그램 내 로그 섹션)
