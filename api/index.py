from http.server import BaseHTTPRequestHandler
import requests
import os
import time

# Данные твоего репозитория
USER = "qopq1366"
REPO = "VlessConfig"
GITHUB_RAW = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Очищаем путь от параметров (например, ?t=...)
        path = self.path.split('?')[0]
        # Метка времени для обхода кэша при запросе к GitHub
        ts = int(time.time()) 
        
        try:
            # 1. Обработка запроса прямой ссылки на подписку
            if path == "/sub.txt":
                # Запрашиваем файл напрямую из GitHub с анти-кэшем
                r = requests.get(f"{GITHUB_RAW}sub.txt?t={ts}", timeout=10)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                # Запрещаем Vercel кэшировать файл подписки
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(r.text.encode('utf-8'))
                return

            # 2. Обработка главной страницы (HTML)
            current_dir = os.path.dirname(__file__)
            # Читаем твой новый шаблон без переменных $count и $timer
            with open(os.path.join(current_dir, 'template.html'), 'r', encoding='utf-8') as f:
                html_content = f.read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            # Запрещаем кэширование страницы для корректной работы кнопки копирования
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.end_headers()
            
            self.wfile.write(html_content.encode('utf-8'))

        except Exception as e:
            # Если что-то пошло не так, выводим простое уведомление
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"Proxy System Online. Please refresh. (Code: {str(e)})".encode('utf-8'))
