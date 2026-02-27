import requests
import base64
import re
import os
import urllib3
from datetime import datetime

# Отключаем ворнинги SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ТВОИ ИСТОЧНИКИ + ПРОВЕРЕННЫЕ ДОПОЛНИТЕЛЬНЫЕ
SOURCES = [
    "https://livpn.atwebpages.com/sub.php?token=3b4cbb400a537740",
    "https://subrostunnel.vercel.app/gen.txt",
    "https://gitverse.ru/api/repos/Vsevj/OBS/raw/branch/master/wwh",
    "https://raw.githubusercontent.com/CidVpn/cid-vpn-config/refs/heads/main/general.txt",
    "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/LimeVPN.txt"
]

def decode_content(text):
    try:
        return base64.b64decode(text).decode('utf-8')
    except:
        return text

def scrape():
    raw_configs = []
    print("🚀 Запуск масштабного сбора...")
    
    for url in SOURCES:
        try:
            print(f"📡 Запрос: {url}")
            res = requests.get(url, timeout=15, verify=False)
            if res.status_code == 200:
                content = decode_content(res.text)
                
                found_count = 0
                for line in content.splitlines():
                    line = line.strip()
                    # Проверяем, что строка — это прокси-ссылка
                    if any(line.startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://', 'ssr://']):
                        raw_configs.append(line)
                        found_count += 1
                print(f"✅ Найдено: {found_count}")
        except Exception as e:
            print(f"❌ Ошибка на {url}: {e}")

    # Убираем дубликаты
    unique_configs = list(set(raw_configs))
    
    # СОРТИРОВКА И ГРУППИРОВКА
    # Сначала VLESS, потом Trojan, потом SS
    vless = [c for c in unique_configs if c.startswith('vless://')]
    trojan = [c for c in unique_configs if c.startswith('trojan://')]
    ss = [c for c in unique_configs if c.startswith('ss://')]
    vmess = [c for c in unique_configs if c.startswith('vmess://')]
    
    # Собираем всё вместе
    final_output = vless + trojan + ss + vmess
    
    if not final_output:
        print("⚠ Конфиги не найдены. Отмена записи.")
        return

    # Записываем основной файл подписки
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))
    
    # Записываем время обновления для таймера на сайте
    with open("last_update.txt", "w", encoding="utf-8") as f:
        f.write(datetime.now().isoformat())
        
    print(f"🏁 Готово! Итого: {len(final_output)} конфигов.")
    print(f"📊 VLESS: {len(vless)} | Trojan: {len(trojan)} | SS: {len(ss)}")

if __name__ == "__main__":
    scrape()
