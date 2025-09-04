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
        
        logger.info(f"URL 감지 시도: {url}")
        logger.info(f"도메인: {domain}")
        
        for website_name, website_config in Config.SUPPORTED_WEBSITES.items():
            # 기본 base_url 검사
            base_url = website_config['base_url'].lower()
            logger.info(f"웹사이트 '{website_name}' 검사: base_url='{base_url}' vs domain='{domain}'")
            
            if base_url in domain:
                logger.info(f"웹사이트 감지 성공: {website_name}")
                return website_name, website_config
            
            # url_patterns가 있으면 추가 검사
            if 'url_patterns' in website_config:
                for pattern in website_config['url_patterns']:
                    pattern_lower = pattern.lower()
                    logger.info(f"  패턴 검사: '{pattern_lower}' vs domain='{domain}'")
                    
                    if pattern_lower in domain:
                        logger.info(f"웹사이트 감지 성공 (패턴): {website_name} - '{pattern}'")
                        return website_name, website_config
        
        logger.error(f"지원하지 않는 웹사이트: {url} (도메인: {domain})")
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
            stock_status = self._check_stock_availability(soup, website_config, url)
            
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
    
    def _check_stock_availability(self, soup, website_config, url):
        """품절 상태를 체크합니다."""
        stock_status = {
            'is_available': True,
            'out_of_stock_options': [],
            'all_options': [],
            'option_levels': {}
        }
        
        # 다계층 옵션 지원 여부 확인
        if website_config.get('multi_level_options', False):
            return self._check_multi_level_stock(soup, website_config, stock_status, url)
        else:
            return self._check_single_level_stock(soup, website_config, stock_status)
    
    def _check_multi_level_stock(self, soup, website_config, stock_status, url):
        """다계층 옵션의 품절 상태를 순차적으로 체크합니다."""
        try:
            stock_status['option_levels'] = {}
            all_options = []
            out_of_stock_options = []
            
            # 첫 번째 옵션 선택자로 옵션1 찾기
            option1_element = soup.select_one(website_config.get('option1_selector', '#option1'))
            if option1_element:
                option1_info = self._extract_option_info(option1_element)
                stock_status['option_levels']['option1'] = option1_info
                
                logger.info(f"옵션1 선택자 '{website_config.get('option1_selector', '#option1')}'로 {option1_info['total_count']}개 옵션 발견")
                
                # 디버깅: 페이지의 모든 select 요소 확인
                all_selects = soup.find_all('select')
                logger.info(f"페이지에서 발견된 select 요소들: {[select.get('id', select.get('name', 'unnamed')) for select in all_selects]}")
                
                # 디버깅: 모든 select 요소의 id와 name 속성 상세 확인
                for i, select in enumerate(all_selects):
                    select_id = select.get('id', 'no-id')
                    select_name = select.get('name', 'no-name')
                    select_class = select.get('class', [])
                    logger.info(f"  Select {i+1}: id='{select_id}', name='{select_name}', class='{select_class}'")
                    
                    # 각 select의 첫 번째 옵션 텍스트도 확인
                    first_option = select.find('option')
                    if first_option:
                        logger.info(f"    첫 번째 옵션: '{first_option.get_text(strip=True)}'")
                
                # 디버깅: 옵션2 선택자로 찾을 수 있는 요소들 확인
                option2_candidates = soup.select(website_config.get('option2_selector', '#option2'))
                logger.info(f"옵션2 선택자 '{website_config.get('option2_selector', '#option2')}'로 {len(option2_candidates)}개 요소 발견")
                
                # 옵션1의 각 선택지에 대해 순차적으로 체크
                for option1 in option1_info['options']:
                    option1_text = option1['text']
                    all_options.append(f"option1: {option1_text}")
                    
                    logger.info(f"옵션1 체크 중: {option1_text}")
                    
                    # 옵션1이 품절인지 체크
                    if website_config['out_of_stock_text'] in option1_text:
                        logger.warning(f"옵션1 품절 발견: {option1_text}")
                        stock_status['is_available'] = False
                        out_of_stock_options.append(f"option1: {option1_text}")
                        continue  # 옵션1이 품절이면 옵션2 체크하지 않음
                    
                    logger.info(f"옵션1 '{option1_text}' 선택 후 옵션2 체크 시작")
                    
                    # 옵션1 선택 후 옵션2 체크
                    if url:
                        option2_status = self._check_option2_for_option1(
                            soup, website_config, option1, stock_status, url
                        )
                    else:
                        # URL이 없으면 정적 파싱만 수행
                        logger.warning(f"    └─ URL이 제공되지 않아 정적 파싱만 수행합니다.")
                        option2_status = self._check_option2_static(soup, website_config, option1, stock_status)
                    
                    # 옵션2 결과를 전체 옵션에 추가
                    all_options.extend(option2_status['all_options'])
                    out_of_stock_options.extend(option2_status['out_of_stock_options'])
                    
                    # 옵션2에 품절이 있으면 전체 재고 상태 업데이트
                    if option2_status['out_of_stock_options']:
                        logger.warning(f"옵션2 품절 발견 (옵션1: {option1_text}): {option2_status['out_of_stock_options']}")
                        stock_status['is_available'] = False
            
            stock_status['all_options'] = all_options
            stock_status['out_of_stock_options'] = out_of_stock_options
            
            return stock_status
            
        except Exception as e:
            logger.error(f"다계층 옵션 체크 중 오류: {e}")
            # 예외 발생 시 단일 레벨 체크로 폴백
            return self._check_single_level_stock(soup, website_config, stock_status)
    
    def _check_option2_for_option1(self, soup, website_config, option1, stock_status, url):
        """특정 옵션1에 대한 옵션2를 체크합니다."""
        try:
            option2_status = {
                'all_options': [],
                'out_of_stock_options': []
            }
            
            logger.info(f"  └─ 옵션2 선택자 '{website_config.get('option2_selector', '#option2')}'로 옵션2 탐색 중...")
            
            # 옵션1 선택을 시뮬레이션하여 옵션2 업데이트
            updated_soup = self._simulate_option1_selection(soup, website_config, option1, url)
            
            # 업데이트된 페이지에서 옵션2 찾기
            option2_element = updated_soup.select_one(website_config.get('option2_selector', '#option2'))
            if not option2_element:
                logger.warning(f"  └─ 옵션2 요소를 찾을 수 없음: {website_config.get('option2_selector', '#option2')}")
                return option2_status
            
            logger.info(f"  └─ 옵션2 요소 발견, 옵션 정보 추출 중...")
            
            # 옵션2 정보 추출
            option2_info = self._extract_option_info(option2_element)
            logger.info(f"  └─ 옵션2 총 {option2_info['total_count']}개 발견")
            
            # 옵션2의 각 선택지 체크
            for option2 in option2_info['options']:
                option2_text = option2['text']
                combined_option = f"option1: {option1['text']} + option2: {option2_text}"
                option2_status['all_options'].append(combined_option)
                
                logger.info(f"    └─ 옵션2 체크 중: {option2_text}")
                
                # 옵션2가 품절인지 체크
                if website_config['out_of_stock_text'] in option2_text:
                    logger.warning(f"    └─ 옵션2 품절 발견: {option2_text}")
                    option2_status['out_of_stock_options'].append(combined_option)
                else:
                    logger.info(f"    └─ 옵션2 재고 있음: {option2_text}")
            
            logger.info(f"  └─ 옵션2 체크 완료: {len(option2_status['all_options'])}개 옵션, {len(option2_status['out_of_stock_options'])}개 품절")
            return option2_status
            
        except Exception as e:
            logger.error(f"옵션2 체크 중 오류: {e}")
            return {'all_options': [], 'out_of_stock_options': []}
    
    def _simulate_option1_selection(self, soup, website_config, option1, url):
        """옵션1 선택을 시뮬레이션하여 옵션2를 업데이트합니다."""
        try:
            logger.info(f"    └─ 옵션1 '{option1['text']}' 선택 시뮬레이션 중...")
            
            # Selenium을 사용하여 JavaScript 실행
            try:
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                logger.info(f"    └─ Selenium WebDriver 초기화 중...")
                
                # Chrome 옵션 설정 (헤드리스 모드)
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--headless')  # 백그라운드 실행
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                
                # WebDriver 초기화
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                try:
                    # 파라미터로 받은 URL 사용
                    driver.get(url)
                    
                    # 옵션1 선택
                    option1_select = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, website_config.get('option1_selector', '#option1')))
                    )
                    
                    # 옵션1에서 해당 옵션 선택
                    for option in option1_select.find_elements(By.TAG_NAME, 'option'):
                        if option.text == option1['text']:
                            option.click()
                            logger.info(f"    └─ 옵션1 '{option1['text']}' 선택 완료")
                            break
                    
                    # 옵션2 업데이트 대기
                    import time
                    time.sleep(2)  # 옵션2 업데이트 대기
                    
                    # 업데이트된 페이지 소스 가져오기
                    updated_html = driver.page_source
                    from bs4 import BeautifulSoup
                    updated_soup = BeautifulSoup(updated_html, 'html.parser')
                    
                    logger.info(f"    └─ 옵션1 선택 후 페이지 업데이트 완료")
                    return updated_soup
                    
                finally:
                    driver.quit()
                    
            except ImportError:
                logger.warning(f"    └─ Selenium이 설치되지 않았습니다. 정적 파싱만 가능합니다.")
                return soup
            except Exception as e:
                logger.error(f"    └─ Selenium 실행 중 오류: {e}")
                return soup
            
        except Exception as e:
            logger.error(f"옵션1 선택 시뮬레이션 중 오류: {e}")
            return soup
    
    def _check_option2_static(self, soup, website_config, option1, stock_status):
        """정적 파싱으로 옵션2를 체크합니다 (URL이 없는 경우)."""
        try:
            option2_status = {
                'all_options': [],
                'out_of_stock_options': []
            }
            
            logger.info(f"    └─ 정적 파싱으로 옵션2 탐색 중...")
            
            # 옵션2 선택자로 옵션2 찾기
            option2_element = soup.select_one(website_config.get('option2_selector', '#option2'))
            if not option2_element:
                logger.warning(f"    └─ 옵션2 요소를 찾을 수 없음: {website_config.get('option2_selector', '#option2')}")
                return option2_status
            
            # 옵션2 정보 추출
            option2_info = self._extract_option_info(option2_element)
            logger.info(f"    └─ 옵션2 총 {option2_info['total_count']}개 발견")
            
            # 옵션2의 각 선택지 체크
            for option2 in option2_info['options']:
                option2_text = option2['text']
                combined_option = f"option1: {option1['text']} + option2: {option2_text}"
                option2_status['all_options'].append(combined_option)
                
                logger.info(f"      └─ 옵션2 체크 중: {option2_text}")
                
                # 옵션2가 품절인지 체크
                if website_config['out_of_stock_text'] in option2_text:
                    logger.warning(f"      └─ 옵션2 품절 발견: {option2_text}")
                    option2_status['out_of_stock_options'].append(combined_option)
                else:
                    logger.info(f"      └─ 옵션2 재고 있음: {option2_text}")
            
            logger.info(f"    └─ 정적 옵션2 체크 완료: {len(option2_status['all_options'])}개 옵션, {len(option2_status['out_of_stock_options'])}개 품절")
            return option2_status
            
        except Exception as e:
            logger.error(f"정적 옵션2 체크 중 오류: {e}")
            return {'all_options': [], 'out_of_stock_options': []}
    
    def _check_single_level_stock(self, soup, website_config, stock_status):
        """단일 레벨 옵션의 품절 상태를 체크합니다."""
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
    
    def _extract_option_info(self, select_element):
        """select 요소에서 옵션 정보를 추출합니다."""
        options = []
        try:
            for option in select_element.find_all('option'):
                option_text = option.get_text(strip=True)
                if option_text:
                    options.append({
                        'text': option_text,
                        'value': option.get('value', ''),
                        'selected': option.get('selected') is not None
                    })
        except Exception as e:
            logger.error(f"옵션 정보 추출 중 오류: {e}")
        
        return {
            'options': options,
            'total_count': len(options)
        }
    
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
