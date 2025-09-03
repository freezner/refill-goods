# 상품 재고 모니터링 시스템

도매 웹사이트의 상품 품절 상태를 체크하고 알림을 발송하는 Python 애플리케이션입니다.

## 주요 기능

- **🚀 간단한 설정**: 수신자 이메일만 입력하면 바로 사용 가능
- **📧 자동 이메일**: Gmail을 통한 자동 알림 발송 (별도 설정 불필요)
- **⏰ 자동 모니터링**: 설정한 간격(1분, 5분, 10분)마다 상품 상태 체크
- **🔍 상태 변화 감지**: 이전 상태와 비교하여 재고 상태 변화 시에만 알림 발송
- **📱 사용자 친화적 GUI**: 직관적이고 깔끔한 그래픽 인터페이스
- **🔌 확장 가능**: 새로운 웹사이트 지원을 위한 플러그인 구조

## 지원하는 웹사이트

- **오너클랜** (https://ownerclan.com/)
  - 재고 확인 방법: `.detail04` 클래스 내 `<select>` 태그의 "품절" 텍스트 감지
  - 품절 옵션명, 상품명, 페이지 링크를 이메일로 발송

## 설치 방법

### 방법 1: 실행 파일 다운로드 (권장)

#### Windows 사용자
1. 릴리즈 페이지에서 `StockMonitor-Windows.zip` 다운로드
2. 압축 해제 후 `StockMonitor.exe` 실행
3. 수신자 이메일 주소만 입력하면 바로 사용 가능!

#### MacOS 사용자
1. 릴리즈 페이지에서 `StockMonitor-MacOS.zip` 다운로드
2. 압축 해제 후 `StockMonitor` 실행
3. 보안 경고 시 "열기" 클릭
4. 수신자 이메일 주소만 입력하면 바로 사용 가능!

### 방법 2: 소스에서 빌드

#### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

#### 2. 환경 변수 설정

`env_example.txt` 파일을 참고하여 `.env` 파일을 생성하세요:

```bash
cp env_example.txt .env
```

`.env` 파일을 편집하여 이메일 설정을 입력하세요:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
DEFAULT_RECEIVER_EMAIL=receiver@example.com
```

**Gmail 사용 시 주의사항:**
1. 2단계 인증을 활성화하세요
2. 앱 비밀번호를 생성하여 `EMAIL_PASSWORD`에 입력하세요
3. 일반 비밀번호는 사용하지 마세요

## 사용 방법

### 1. 프로그램 실행

#### 실행 파일 사용 시
- Windows: `StockMonitor.exe` 더블클릭
- MacOS: `StockMonitor` 더블클릭

#### 소스에서 실행 시
```bash
python main.py
```

### 2. 이메일 설정 (간단!)

1. **수신자 이메일**: 알림을 받을 이메일 주소만 입력
2. **자동 설정**: Gmail을 통해 자동으로 발송 (별도 설정 불필요)
3. **연결 테스트**: "이메일 연결 테스트" 버튼으로 확인

> 💡 **팁**: Gmail 계정의 2단계 인증과 앱 비밀번호만 설정하면 끝!

### 3. URL 모니터링 설정

1. **상품 URL 입력**: 모니터링할 상품 페이지 URL 입력
2. **체크 간격 선택**: 1분, 5분, 10분 중 선택
3. **URL 추가**: "URL 추가" 버튼 클릭
4. **모니터링 시작**: "모니터링 시작" 버튼 클릭

### 4. 모니터링 관리

- **URL 추가/제거**: 모니터링할 상품 URL 관리
- **설정 저장/불러오기**: 현재 설정을 파일로 저장하고 불러오기
- **실시간 로그**: 모니터링 상태와 이벤트 로그 확인

## 프로젝트 구조

```
refill-goods/
├── main.py                  # 메인 실행 파일
├── gui.py                   # GUI 인터페이스
├── monitor.py               # 모니터링 시스템
├── stock_checker.py         # 재고 상태 체크
├── email_sender.py          # 이메일 발송
├── config.py                # 설정 관리
├── requirements.txt         # Python 패키지 의존성
├── env_example.txt          # 환경 변수 예시
├── build_config.spec        # PyInstaller 빌드 설정
├── build_windows.bat        # Windows 빌드 스크립트
├── build_macos.sh           # MacOS 빌드 스크립트
├── package_release.py       # 릴리즈 패키지 생성 스크립트
├── INSTALL.md               # 설치 가이드
└── README.md                # 프로젝트 설명서
```

## 기술 스택

- **Python 3.7+**: 메인 프로그래밍 언어
- **tkinter**: GUI 프레임워크
- **requests**: HTTP 요청 처리
- **BeautifulSoup4**: HTML 파싱
- **schedule**: 작업 스케줄링
- **python-dotenv**: 환경 변수 관리

## 패키징 및 배포

### 개발자를 위한 빌드 방법

#### Windows에서 빌드
```bash
# 방법 1: 배치 파일 사용
build_windows.bat

# 방법 2: 직접 명령어 실행
pyinstaller build_config.spec
```

#### MacOS에서 빌드
```bash
# 방법 1: 셸 스크립트 사용
./build_macos.sh

# 방법 2: 직접 명령어 실행
pyinstaller build_config.spec
```

#### 모든 플랫폼용 패키지 생성
```bash
python package_release.py
```

### 사용자를 위한 배포

빌드가 완료되면 다음 파일들이 생성됩니다:
- `dist/StockMonitor/StockMonitor.exe` (Windows)
- `dist/StockMonitor/StockMonitor` (MacOS)
- `StockMonitor-Windows.zip` (Windows 배포용)
- `StockMonitor-MacOS.zip` (MacOS 배포용)

## 확장 방법

새로운 웹사이트를 지원하려면:

1. `config.py`의 `SUPPORTED_WEBSITES`에 웹사이트 정보 추가
2. `stock_checker.py`의 `_extract_product_name`과 `_check_stock_availability` 메서드 수정
3. 해당 웹사이트의 HTML 구조에 맞는 선택자와 파싱 로직 구현

## 문제 해결

### 이메일 발송 실패
- SMTP 서버 설정 확인
- 이메일 계정의 2단계 인증 및 앱 비밀번호 설정 확인
- 방화벽이나 네트워크 설정 확인

### 웹사이트 접근 실패
- 인터넷 연결 상태 확인
- 웹사이트 서버 상태 확인
- User-Agent 설정 확인

### 모니터링이 작동하지 않음
- URL 형식 확인
- 체크 간격 설정 확인
- 로그 메시지 확인

## 라이선스

이 프로젝트는 개인 및 상업적 용도로 자유롭게 사용할 수 있습니다.

## 기여

버그 리포트나 기능 제안은 이슈로 등록해 주세요.
