from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime
import os

# НАСТРОЙКИ (обязательно замени на свои)
USER = "qopq1366"
REPO = "VlessConfig"
GITHUB_BASE = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        user_agent = self.headers.get('User-Agent', '').lower()
        # Определяем, зашел ли человек через браузер
        is_browser = any(x in user_agent for x in ['mozilla', 'chrome', 'safari', 'edge'])

        try:
            # 1. Тянем данные из GitHub
            sub_res = requests.get(GITHUB_BASE + "sub.txt", timeout=5)
            time_res = requests.get(GITHUB_BASE + "last_update.txt", timeout=5)
            
            if is_browser:
                # 2. Определяем путь к index.html относительно текущего файла
                current_dir = os.path.dirname(__file__)
                html_path = os.path.join(current_dir, 'index.html')
                
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_template = f.read()
                
                # 3. Считаем статистику
                count = len([l for l in sub_res.text.splitlines() if l.strip()])
                
                try:
                    last_time = datetime.fromisoformat(time_res.text.strip())
                    diff = int((datetime.now() - last_time).total_seconds() / 60)
                    timer = max(0, 20 - (diff % 20))
                except:
                    timer = 20 # Если файл времени битый

                # 4. Отдаем страницу
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                
                response_html = html_template.format(count=count, timer=timer)
                self.wfile.write(response_html.encode('utf-8'))
            else:
                # 5. Для v2raytun отдаем чистый текст
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(sub_res.text.encode('utf-8'))

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"System initializing... If you just created the repo, please run GitHub Action manually once. Error: {str(e)}".encode('utf-8'))
