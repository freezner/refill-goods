import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 이메일 설정 (Gmail 기본값)
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_USER = 'freezner3@gmail.com'  # 기본 발신자 이메일
    EMAIL_PASSWORD = 'cdxc uuvz sclg ekru'   # 앱 비밀번호 필요
    
    # 기본 설정
    DEFAULT_INTERVAL = 5  # 기본 체크 간격 (분)
    DEFAULT_RECEIVER_EMAIL = ''  # 사용자가 입력할 수신자 이메일
    
    # 웹사이트 설정
    SUPPORTED_WEBSITES = {
        'ownerclan': {
            'base_url': 'ownerclan.com',  # https:// 제거하여 도메인만 매칭
            'url_patterns': [  # 여러 URL 패턴 지원
                'ownerclan.com',
                'www.ownerclan.com',
                'https://ownerclan.com',
                'https://www.ownerclan.com'
            ],
            'stock_check_selector': '.detail04 select option',
            'out_of_stock_text': '품절',
            'multi_level_options': True,  # 2계층 옵션 지원
            'option1_selector': '#option1',  # 첫 번째 옵션 선택자
            'option2_selector': '#option2',  # 두 번째 옵션 선택자
            'stock_status_selector': 'option',  # 품절 상태 확인할 옵션 요소
            'stock_check_method': 'multi_level'  # 다계층 옵션 체크 방법
        }
    }
