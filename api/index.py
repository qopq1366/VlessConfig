from http.server import BaseHTTPRequestHandler
import requests
import os
import time
from string import Template

USER = "qopq1366"
REPO = "VlessConfig"
GITHUB_RAW = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]
        ts = int(time.time()) 
        
        try:
            if path == "/sub.txt":
                r = requests.get(f"{GITHUB_RAW}sub.txt?t={ts}", timeout=10)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(r.text.encode('utf-8'))
                return

            # Получаем количество серверов для визуала
            sub_res = requests.get(f"{GITHUB_RAW}sub.txt?t={ts}", timeout=10)
            lines = [l for l in sub_res.text.splitlines() if l.strip()]
            count = len(lines)

            # Загружаем HTML
            current_dir = os.path.dirname(__file__)
            with open(os.path.join(current_dir, 'template.html'), 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Подставляем только количество
            t = Template(html_content)
            final_html = t.safe_substitute(count=count)

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.end_headers()
            self.wfile.write(final_html.encode('utf-8'))

        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"System Online. (Error: {str(e)})".encode('utf-8'))
