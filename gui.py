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
        self.root.geometry("800x600")
        
        self.monitor = StockMonitor()
        self.email_sender = EmailSender()
        
        # 설정 파일 경로 (사용자 홈 디렉토리에 저장)
        import os
        home_dir = os.path.expanduser("~")
        self.config_file = os.path.join(home_dir, "StockMonitor_config.json")
        
        # GUI 구성
        self._create_widgets()
        self._load_config()
        
        # 상태 업데이트 타이머
        self._start_status_update()
    
    def _create_widgets(self):
        """GUI 위젯들을 생성합니다."""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="상품 재고 모니터링 시스템", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 이메일 설정 섹션
        self._create_email_settings(main_frame, 1)
        
        # URL 모니터링 섹션
        self._create_url_monitoring(main_frame, 2)
        
        # 모니터링 상태 섹션
        self._create_monitoring_status(main_frame, 3)
        
        # 로그 섹션
        self._create_log_section(main_frame, 4)
        
        # 버튼들
        self._create_buttons(main_frame, 5)
        
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
        
        # 체크 간격
        ttk.Label(url_frame, text="체크 간격:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.interval_var = tk.StringVar(value="5")
        interval_combo = ttk.Combobox(url_frame, textvariable=self.interval_var, 
                                     values=["1", "5", "10"], width=10, state="readonly")
        interval_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        # URL 추가/제거 버튼
        add_url_btn = ttk.Button(url_frame, text="URL 추가", command=self._add_url)
        add_url_btn.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        remove_url_btn = ttk.Button(url_frame, text="URL 제거", command=self._remove_url)
        remove_url_btn.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # 모니터링 중인 URL 목록
        ttk.Label(url_frame, text="모니터링 중인 URL:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        self.url_listbox = tk.Listbox(url_frame, height=4)
        self.url_listbox.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 그리드 가중치
        url_frame.columnconfigure(1, weight=1)
    
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
        """로그 섹션을 생성합니다."""
        # 로그 프레임
        log_frame = ttk.LabelFrame(parent, text="로그", padding="10")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 로그 지우기 버튼
        clear_log_btn = ttk.Button(log_frame, text="로그 지우기", command=self._clear_log)
        clear_log_btn.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
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
            # 성공 시 자동 저장
            self._save_config()
        else:
            messagebox.showerror("연결 실패", message)
    
    def _add_url(self):
        """URL을 모니터링에 추가합니다."""
        url = self.url_var.get().strip()
        interval = int(self.interval_var.get())
        receiver_email = self.receiver_email_var.get().strip()
        
        if not url:
            messagebox.showwarning("경고", "URL을 입력해주세요.")
            return
        
        if not receiver_email:
            messagebox.showwarning("경고", "수신자 이메일을 입력해주세요.")
            return
        
        if self.monitor.add_url(url, interval, receiver_email):
            self.url_var.set("")  # 입력 필드 초기화
            self._update_url_list()
            self._log_message(f"URL 추가됨: {url}")
            
            # URL 추가 후 자동 저장
            self._save_config()
        else:
            messagebox.showerror("오류", "URL 추가에 실패했습니다.")
    
    def _remove_url(self):
        """선택된 URL을 모니터링에서 제거합니다."""
        selection = self.url_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "제거할 URL을 선택해주세요.")
            return
        
        url = self.url_listbox.get(selection[0])
        if self.monitor.remove_url(url):
            self._update_url_list()
            self._log_message(f"URL 제거됨: {url}")
            
            # URL 제거 후 자동 저장
            self._save_config()
        else:
            messagebox.showerror("오류", "URL 제거에 실패했습니다.")
    
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
        
        self._log_message("모니터링이 시작되었습니다.")
    
    def _stop_monitoring(self):
        """모니터링을 중지합니다."""
        self.monitor.stop_monitoring()
        
        # UI 상태 업데이트
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="상태: 중지됨")
        
        self._log_message("모니터링이 중지되었습니다.")
    
    def _update_email_config(self):
        """이메일 설정을 업데이트합니다."""
        # 수신자 이메일만 업데이트
        os.environ['DEFAULT_RECEIVER_EMAIL'] = self.receiver_email_var.get()
        
        # EmailSender 인스턴스 재생성
        self.email_sender = EmailSender()
    
    def _update_url_list(self):
        """URL 목록을 업데이트합니다."""
        self.url_listbox.delete(0, tk.END)
        for url in self.monitor.monitored_urls.keys():
            self.url_listbox.insert(tk.END, url)
        
        # URL 수 업데이트
        self.url_count_label.config(text=f"모니터링 URL 수: {len(self.monitor.monitored_urls)}")
    
    def _start_status_update(self):
        """상태 업데이트 타이머를 시작합니다."""
        def update_status():
            while True:
                try:
                    # UI 업데이트는 메인 스레드에서 실행
                    self.root.after(0, self._update_status_display)
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
