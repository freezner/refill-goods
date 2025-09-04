import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from monitor import StockMonitor
from email_sender import EmailSender
from config import Config
import json
import os

class StockMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("상품 재고 모니터링 시스템")
        self.root.geometry("900x700")
        
        self.monitor = StockMonitor()
        self.email_sender = EmailSender()
        
        # 모니터에 로그 콜백 설정
        self.monitor.log_callback = self._add_log
        
        # 설정 파일 경로 (사용자 홈 디렉토리에 저장)
        import os
        home_dir = os.path.expanduser("~")
        self.config_file = os.path.join(home_dir, "StockMonitor_config.json")
        
        # GUI 구성
        self._create_widgets()
        self._load_config()
        
        # 상태 업데이트 타이머
        self._start_status_update()
        
        # 초기 로그 추가
        self._add_log("INFO", "상품 재고 모니터링 시스템이 시작되었습니다.")
        self._add_log("INFO", "모니터링할 URL을 추가하고 모니터링을 시작하세요.")
    
    def _create_widgets(self):
        """GUI 위젯들을 생성합니다."""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 필요한 변수들 초기화
        self.receiver_email_var = tk.StringVar(value=Config.DEFAULT_RECEIVER_EMAIL)
        self.interval_var = tk.StringVar(value="1")
        
        # 제목
        title_label = ttk.Label(main_frame, text="상품 재고 모니터링 시스템", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL 모니터링 섹션
        self._create_url_monitoring(main_frame, 1)
        
        # 모니터링 상태 섹션
        self._create_monitoring_status(main_frame, 2)
        
        # 실시간 로그 섹션
        self._create_log_section(main_frame, 3)
        
        # 버튼들
        self._create_buttons(main_frame, 4)
        
        # 설정 메뉴 생성
        self._create_settings_menu()
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def _create_email_settings(self, parent, row):
        """이메일 설정 섹션을 생성합니다."""
        # 이메일 설정 프레임
        email_frame = ttk.LabelFrame(parent, text="이메일 설정", padding="10")
        email_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 설명 텍스트
        info_text = "알림을 받을 이메일 주소를 입력하세요.\nGmail을 통해 자동으로 발송됩니다."
        info_label = ttk.Label(email_frame, text=info_text, foreground="gray")
        info_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # 수신자 이메일
        ttk.Label(email_frame, text="수신자 이메일:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.receiver_email_var = tk.StringVar(value=Config.DEFAULT_RECEIVER_EMAIL)
        receiver_email_entry = ttk.Entry(email_frame, textvariable=self.receiver_email_var, width=40)
        receiver_email_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 이메일 테스트 버튼
        test_email_btn = ttk.Button(email_frame, text="이메일 연결 테스트", 
                                   command=self._test_email_connection)
        test_email_btn.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 그리드 가중치
        email_frame.columnconfigure(1, weight=1)
    
    def _create_url_monitoring(self, parent, row):
        """URL 모니터링 섹션을 생성합니다."""
        # URL 모니터링 프레임
        url_frame = ttk.LabelFrame(parent, text="URL 모니터링", padding="10")
        url_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # URL 입력
        ttk.Label(url_frame, text="상품 URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # URL 입력 필드에 붙여넣기 단축키 및 우클릭 메뉴 추가
        self._setup_url_entry_context_menu(url_entry)
        
        # URL 입력 도움말
        help_text = "Ctrl+V로 붙여넣기 또는 우클릭으로 메뉴 사용"
        help_label = ttk.Label(url_frame, text=help_text, foreground="gray", font=("Arial", 8))
        help_label.grid(row=1, column=1, sticky=tk.W, pady=(2, 0))
        
        # URL 추가/제거 버튼
        add_url_btn = ttk.Button(url_frame, text="URL 추가", command=self._add_url)
        add_url_btn.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        remove_url_btn = ttk.Button(url_frame, text="URL 제거", command=self._remove_url)
        remove_url_btn.grid(row=2, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # 모니터링 중인 URL 목록
        ttk.Label(url_frame, text="모니터링 중인 URL:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        self.url_listbox = tk.Listbox(url_frame, height=4)
        self.url_listbox.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 그리드 가중치
        url_frame.columnconfigure(1, weight=1)
    
    def _create_monitoring_status(self, parent, row):
        """모니터링 상태 섹션을 생성합니다."""
        # 모니터링 상태 프레임
        status_frame = ttk.LabelFrame(parent, text="모니터링 상태", padding="10")
        status_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        # 상태 표시
        self.status_label = ttk.Label(status_frame, text="상태: 중지됨")
        self.status_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        # URL 수 표시
        self.url_count_label = ttk.Label(status_frame, text="모니터링 URL 수: 0")
        self.url_count_label.grid(row=0, column=1, sticky=tk.W)
        
        # 그리드 가중치
        status_frame.columnconfigure(1, weight=1)
    
    def _create_buttons(self, parent, row):
        """모니터링 제어 버튼들을 생성합니다."""
        # 버튼 프레임
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        # 시작 버튼
        self.start_btn = ttk.Button(button_frame, text="모니터링 시작", command=self._start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 중지 버튼
        self.stop_btn = ttk.Button(button_frame, text="모니터링 중지", command=self._stop_monitoring, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 설정 저장 버튼
        save_config_btn = ttk.Button(button_frame, text="설정 저장", command=self._manual_save_config)
        save_config_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 종료 버튼
        exit_btn = ttk.Button(button_frame, text="종료", command=self._exit_application)
        exit_btn.pack(side=tk.RIGHT)
    
    def _create_interval_section(self, parent, row):
        """체크 간격 설정 섹션을 생성합니다."""
        # 체크 간격 프레임
        interval_frame = ttk.LabelFrame(parent, text="체크 간격 설정", padding="10")
        interval_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        # 체크 간격 설명
        ttk.Label(interval_frame, text="모니터링할 상품의 재고 체크 간격을 설정하세요:").grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # 체크 간격 선택
        ttk.Label(interval_frame, text="체크 간격:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.interval_var = tk.StringVar(value="1")
        
        # 사용자 친화적인 표시를 위한 값과 표시 텍스트 분리
        interval_values = ["0.17", "0.5", "1", "5", "10", "30", "60"]
        interval_display = ["10초", "30초", "1분", "5분", "10분", "30분", "1시간"]
        
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var, 
                                     values=interval_display, width=15, state="readonly")
        interval_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        
        # 선택된 값에 따라 실제 값 설정
        def on_interval_change(event):
            selected_index = interval_combo.current()
            if selected_index >= 0:
                self.interval_var.set(interval_values[selected_index])
        
        interval_combo.bind('<<ComboboxSelected>>', on_interval_change)
        
        # 체크 간격 도움말
        interval_help = "빠른 모니터링: 10초/30초 | 일반 모니터링: 1분~30분 | 장기 모니터링: 1시간"
        interval_help_label = ttk.Label(interval_frame, text=interval_help, foreground="gray", font=("Arial", 9))
        interval_help_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # 그리드 가중치
        interval_frame.columnconfigure(1, weight=1)
    
    def _create_settings_menu(self):
        """설정 메뉴를 생성합니다."""
        # 메뉴바 생성
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 설정 메뉴
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        
        # 설정 메뉴 항목
        settings_menu.add_command(label="이메일 및 체크 간격 설정", command=self._show_settings_dialog)
        settings_menu.add_separator()
        settings_menu.add_command(label="설정 저장", command=self._manual_save_config)
        settings_menu.add_command(label="설정 불러오기", command=self._load_config)
    
    def _show_settings_dialog(self):
        """설정 대화상자를 표시합니다."""
        # 설정 창 생성
        settings_window = tk.Toplevel(self.root)
        settings_window.title("설정")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 메인 프레임
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text="설정", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 이메일 설정 섹션
        email_frame = ttk.LabelFrame(main_frame, text="이메일 설정", padding="15")
        email_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(email_frame, text="수신자 이메일:").pack(anchor=tk.W)
        email_entry = ttk.Entry(email_frame, textvariable=self.receiver_email_var, width=50)
        email_entry.pack(fill=tk.X, pady=(5, 10))
        
        # 이메일 테스트 버튼
        test_email_btn = ttk.Button(email_frame, text="이메일 연결 테스트", 
                                   command=self._test_email_connection)
        test_email_btn.pack(anchor=tk.W)
        
        # 체크 간격 설정 섹션
        interval_frame = ttk.LabelFrame(main_frame, text="체크 간격 설정", padding="15")
        interval_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(interval_frame, text="모니터링할 상품의 재고 체크 간격을 설정하세요:").pack(anchor=tk.W, pady=(0, 10))
        
        # 체크 간격 선택
        interval_label_frame = ttk.Frame(interval_frame)
        interval_label_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(interval_label_frame, text="체크 간격:").pack(side=tk.LEFT)
        
        # 사용자 친화적인 표시를 위한 값과 표시 텍스트 분리
        interval_values = ["0.17", "0.5", "1", "5", "10", "30", "60"]
        interval_display = ["10초", "30초", "1분", "5분", "10분", "30분", "1시간"]
        
        interval_combo = ttk.Combobox(interval_label_frame, textvariable=self.interval_var, 
                                     values=interval_display, width=20, state="readonly")
        interval_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # 선택된 값에 따라 실제 값 설정
        def on_interval_change(event):
            selected_index = interval_combo.current()
            if selected_index >= 0:
                self.interval_var.set(interval_values[selected_index])
        
        interval_combo.bind('<<ComboboxSelected>>', on_interval_change)
        
        # 체크 간격 도움말
        interval_help = "빠른 모니터링: 10초/30초 | 일반 모니터링: 1분~30분 | 장기 모니터링: 1시간"
        interval_help_label = ttk.Label(interval_frame, text=interval_help, foreground="gray", font=("Arial", 9))
        interval_help_label.pack(anchor=tk.W)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 저장 버튼
        save_btn = ttk.Button(button_frame, text="저장", command=lambda: self._save_settings_and_close(settings_window))
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 취소 버튼
        cancel_btn = ttk.Button(button_frame, text="취소", command=settings_window.destroy)
        cancel_btn.pack(side=tk.RIGHT)
        
        # 현재 설정된 값으로 초기화
        current_interval = self.interval_var.get()
        try:
            interval_index = interval_values.index(current_interval)
            interval_combo.current(interval_index)
        except ValueError:
            interval_combo.current(0)  # 기본값
    
    def _save_settings_and_close(self, settings_window):
        """설정을 저장하고 창을 닫습니다."""
        try:
            # 설정 저장
            self._save_config()
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
            settings_window.destroy()
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장에 실패했습니다: {e}")
    
    def _setup_url_entry_context_menu(self, entry_widget):
        """URL 입력 필드에 컨텍스트 메뉴와 단축키를 설정합니다."""
        # 컨텍스트 메뉴 생성
        context_menu = tk.Menu(entry_widget, tearoff=0)
        
        # 메뉴 항목 추가
        context_menu.add_command(label="잘라내기", command=lambda: entry_widget.event_generate("<<Cut>>"))
        context_menu.add_command(label="복사", command=lambda: entry_widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="붙여넣기", command=lambda: entry_widget.event_generate("<<Paste>>"))
        context_menu.add_separator()
        context_menu.add_command(label="모두 선택", command=lambda: entry_widget.select_range(0, tk.END))
        context_menu.add_command(label="지우기", command=lambda: self.url_var.set(""))
        
        # 우클릭 이벤트 바인딩
        entry_widget.bind("<Button-3>", lambda e: self._show_context_menu(e, context_menu))
        
        # 단축키 바인딩 (Windows/Linux용 Control, MacOS용 Command)
        # 중복 이벤트 방지를 위해 직접 붙여넣기 처리
        entry_widget.bind("<Control-v>", self._handle_shortcut_paste)
        entry_widget.bind("<Control-V>", self._handle_shortcut_paste)
        entry_widget.bind("<Command-v>", self._handle_shortcut_paste)
        entry_widget.bind("<Command-V>", self._handle_shortcut_paste)
        
        entry_widget.bind("<Control-c>", lambda e: entry_widget.event_generate("<<Copy>>"))
        entry_widget.bind("<Control-C>", lambda e: entry_widget.event_generate("<<Copy>>"))
        entry_widget.bind("<Command-c>", lambda e: entry_widget.event_generate("<<Copy>>"))
        entry_widget.bind("<Command-C>", lambda e: entry_widget.event_generate("<<Copy>>"))
        
        entry_widget.bind("<Control-x>", lambda e: entry_widget.event_generate("<<Cut>>"))
        entry_widget.bind("<Control-X>", lambda e: entry_widget.event_generate("<<Cut>>"))
        entry_widget.bind("<Command-x>", lambda e: entry_widget.event_generate("<<Cut>>"))
        entry_widget.bind("<Command-X>", lambda e: entry_widget.event_generate("<<Cut>>"))
        
        entry_widget.bind("<Control-a>", lambda e: entry_widget.select_range(0, tk.END))
        entry_widget.bind("<Control-A>", lambda e: entry_widget.select_range(0, tk.END))
        entry_widget.bind("<Command-a>", lambda e: entry_widget.select_range(0, tk.END))
        entry_widget.bind("<Command-A>", lambda e: entry_widget.select_range(0, tk.END))
        
        # 붙여넣기 이벤트 처리 (중복 방지)
        entry_widget.bind("<<Paste>>", self._handle_paste)
        
        # 추가 붙여넣기 이벤트 바인딩 방지
        entry_widget.unbind_class("Entry", "<<Paste>>")
    
    def _show_context_menu(self, event, menu):
        """컨텍스트 메뉴를 표시합니다."""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _handle_paste(self, event):
        """붙여넣기 이벤트를 처리합니다."""
        try:
            # 이벤트 중복 처리 방지
            if hasattr(self, '_last_paste_time'):
                current_time = time.time()
                if current_time - self._last_paste_time < 0.1:  # 0.1초 내 중복 방지
                    return
            self._last_paste_time = time.time()
            
            # 클립보드 내용 가져오기
            clipboard_content = self.root.clipboard_get()
            
            if not clipboard_content:
                self._add_log("WARNING", "클립보드가 비어있습니다.")
                return
            
            # 현재 입력 필드의 내용과 비교하여 중복 붙여넣기 방지
            current_content = self.url_var.get().strip()
            if current_content == clipboard_content.strip():
                self._add_log("INFO", "이미 동일한 URL이 입력되어 있습니다.")
                return
            
            # URL 유효성 검사
            if self._is_valid_url(clipboard_content):
                self.url_var.set(clipboard_content.strip())
                self._add_log("INFO", f"URL이 붙여넣기되었습니다: {clipboard_content[:50]}...")
            else:
                self._add_log("WARNING", f"붙여넣기된 내용이 유효한 URL이 아닙니다: {clipboard_content[:30]}...")
                
        except Exception as e:
            self._add_log("ERROR", f"붙여넣기 처리 중 오류: {e}")
            # 에러 발생 시에도 클립보드 내용을 입력 필드에 설정
            try:
                clipboard_content = self.root.clipboard_get()
                if clipboard_content:
                    self.url_var.set(clipboard_content.strip())
                    self._add_log("INFO", "클립보드 내용을 입력 필드에 설정했습니다.")
            except:
                pass
    
    def _handle_shortcut_paste(self, event):
        """단축키를 통한 붙여넣기를 처리합니다."""
        # 이벤트 전파 중지
        event.widget.focus_set()
        # 직접 붙여넣기 처리
        self._handle_paste(None)
        return "break"  # 이벤트 전파 중지
    
    def _is_valid_url(self, url):
        """URL 유효성을 검사합니다."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url.strip())
            return all([parsed.scheme, parsed.netloc])
        except:
            return False
    
    def _is_valid_email(self, email):
        """이메일 유효성을 검사합니다."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _create_monitoring_status(self, parent, row):
        """모니터링 상태 섹션을 생성합니다."""
        # 상태 프레임
        status_frame = ttk.LabelFrame(parent, text="모니터링 상태", padding="10")
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 상태 정보
        self.status_label = ttk.Label(status_frame, text="상태: 중지됨")
        self.status_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.url_count_label = ttk.Label(status_frame, text="모니터링 URL 수: 0")
        self.url_count_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # 시작/중지 버튼
        self.start_btn = ttk.Button(status_frame, text="모니터링 시작", command=self._start_monitoring)
        self.start_btn.grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        self.stop_btn = ttk.Button(status_frame, text="모니터링 중지", command=self._stop_monitoring, 
                                  state="disabled")
        self.stop_btn.grid(row=0, column=3, sticky=tk.W)
        
        # 그리드 가중치
        status_frame.columnconfigure(1, weight=1)
    
    def _create_log_section(self, parent, row):
        """실시간 모니터링 로그 섹션을 생성합니다."""
        # 로그 프레임
        log_frame = ttk.LabelFrame(parent, text="실시간 모니터링 로그", padding="10")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80, 
                                                font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 로그 제어 버튼들
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 로그 지우기 버튼
        clear_log_btn = ttk.Button(log_control_frame, text="로그 지우기", 
                                  command=self._clear_log)
        clear_log_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 로그 저장 버튼
        save_log_btn = ttk.Button(log_control_frame, text="로그 저장", 
                                 command=self._save_log)
        save_log_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 자동 스크롤 체크박스
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = ttk.Checkbutton(log_control_frame, text="자동 스크롤", 
                                          variable=self.auto_scroll_var)
        auto_scroll_check.pack(side=tk.LEFT)
        
        # 로그 레벨 필터
        ttk.Label(log_control_frame, text="로그 레벨:").pack(side=tk.LEFT, padx=(20, 5))
        self.log_level_var = tk.StringVar(value="ALL")
        log_level_combo = ttk.Combobox(log_control_frame, textvariable=self.log_level_var, 
                                      values=["ALL", "INFO", "WARNING", "ERROR"], 
                                      state="readonly", width=10)
        log_level_combo.pack(side=tk.LEFT)
        
        # 그리드 가중치
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def _create_buttons(self, parent, row):
        """버튼들을 생성합니다."""
        # 버튼 프레임
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(10, 0))
        
        # 설정 저장 버튼
        save_config_btn = ttk.Button(button_frame, text="설정 저장", command=self._manual_save_config)
        save_config_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 설정 불러오기 버튼
        load_config_btn = ttk.Button(button_frame, text="설정 불러오기", command=self._load_config)
        load_config_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 종료 버튼
        exit_btn = ttk.Button(button_frame, text="종료", command=self._exit_application)
        exit_btn.pack(side=tk.RIGHT)
    
    def _test_email_connection(self):
        """이메일 연결을 테스트합니다."""
        # 설정 업데이트
        self._update_email_config()
        
        # 연결 테스트
        success, message = self.email_sender.test_email_connection()
        
        if success:
            messagebox.showinfo("연결 성공", message)
            self._add_log("INFO", f"이메일 연결 테스트 성공: {message}")
            # 성공 시 자동 저장
            self._save_config()
        else:
            messagebox.showerror("연결 실패", message)
            self._add_log("ERROR", f"이메일 연결 테스트 실패: {message}")
    
    def _add_url(self):
        """URL을 모니터링에 추가합니다."""
        url = self.url_var.get().strip()
        
        # URL 입력 검증
        if not url:
            messagebox.showwarning("경고", "URL을 입력해주세요.")
            self._add_log("WARNING", "URL 입력이 비어있습니다.")
            return
        
        # URL 형식 검증
        if not self._is_valid_url(url):
            messagebox.showerror("오류", "유효하지 않은 URL 형식입니다.\n예시: https://example.com/product")
            self._add_log("ERROR", f"유효하지 않은 URL 형식: {url}")
            return
        
        # 공통 체크 간격 사용
        interval = float(self.interval_var.get())
        
        # 수신자 이메일 검증
        receiver_email = self.receiver_email_var.get().strip()
        if not receiver_email:
            messagebox.showwarning("경고", "수신자 이메일을 입력해주세요.")
            self._add_log("WARNING", "수신자 이메일이 입력되지 않았습니다.")
            return
        
        # 이메일 형식 검증
        if not self._is_valid_email(receiver_email):
            messagebox.showerror("오류", "유효하지 않은 이메일 형식입니다.")
            self._add_log("ERROR", f"유효하지 않은 이메일 형식: {receiver_email}")
            return
        
        # 중복 URL 검사
        if url in self.monitor.monitored_urls:
            messagebox.showwarning("경고", "이미 모니터링 중인 URL입니다.")
            self._add_log("WARNING", f"중복 URL: {url}")
            return
        
        # URL 추가 시도
        if self.monitor.add_url(url, interval, receiver_email):
            self.url_var.set("")  # 입력 필드 초기화
            self._update_url_list()
            interval_text = self._format_interval(interval)
            self._add_log("INFO", f"URL 추가 성공: {url} (간격: {interval_text})")
            
            # URL 추가 후 자동 저장
            self._save_config()
            
            # 성공 메시지
            messagebox.showinfo("성공", f"URL이 추가되었습니다.\n\nURL: {url}\n체크 간격: {interval_text}")
        else:
            messagebox.showerror("오류", "URL 추가에 실패했습니다.")
            self._add_log("ERROR", f"URL 추가 실패: {url}")
    
    def _remove_url(self):
        """선택된 URL을 모니터링에서 제거합니다."""
        selection = self.url_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "제거할 URL을 선택해주세요.")
            return
        
        # 표시된 텍스트에서 실제 URL 추출
        display_text = self.url_listbox.get(selection[0])
        # "URL (간격: X)" 형태에서 URL 부분만 추출
        url = display_text.split(" (간격:")[0].strip()
        
        # URL 제거 확인
        confirm = messagebox.askyesno("확인", f"다음 URL을 모니터링에서 제거하시겠습니까?\n\n{url}")
        if not confirm:
            return
        
        if self.monitor.remove_url(url):
            self._update_url_list()
            self._add_log("INFO", f"URL 제거됨: {url}")
            
            # URL 제거 후 자동 저장
            self._save_config()
        else:
            messagebox.showerror("오류", f"URL 제거에 실패했습니다: {url}")
    
    def _start_monitoring(self):
        """모니터링을 시작합니다."""
        if not self.monitor.monitored_urls:
            messagebox.showwarning("경고", "모니터링할 URL을 추가해주세요.")
            return
        
        # 이메일 설정 업데이트
        self._update_email_config()
        
        # 모니터링 시작
        self.monitor.start_monitoring()
        
        # UI 상태 업데이트
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="상태: 실행 중")
        
        self._add_log("INFO", "모니터링이 시작되었습니다.")
        self._add_log("INFO", f"모니터링 URL 수: {len(self.monitor.monitored_urls)}")
        
        # 체크 간격 정보 표시 (첫 번째 URL 기준)
        if self.monitor.monitored_urls:
            first_url = list(self.monitor.monitored_urls.keys())[0]
            interval = self.monitor.monitored_urls[first_url]['interval']
            interval_text = self._format_interval(interval)
            self._add_log("INFO", f"체크 간격: {interval_text}")
    
    def _stop_monitoring(self):
        """모니터링을 중지합니다."""
        self.monitor.stop_monitoring()
        
        # UI 상태 업데이트
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="상태: 중지됨")
        
        self._add_log("INFO", "모니터링이 중지되었습니다.")
    
    def _update_email_config(self):
        """이메일 설정을 업데이트합니다."""
        # 수신자 이메일만 업데이트
        os.environ['DEFAULT_RECEIVER_EMAIL'] = self.receiver_email_var.get()
        
        # EmailSender 인스턴스 재생성
        self.email_sender = EmailSender()
    
    def _update_url_list(self):
        """URL 목록을 업데이트합니다."""
        self.url_listbox.delete(0, tk.END)
        for url, config in self.monitor.monitored_urls.items():
            interval_text = self._format_interval(config['interval'])
            display_text = f"{url} (간격: {interval_text})"
            self.url_listbox.insert(tk.END, display_text)
        
        # URL 수 업데이트
        self.url_count_label.config(text=f"모니터링 URL 수: {len(self.monitor.monitored_urls)}")
    
    def _format_interval(self, interval):
        """체크 간격을 읽기 쉬운 형태로 포맷합니다."""
        try:
            interval_float = float(interval)
            if interval_float < 1:
                seconds = int(interval_float * 60)
                if seconds == 10:
                    return "10초"
                elif seconds == 30:
                    return "30초"
                else:
                    return f"{seconds}초"
            elif interval_float == 1:
                return "1분"
            elif interval_float < 60:
                return f"{int(interval_float)}분"
            else:
                hours = interval_float / 60
                if hours == 1:
                    return "1시간"
                else:
                    return f"{int(hours)}시간"
        except ValueError:
            return interval
    
    def _start_status_update(self):
        """상태 업데이트 타이머를 시작합니다."""
        def update_status():
            while True:
                try:
                    # UI 업데이트는 메인 스레드에서 실행
                    self.root.after(0, self._update_status_display)
                    
                    # 모니터링 중일 때만 로그 업데이트 (5초마다)
                    if hasattr(self, 'monitor') and getattr(self.monitor, 'is_monitoring', False):
                        self.root.after(0, self._update_monitoring_log)
                        time.sleep(5)  # 로그 부하 감소
                    else:
                        time.sleep(1)
                except:
                    break
        
        status_thread = threading.Thread(target=update_status, daemon=True)
        status_thread.start()
    
    def _update_status_display(self):
        """상태 표시를 업데이트합니다."""
        try:
            status = self.monitor.get_monitoring_status()
            
            if status['is_running']:
                self.status_label.config(text="상태: 실행 중")
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
            else:
                self.status_label.config(text="상태: 중지됨")
                self.start_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
            
            self.url_count_label.config(text=f"모니터링 URL 수: {status['total_urls']}")
            
        except:
            pass
    
    def _log_message(self, message):
        """로그 메시지를 추가합니다."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def _clear_log(self):
        """로그를 지웁니다."""
        self.log_text.delete(1.0, tk.END)
        self._add_log("INFO", "로그가 지워졌습니다.")
    
    def _save_log(self):
        """로그를 파일로 저장합니다."""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
                title="로그 저장"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self._add_log("INFO", f"로그가 {filename}에 저장되었습니다.")
        except Exception as e:
            self._add_log("ERROR", f"로그 저장 실패: {e}")
    
    def _add_log(self, level, message):
        """로그를 추가합니다."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 로그 레벨에 따른 색상 설정
        level_colors = {
            "INFO": "black",
            "WARNING": "orange",
            "ERROR": "red"
        }
        
        # 현재 선택된 로그 레벨 확인
        if self.log_level_var.get() != "ALL" and self.log_level_var.get() != level:
            return
        
        # 로그 텍스트에 추가
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # 로그 레벨에 따른 색상 적용
        self.log_text.insert(tk.END, log_entry)
        
        # 자동 스크롤
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
        
        # 로그가 너무 많으면 오래된 것 삭제 (최대 1000줄)
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 1000:
            self.log_text.delete(1.0, f"{lines-1000}.0")
    
    def _update_monitoring_log(self):
        """모니터링 상태를 로그로 업데이트합니다."""
        if hasattr(self, 'monitor') and self.monitor.is_monitoring:
            # 현재 모니터링 중인 URL 수
            url_count = len(self.monitor.monitored_urls)
            # 마지막 체크 시간
            last_check = getattr(self.monitor, 'last_check_time', '알 수 없음')
            if last_check != '알 수 없음':
                last_check = last_check.strftime("%H:%M:%S")
            
            self._add_log("INFO", f"모니터링 중: {url_count}개 URL, 마지막 체크: {last_check}")
            
            # 다음 체크까지 남은 시간
            if hasattr(self.monitor, 'next_check_time'):
                next_check = self.monitor.next_check_time
                if next_check:
                    remaining = (next_check - datetime.datetime.now()).total_seconds()
                    if remaining > 0:
                        self._add_log("INFO", f"다음 체크까지 {int(remaining)}초 남음")
    
    def _save_config(self):
        """설정을 파일에 저장합니다."""
        config_data = {
            'receiver_email': self.receiver_email_var.get(),
            'monitored_urls': self.monitor.monitored_urls
        }
        
        try:
            # 설정 파일이 저장될 디렉토리 생성
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            # 자동 저장 시에는 팝업을 표시하지 않음 (로그만 기록)
            self._log_message("설정이 자동 저장되었습니다.")
            
        except Exception as e:
            self._log_message(f"설정 저장 실패: {e}")
            messagebox.showerror("오류", f"설정 저장에 실패했습니다: {e}")
    
    def _manual_save_config(self):
        """수동으로 설정을 저장합니다."""
        try:
            self._save_config()
            messagebox.showinfo("성공", "설정이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장에 실패했습니다: {e}")
    
    def _load_config(self):
        """설정을 파일에서 불러옵니다."""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 수신자 이메일만 불러오기
            self.receiver_email_var.set(config_data.get('receiver_email', Config.DEFAULT_RECEIVER_EMAIL))
            
            # 모니터링 URL 불러오기
            monitored_urls = config_data.get('monitored_urls', {})
            for url, config in monitored_urls.items():
                self.monitor.add_url(url, config['interval'], config['receiver_email'])
            
            self._update_url_list()
            self._log_message("설정을 불러왔습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"설정 불러오기에 실패했습니다: {e}")
    
    def _exit_application(self):
        """애플리케이션을 종료합니다."""
        try:
            # 모니터링 중지
            if self.monitor.is_running:
                self.monitor.stop_monitoring()
            
            # 종료 전 자동으로 설정 저장
            self._save_config()
            self._log_message("설정이 자동 저장되었습니다.")
            
        except Exception as e:
            print(f"설정 저장 중 오류: {e}")
        
        self.root.quit()

def main():
    root = tk.Tk()
    app = StockMonitorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
