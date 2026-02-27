from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime
import os

# НАСТРОЙКИ
USER = "qopq1366"
REPO = "VlessConfig"
GITHUB_BASE = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Получаем путь запроса (например, "/" или "/sub.txt")
        path_requested = self.path
        
        user_agent = self.headers.get('User-Agent', '').lower()
        is_browser = any(x in user_agent for x in ['mozilla', 'chrome', 'safari', 'edge'])

        try:
            # Всегда подгружаем актуальные данные с GitHub
            sub_res = requests.get(GITHUB_BASE + "sub.txt", timeout=5)
            time_res = requests.get(GITHUB_BASE + "last_update.txt", timeout=5)
            
            # ЛОГИКА: 
            # Если в URL написано /sub.txt ИЛИ это не браузер — отдаем чистый текст
            if "/sub.txt" in path_requested or not is_browser:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(sub_res.text.encode('utf-8'))
            
            # В остальных случаях (просто зашли на сайт) — отдаем HTML
            else:
                current_dir = os.path.dirname(__file__)
                html_path = os.path.join(current_dir, 'template.html')
                
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_template = f.read()
                
                count = len([l for l in sub_res.text.splitlines() if l.strip()])
                
                try:
                    last_time = datetime.fromisoformat(time_res.text.strip())
                    diff = int((datetime.now() - last_time).total_seconds() / 60)
                    timer = max(0, 20 - (diff % 20))
                except:
                    timer = 20

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                response_html = html_template.format(count=count, timer=timer)
                self.wfile.write(response_html.encode('utf-8'))

        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
