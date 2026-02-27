from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime
import os
from string import Template # Добавили этот модуль

USER = "qopq1366"
REPO = "VlessConfig"
GITHUB_BASE = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path_requested = self.path.split('?')[0]
        try:
            if path_requested == "/sub.txt":
                sub_res = requests.get(GITHUB_BASE + "sub.txt", timeout=5)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(sub_res.text.encode('utf-8'))
                return

            sub_res = requests.get(GITHUB_BASE + "sub.txt", timeout=5)
            time_res = requests.get(GITHUB_BASE + "last_update.txt", timeout=5)
            
            current_dir = os.path.dirname(__file__)
            html_path = os.path.join(current_dir, 'template.html')
            
            with open(html_path, 'r', encoding='utf-8') as f:
                html_raw = f.read()
            
            # Подсчет данных
            count = len([l for l in sub_res.text.splitlines() if l.strip()])
            try:
                last_time = datetime.fromisoformat(time_res.text.strip())
                diff = int((datetime.now() - last_time).total_seconds() / 60)
                timer = max(0, 20 - (diff % 20))
            except:
                timer = 20

            # ИСПОЛЬЗУЕМ БЕЗОПАСНУЮ ПОДСТАНОВКУ
            # В template.html замени {count} на $count и {timer} на $timer
            t = Template(html_raw)
            response_html = t.safe_substitute(count=count, timer=timer)

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(response_html.encode('utf-8'))

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
