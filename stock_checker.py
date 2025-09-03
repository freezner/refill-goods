import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.previous_states = {}  # 이전 상태 저장
    
    def detect_website(self, url):
        """URL에서 지원하는 웹사이트를 감지합니다."""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        for website_name, website_config in Config.SUPPORTED_WEBSITES.items():
            if website_config['base_url'].lower() in domain:
                return website_name, website_config
        
        return None, None
    
    def check_stock_status(self, url):
        """상품의 품절 상태를 체크합니다."""
        try:
            website_name, website_config = self.detect_website(url)
            if not website_name:
                logger.error(f"지원하지 않는 웹사이트: {url}")
                return None
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 상품명 추출
            product_name = self._extract_product_name(soup, website_name)
            
            # 품절 상태 체크
            stock_status = self._check_stock_availability(soup, website_config)
            
            return {
                'url': url,
                'product_name': product_name,
                'stock_status': stock_status,
                'website': website_name,
                'timestamp': self._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"상품 상태 체크 중 오류 발생: {e}")
            return None
    
    def _extract_product_name(self, soup, website_name):
        """상품명을 추출합니다."""
        if website_name == 'ownerclan':
            # 오너클랜 상품명 추출 로직
            title_element = soup.find('h1') or soup.find('title')
            if title_element:
                return title_element.get_text(strip=True)
        
        return "상품명을 찾을 수 없습니다"
    
    def _check_stock_availability(self, soup, website_config):
        """품절 상태를 체크합니다."""
        stock_status = {
            'is_available': True,
            'out_of_stock_options': [],
            'all_options': []
        }
        
        # .detail04 클래스 내의 select 옵션들을 찾습니다
        detail04 = soup.find('div', class_='detail04')
        if not detail04:
            return stock_status
        
        select_elements = detail04.find_all('select')
        
        for select in select_elements:
            options = select.find_all('option')
            for option in options:
                option_text = option.get_text(strip=True)
                if option_text:
                    stock_status['all_options'].append(option_text)
                    
                    # 품절 옵션 체크
                    if website_config['out_of_stock_text'] in option_text:
                        stock_status['is_available'] = False
                        stock_status['out_of_stock_options'].append(option_text)
        
        return stock_status
    
    def _get_current_timestamp(self):
        """현재 타임스탬프를 반환합니다."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def has_stock_changed(self, url, current_status):
        """이전 상태와 비교하여 재고 상태 변화를 감지합니다."""
        if url not in self.previous_states:
            # 첫 번째 체크
            self.previous_states[url] = current_status
            return False
        
        previous_status = self.previous_states[url]
        
        # 재고 상태 변화 감지
        if (previous_status['stock_status']['is_available'] != 
            current_status['stock_status']['is_available']):
            return True
        
        # 품절 옵션 변화 감지
        previous_out_of_stock = set(previous_status['stock_status']['out_of_stock_options'])
        current_out_of_stock = set(current_status['stock_status']['out_of_stock_options'])
        
        if previous_out_of_stock != current_out_of_stock:
            return True
        
        # 상태 업데이트
        self.previous_states[url] = current_status
        return False
