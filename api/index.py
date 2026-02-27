from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime, timezone
import os
from string import Template

# НАСТРОЙКИ
USER = "qopq1366"
REPO = "VlessConfig"
# Ссылка для получения данных
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/"
# Ссылка на API для проверки времени коммита
GITHUB_API_URL = f"https://api.github.com/repos/{USER}/{REPO}/commits/main"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path_requested = self.path.split('?')[0]
        
        try:
            # 1. Если запрашивают конфиги для v2raytun
            if path_requested == "/sub.txt":
                sub_res = requests.get(GITHUB_RAW_BASE + "sub.txt", timeout=5)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(sub_res.text.encode('utf-8'))
                return

            # 2. Если зашли на главную страницу (Сайт)
            # Тянем конфиги для подсчета количества
            sub_res = requests.get(GITHUB_RAW_BASE + "sub.txt", timeout=5)
            count = len([l for l in sub_res.text.splitlines() if l.strip()])

            # Тянем время последнего коммита через API
            # GitHub возвращает время в формате ISO 8601 (UTC)
            api_res = requests.get(GITHUB_API_URL, timeout=5).json()
            commit_date_str = api_res['commit']['committer']['date'].replace('Z', '+00:00')
            last_commit_time = datetime.fromisoformat(commit_date_str)
            
            # Считаем разницу с текущим временем в UTC
            now = datetime.now(timezone.utc)
            diff_minutes = int((now - last_commit_time).total_seconds() / 60)
            
            # Рассчитываем таймер до следующего 20-минутного окна
            # (отсчитываем от последнего реального коммита)
            timer = max(0, 20 - (diff_minutes % 20))

            # Загружаем HTML-шаблон
            current_dir = os.path.dirname(__file__)
            html_path = os.path.join(current_dir, 'template.html')
            
            with open(html_path, 'r', encoding='utf-8') as f:
                html_raw = f.read()

            # Безопасно подставляем переменные $count и $timer
            t = Template(html_raw)
            response_html = t.safe_substitute(count=count, timer=timer)

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(response_html.encode('utf-8'))

        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"System error or GitHub API limit. Details: {str(e)}".encode('utf-8'))
