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
    
    def send_stock_notification(self, receiver_email, stock_info, email_type="initial"):
        """재고 상태 알림을 이메일로 발송합니다.
        
        Args:
            receiver_email: 수신자 이메일
            stock_info: 재고 정보
            email_type: 이메일 유형 ("initial", "change", "status")
        """
        try:
            # 이메일 설정이 완료되지 않은 경우
            if not self.email_user or not self.email_password:
                logger.error("이메일 설정이 완료되지 않았습니다.")
                return False
            
            # 이메일 유형에 따른 제목과 본문 구성
            if email_type == "initial":
                subject = f"[재고 모니터링 시작] {stock_info['product_name']} 재고 상태"
            elif email_type == "change":
                subject = f"[재고 변동 알림] {stock_info['product_name']} 재고 상태 변화"
            else:
                subject = f"[재고 상태 알림] {stock_info['product_name']} 재고 현황"
            
            # 이메일 본문 구성
            body = self._create_email_body(stock_info, email_type)
            
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
            
            logger.info(f"재고 알림 이메일을 {receiver_email}로 발송했습니다. (유형: {email_type})")
            return True
            
        except Exception as e:
            logger.error(f"이메일 발송 중 오류 발생: {e}")
            return False
    
    def _create_email_body(self, stock_info, email_type="initial"):
        """이메일 본문을 생성합니다."""
        body = f"""
{'='*50}
재고 모니터링 시스템 알림
{'='*50}

상품명: {stock_info['product_name']}
웹사이트: {stock_info['website']}
체크 시간: {stock_info['timestamp']}
상품 링크: {stock_info['url']}

재고 요약: {stock_info['stock_status']['all_options'].__len__()}개 옵션 중 {stock_info['stock_status']['out_of_stock_options'].__len__()}개 품절

"""
        
        # 이메일 유형에 따른 메시지 구성
        if email_type == "initial":
            body += self._create_initial_status_message(stock_info)
        elif email_type == "change":
            body += self._create_change_notification_message(stock_info)
        else:
            body += self._create_status_message(stock_info)
        
        body += f"""
{'='*50}
이 메일은 자동으로 발송되었습니다.
{'='*50}"""
        return body
    
    def _create_initial_status_message(self, stock_info):
        """초기 상태 메시지를 생성합니다."""
        stock_status = stock_info['stock_status']
        
        if stock_status['is_available']:
            message = f"✅ {stock_info['product_name']} 상품 재고 이상 없습니다.\n\n"
        else:
            message += f"⚠️ {stock_info['product_name']} 상품 일부 재고가 없습니다.\n\n"
            message += "품절된 옵션:\n"
            for option in stock_status['out_of_stock_options']:
                message += f"  ❌ {option}\n"
            message += "\n"
        
        return message
    
    def _create_change_notification_message(self, stock_info):
        """재고 변동 알림 메시지를 생성합니다."""
        message = f"🔄 {stock_info['product_name']} 상품의 재고 변동이 발생했습니다.\n\n"
        
        # 이전 상태와 현재 상태 비교 정보 추가
        if 'previous_status' in stock_info:
            message += "변동 전 품절 옵션:\n"
            for option in stock_info['previous_status']['out_of_stock_options']:
                message += f"  ❌ {option}\n"
            message += "\n"
        
        message += "현재 품절 옵션:\n"
        stock_status = stock_info['stock_status']
        for option in stock_status['out_of_stock_options']:
            message += f"  ❌ {option}\n"
        
        return message
    
    def _create_status_message(self, stock_info):
        """일반 상태 메시지를 생성합니다."""
        return self._create_initial_status_message(stock_info)
    
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
