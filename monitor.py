import schedule
import time
import threading
from datetime import datetime
from stock_checker import StockChecker
from email_sender import EmailSender
from config import Config
import logging

logger = logging.getLogger(__name__)

class StockMonitor:
    def __init__(self):
        self.stock_checker = StockChecker()
        self.email_sender = EmailSender()
        self.monitored_urls = {}  # {url: {'interval': minutes, 'receiver_email': email}}
        self.is_running = False
        self.monitor_thread = None
    
    def add_url(self, url, interval_minutes, receiver_email):
        """모니터링할 URL을 추가합니다."""
        if not self._validate_url(url):
            logger.error(f"유효하지 않은 URL: {url}")
            return False
        
        self.monitored_urls[url] = {
            'interval': interval_minutes,
            'receiver_email': receiver_email,
            'last_check': None,
            'status': None
        }
        
        logger.info(f"URL 추가됨: {url} (간격: {interval_minutes}분)")
        return True
    
    def remove_url(self, url):
        """모니터링에서 URL을 제거합니다."""
        if url in self.monitored_urls:
            del self.monitored_urls[url]
            logger.info(f"URL 제거됨: {url}")
            return True
        return False
    
    def start_monitoring(self):
        """모니터링을 시작합니다."""
        if self.is_running:
            logger.warning("모니터링이 이미 실행 중입니다.")
            return
        
        self.is_running = True
        
        # 각 URL에 대해 스케줄 설정
        for url, config in self.monitored_urls.items():
            interval = config['interval']
            schedule.every(interval).minutes.do(self._check_url, url)
        
        # 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.monitor_thread.start()
        
        logger.info("모니터링이 시작되었습니다.")
    
    def stop_monitoring(self):
        """모니터링을 중지합니다."""
        if not self.is_running:
            return
        
        self.is_running = False
        schedule.clear()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        logger.info("모니터링이 중지되었습니다.")
    
    def _run_scheduler(self):
        """스케줄러를 실행합니다."""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def _check_url(self, url):
        """특정 URL의 재고 상태를 체크합니다."""
        try:
            logger.info(f"URL 체크 중: {url}")
            
            # 재고 상태 체크
            current_status = self.stock_checker.check_stock_status(url)
            if not current_status:
                logger.error(f"상태 체크 실패: {url}")
                return
            
            # 상태 변화 감지
            if self.stock_checker.has_stock_changed(url, current_status):
                logger.info(f"재고 상태 변화 감지: {url}")
                
                # 이메일 알림 발송
                receiver_email = self.monitored_urls[url]['receiver_email']
                if self.email_sender.send_stock_notification(receiver_email, current_status):
                    logger.info(f"재고 알림 이메일 발송 완료: {url}")
                else:
                    logger.error(f"재고 알림 이메일 발송 실패: {url}")
            else:
                logger.info(f"재고 상태 변화 없음: {url}")
            
            # 마지막 체크 시간 업데이트
            self.monitored_urls[url]['last_check'] = datetime.now()
            self.monitored_urls[url]['status'] = current_status
            
        except Exception as e:
            logger.error(f"URL 체크 중 오류 발생: {url}, 오류: {e}")
    
    def _validate_url(self, url):
        """URL 유효성을 검사합니다."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except:
            return False
    
    def get_monitoring_status(self):
        """현재 모니터링 상태를 반환합니다."""
        return {
            'is_running': self.is_running,
            'monitored_urls': self.monitored_urls,
            'total_urls': len(self.monitored_urls)
        }
    
    def manual_check(self, url):
        """수동으로 URL을 체크합니다."""
        if url not in self.monitored_urls:
            logger.error(f"모니터링되지 않는 URL: {url}")
            return None
        
        self._check_url(url)
        return self.monitored_urls[url]['status']
