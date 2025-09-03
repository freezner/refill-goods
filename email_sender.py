import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_user = Config.EMAIL_USER
        self.email_password = Config.EMAIL_PASSWORD
    
    def send_stock_notification(self, receiver_email, stock_info):
        """재고 상태 변화 알림을 이메일로 발송합니다."""
        try:
            # 이메일 설정이 완료되지 않은 경우
            if not self.email_user or not self.email_password:
                logger.error("이메일 설정이 완료되지 않았습니다.")
                return False
            
            # 이메일 내용 구성
            subject = f"[재고 알림] {stock_info['product_name']} 재고 상태 변화"
            
            # 이메일 본문 구성
            body = self._create_email_body(stock_info)
            
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = receiver_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 이메일 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"재고 알림 이메일을 {receiver_email}로 발송했습니다.")
            return True
            
        except Exception as e:
            logger.error(f"이메일 발송 중 오류 발생: {e}")
            return False
    
    def _create_email_body(self, stock_info):
        """이메일 본문을 생성합니다."""
        body = f"""
재고 상태 변화 알림

상품명: {stock_info['product_name']}
웹사이트: {stock_info['website']}
체크 시간: {stock_info['timestamp']}
상품 링크: {stock_info['url']}

재고 상태:
"""
        
        if stock_info['stock_status']['is_available']:
            body += "✅ 모든 옵션이 재고에 있습니다.\n\n"
        else:
            body += "❌ 일부 옵션이 품절입니다.\n\n"
            body += "품절된 옵션:\n"
            for option in stock_info['stock_status']['out_of_stock_options']:
                body += f"- {option}\n"
            body += "\n"
        
        body += "전체 옵션:\n"
        for option in stock_info['stock_status']['all_options']:
            if option in stock_info['stock_status']['out_of_stock_options']:
                body += f"❌ {option} (품절)\n"
            else:
                body += f"✅ {option}\n"
        
        body += "\n\n이 메일은 자동으로 발송되었습니다."
        return body
    
    def test_email_connection(self):
        """이메일 연결을 테스트합니다."""
        try:
            if not self.email_user or not self.email_password:
                return False, "이메일 계정 정보가 설정되지 않았습니다."
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
            
            return True, "이메일 연결 테스트가 성공했습니다."
            
        except Exception as e:
            return False, f"이메일 연결 테스트 실패: {e}"
