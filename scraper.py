import requests
import base64
import os
import urllib3
import socket
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor # Для скорости

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SOURCES = [
    "https://livpn.atwebpages.com/sub.php?token=3b4cbb400a537740",
    "https://subrostunnel.vercel.app/gen.txt",
    "https://gitverse.ru/api/repos/Vsevj/OBS/raw/branch/master/wwh",
    "https://raw.githubusercontent.com/CidVpn/cid-vpn-config/refs/heads/main/general.txt",
    "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/LimeVPN.txt"
]

COUNTRIES = {
    "GERMANY": "🇩🇪 DE", " DE ": "🇩🇪 DE", "USA": "🇺🇸 US", " US ": "🇺🇸 US",
    "RUSSIA": "🇷🇺 RU", " RU ": "🇷🇺 RU", "TURKEY": "🇹🇷 TR", " TR ": "🇹🇷 TR",
    "FRANCE": "🇫🇷 FR", " FR ": "🇫🇷 FR", "NETHERLANDS": "🇳🇱 NL", " NL ": "🇳🇱 NL",
    "FINLAND": "🇫🇮 FI", " FI ": "🇫🇮 FI", "GREAT BRITAIN": "🇬🇧 GB", " UK ": "🇬🇧 GB",
    "JAPAN": "🇯🇵 JP", "SINGAPORE": "🇸🇬 SG", "POLAND": "🇵🇱 PL", "CANADA": "🇨🇦 CA",
    " UA ": "🇺🇦 UA", "UKRAINE": "🇺🇦 UA"
}

def check_port(config_line):
    """Проверяет порт и возвращает линию, если сервер живой"""
    try:
        # Извлекаем хост и порт
        if config_line.startswith('ss://'):
            content = config_line.split('://')[1].split('#')[0]
            server_data = base64.b64decode(content).decode('utf-8').split('@')[1] if '@' not in content else content.split('@')[1]
            host, port = server_data.split(':')
        else:
            parsed = urlparse(config_line)
            host, port = parsed.hostname, parsed.port

        if host and port:
            with socket.create_connection((host, int(port)), timeout=1.5):
                return config_line
    except:
        return None

def process_config(line, idx):
    """Форматирует название по странам"""
    line_upper = line.upper()
    proto = line.split("://")[0].upper()
    found_country = "🏳️ UNKNOWN"
    
    for key, val in COUNTRIES.items():
        if key in line_upper:
            found_country = val
            break
            
    base = line.split("#")[0]
    return f"{base}#{found_country} {proto} {idx}"

def scrape():
    raw_configs = set()
    print("📡 Сбор ссылок...")
    
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10, verify=False)
            if r.status_code == 200:
                text = r.text
                try: text = base64.b64decode(text).decode('utf-8')
                except: pass
                for l in text.splitlines():
                    if any(l.strip().startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://']):
                        raw_configs.add(l.strip())
        except: continue

    print(f"🔎 Проверка {len(raw_configs)} серверов в 50 потоков...")
    alive_configs = []
    
    # Запускаем параллельную проверку
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_port, raw_configs))
        alive_configs = [r for r in results if r]

    print(f"✨ Живых серверов: {len(alive_configs)}")

    # Форматируем названия
    final_with = []
    final_without = []
    
    for i, line in enumerate(alive_configs):
        formatted = process_config(line, i + 1)
        if "UNKNOWN" in formatted:
            final_without.append(formatted)
        else:
            final_with.append(formatted)

    final_with.sort()
    final = final_with + sorted(final_without)
    
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final))
    with open("last_update.txt", "w", encoding="utf-8") as f:
        f.write(datetime.now().isoformat())

if __name__ == "__main__":
    scrape()
