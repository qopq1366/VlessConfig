from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime
import os

# ЗАМЕНИ НА СВОИ ДАННЫЕ
USER = "qopq1366"
REPO = "VlessConfig"
GITHUB_BASE = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        user_agent = self.headers.get('User-Agent', '').lower()
        is_browser = any(x in user_agent for x in ['mozilla', 'chrome', 'safari', 'edge'])

        try:
            sub_res = requests.get(GITHUB_BASE + "sub.txt", timeout=5)
            time_res = requests.get(GITHUB_BASE + "last_update.txt", timeout=5)
            
            if is_browser:
                # Читаем шаблон из соседнего файла index.html
                with open('index.html', 'r', encoding='utf-8') as f:
                    html = f.read()
                
                # Считаем статистику
                count = len([l for l in sub_res.text.splitlines() if l.strip()])
                last_time = datetime.fromisoformat(time_res.text.strip())
                diff = int((datetime.now() - last_time).total_seconds() / 60)
                timer = max(0, 20 - (diff % 20))
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html.format(count=count, timer=timer).encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(sub_res.text.encode('utf-8'))
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Waiting for first GitHub Action run...")
