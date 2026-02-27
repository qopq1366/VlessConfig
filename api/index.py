from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime
import os
import time
from string import Template

USER = "qopq1366"
REPO = "VlessConfig"
GITHUB_RAW = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]
        ts = int(time.time()) # Уникальный хвост для обхода кэша
        
        try:
            # Ссылка для конфигов
            if path == "/sub.txt":
                r = requests.get(f"{GITHUB_RAW}sub.txt?t={ts}", timeout=10)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(r.text.encode('utf-8'))
                return

            # Главная страница
            # 1. Считаем количество серверов
            sub_res = requests.get(f"{GITHUB_RAW}sub.txt?t={ts}", timeout=10)
            count = len([l for l in sub_res.text.splitlines() if l.strip()])

            # 2. Берем время из файла last_update.txt (вместо медленного API)
            try:
                time_res = requests.get(f"{GITHUB_RAW}last_update.txt?t={ts}", timeout=5)
                last_time = datetime.fromisoformat(time_res.text.strip())
                diff = int((datetime.now() - last_time).total_seconds() / 60)
                timer = max(0, 20 - (diff % 20))
            except:
                timer = 20

            # 3. Собираем HTML
            current_dir = os.path.dirname(__file__)
            with open(os.path.join(current_dir, 'template.html'), 'r', encoding='utf-8') as f:
                html_content = f.read()

            t = Template(html_content)
            final_html = t.safe_substitute(count=count, timer=timer)

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(final_html.encode('utf-8'))

        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"System ready. Please refresh. ({str(e)})".encode('utf-8'))
