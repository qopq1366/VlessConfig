from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime, timezone
import os
import time
from string import Template

# НАСТРОЙКИ
USER = "qopq1366"
REPO = "VlessConfig"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/"
GITHUB_API_URL = f"https://api.github.com/repos/{USER}/{REPO}/commits/main"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path_requested = self.path.split('?')[0]
        # Генерируем уникальный ключ для обхода кеша
        nocache_suffix = f"?t={int(time.time())}"
        
        try:
            # 1. Ссылка для v2raytun (/sub.txt)
            if path_requested == "/sub.txt":
                sub_res = requests.get(GITHUB_RAW_BASE + "sub.txt" + nocache_suffix, timeout=5)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                # Запрещаем кеширование подписки
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                
                self.wfile.write(sub_res.text.encode('utf-8'))
                return

            # 2. Главная страница (Сайт)
            # Запрашиваем данные с GitHub с анти-кеш суффиксом
            sub_res = requests.get(GITHUB_RAW_BASE + "sub.txt" + nocache_suffix, timeout=5)
            api_res = requests.get(GITHUB_API_URL + nocache_suffix, timeout=5).json()
            
            # Считаем количество серверов
            count = len([l for l in sub_res.text.splitlines() if l.strip()])
            
            # Считаем время от последнего коммита
            commit_date_str = api_res['commit']['committer']['date'].replace('Z', '+00:00')
            last_commit_time = datetime.fromisoformat(commit_date_str)
            now = datetime.now(timezone.utc)
            
            diff_minutes = int((now - last_commit_time).total_seconds() / 60)
            timer = max(0, 20 - (diff_minutes % 20))

            # Загружаем HTML
            current_dir = os.path.dirname(__file__)
            html_path = os.path.join(current_dir, 'template.html')
            with open(html_path, 'r', encoding='utf-8') as f:
                html_raw = f.read()

            # Подставляем переменные
            t = Template(html_raw)
            response_html = t.safe_substitute(count=count, timer=timer)

            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            # Запрещаем кеширование страницы
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            
            self.wfile.write(response_html.encode('utf-8'))

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"Update in progress... Error details: {str(e)}".encode('utf-8'))
