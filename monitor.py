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
        self.last_check_time = None
        self.next_check_time = None
        self.log_callback = None  # GUI에서 로그를 받을 콜백 함수
    
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
        
        # GUI 로그 콜백 호출
        if self.log_callback:
            self.log_callback("INFO", f"URL 추가됨: {url} (간격: {interval_minutes}분)")
        
        return True
    
    def remove_url(self, url):
        """모니터링에서 URL을 제거합니다."""
        if url in self.monitored_urls:
            del self.monitored_urls[url]
            logger.info(f"URL 제거됨: {url}")
            
            # GUI 로그 콜백 호출
            if self.log_callback:
                self.log_callback("INFO", f"URL 제거됨: {url}")
            
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
        
        # GUI 로그 콜백 호출
        if self.log_callback:
            self.log_callback("INFO", "모니터링이 시작되었습니다.")
            self.log_callback("INFO", f"모니터링 URL 수: {len(self.monitored_urls)}")
    
    def stop_monitoring(self):
        """모니터링을 중지합니다."""
        if not self.is_running:
            return
        
        self.is_running = False
        schedule.clear()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        logger.info("모니터링이 중지되었습니다.")
        
        # GUI 로그 콜백 호출
        if self.log_callback:
            self.log_callback("INFO", "모니터링이 중지되었습니다.")
    
    def _run_scheduler(self):
        """스케줄러를 실행합니다."""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def _check_url(self, url):
        """특정 URL의 재고 상태를 체크합니다."""
        try:
            # 마지막 체크 시간 업데이트
            self.last_check_time = datetime.now()
            
            logger.info(f"URL 체크 중: {url}")
            
            # GUI 로그 콜백 호출
            if self.log_callback:
                self.log_callback("INFO", f"URL 체크 중: {url}")
            
            # 재고 상태 체크
            current_status = self.stock_checker.check_stock_status(url)
            if not current_status:
                logger.error(f"상태 체크 실패: {url}")
                if self.log_callback:
                    self.log_callback("ERROR", f"상태 체크 실패: {url}")
                return
            
            # 상품 정보 로그 출력
            self._log_product_status(current_status)
            
            # 상태 변화 감지
            if self.stock_checker.has_stock_changed(url, current_status):
                logger.info(f"재고 상태 변화 감지: {url}")
                
                # GUI 로그 콜백 호출
                if self.log_callback:
                    self.log_callback("WARNING", f"재고 상태 변화 감지: {url}")
                
                # 이메일 알림 발송 (변동 알림)
                receiver_email = self.monitored_urls[url]['receiver_email']
                
                # 이전 상태 정보 추가
                if url in self.stock_checker.previous_states:
                    current_status['previous_status'] = self.stock_checker.previous_states[url]['stock_status']
                
                if self.email_sender.send_stock_notification(receiver_email, current_status, "change"):
                    logger.info(f"재고 변동 알림 이메일 발송 완료: {url}")
                    if self.log_callback:
                        self.log_callback("INFO", f"재고 변동 알림 이메일 발송 완료: {url}")
                else:
                    logger.error(f"재고 변동 알림 이메일 발송 실패: {url}")
                    if self.log_callback:
                        self.log_callback("ERROR", f"재고 변동 알림 이메일 발송 실패: {url}")
            else:
                logger.info(f"재고 상태 변화 없음: {url}")
                if self.log_callback:
                    self.log_callback("INFO", f"재고 상태 변화 없음: {url}")
                
                # 첫 번째 체크인 경우 초기 상태 이메일 발송
                if url not in self.stock_checker.previous_states:
                    receiver_email = self.monitored_urls[url]['receiver_email']
                    if self.email_sender.send_stock_notification(receiver_email, current_status, "initial"):
                        logger.info(f"초기 재고 상태 이메일 발송 완료: {url}")
                        if self.log_callback:
                            self.log_callback("INFO", f"초기 재고 상태 이메일 발송 완료: {url}")
                    else:
                        logger.error(f"초기 재고 상태 이메일 발송 실패: {url}")
                        if self.log_callback:
                            self.log_callback("ERROR", f"초기 재고 상태 이메일 발송 실패: {url}")
            
            # 마지막 체크 시간 업데이트
            self.monitored_urls[url]['last_check'] = datetime.now()
            self.monitored_urls[url]['status'] = current_status
            
        except Exception as e:
            logger.error(f"URL 체크 중 오류 발생: {url}, 오류: {e}")
            if self.log_callback:
                self.log_callback("ERROR", f"URL 체크 중 오류 발생: {url}, 오류: {e}")
    
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
    
    def _log_product_status(self, status):
        """상품 상태 정보를 로그에 출력합니다."""
        try:
            if not status:
                return
            
            # 기본 정보 로그
            if self.log_callback:
                self.log_callback("INFO", f"상품명: {status.get('product_name', '알 수 없음')}")
                
                # 재고 상태 요약
                if status.get('stock_status', {}).get('is_available', True):
                    self.log_callback("INFO", "✅ 재고 있음")
                else:
                    self.log_callback("WARNING", "❌ 재고 부족 (품절 옵션 존재)")
                
                # 2계층 옵션 정보 출력
                option_levels = status.get('stock_status', {}).get('option_levels', {})
                if option_levels:
                    self.log_callback("INFO", "📋 옵션 정보:")
                    
                    for level_name, level_info in option_levels.items():
                        level_display = "옵션1" if level_name == "option1" else "옵션2"
                        total_count = level_info.get('total_count', 0)
                        self.log_callback("INFO", f"  {level_display}: 총 {total_count}개")
                        
                        # 품절 옵션 강조
                        for option in level_info.get('options', []):
                            option_text = option['text']
                            if '품절' in option_text:
                                self.log_callback("WARNING", f"    ❌ 품절: {option_text}")
                            else:
                                self.log_callback("INFO", f"    ✅ 재고: {option_text}")
                
                # 품절 옵션 요약
                out_of_stock = status.get('stock_status', {}).get('out_of_stock_options', [])
                if out_of_stock:
                    self.log_callback("WARNING", f"🚫 품절 옵션 ({len(out_of_stock)}개):")
                    for option in out_of_stock:
                        self.log_callback("WARNING", f"  - {option}")
                
        except Exception as e:
            logger.error(f"상품 상태 로그 출력 중 오류: {e}")
            if self.log_callback:
                self.log_callback("ERROR", f"상품 상태 로그 출력 중 오류: {e}")
