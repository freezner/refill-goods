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
            'base_url': 'https://ownerclan.com',
            'stock_check_selector': '.detail04 select option',
            'out_of_stock_text': '품절'
        }
    }
