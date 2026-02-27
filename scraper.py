import requests
import base64
import os
import urllib3
import socket
from datetime import datetime
from urllib.parse import urlparse

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SOURCES = [
    "https://livpn.atwebpages.com/sub.php?token=3b4cbb400a537740",
    "https://subrostunnel.vercel.app/gen.txt",
    "https://gitverse.ru/api/repos/Vsevj/OBS/raw/branch/master/wwh",
    "https://raw.githubusercontent.com/CidVpn/cid-vpn-config/refs/heads/main/general.txt",
    "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/LimeVPN.txt"
]

COUNTRIES = {
    "GERMANY": "🇩🇪 DE", " DE ": "🇩🇪 DE",
    "USA": "🇺🇸 US", " US ": "🇺🇸 US", "UNITED STATES": "🇺🇸 US",
    "RUSSIA": "🇷🇺 RU", " RU ": "🇷🇺 RU",
    "TURKEY": "🇹🇷 TR", " TR ": "🇹🇷 TR",
    "FRANCE": "🇫🇷 FR", " FR ": "🇫🇷 FR",
    "NETHERLANDS": "🇳🇱 NL", " NL ": "🇳🇱 NL",
    "FINLAND": "🇫🇮 FI", " FI ": "🇫🇮 FI",
    "GREAT BRITAIN": "🇬🇧 GB", " UK ": "🇬🇧 GB",
    "JAPAN": "🇯🇵 JP", " JP ": "🇯🇵 JP",
    "SINGAPORE": "🇸🇬 SG", " SG ": "🇸🇬 SG",
    "POLAND": "🇵🇱 PL", " PL ": "🇵🇱 PL",
    "IRAN": "🇮🇷 IR", " KOREA ": "🇰🇷 KR",
    "CANADA": "🇨🇦 CA", " UA ": "🇺🇦 UA", "UKRAINE": "🇺🇦 UA"
}

def check_port(address, port):
    """Проверяет, открыт ли порт сервера (базовая проверка на 'живость')"""
    try:
        with socket.create_connection((address, int(port)), timeout=2):
            return True
    except:
        return False

def get_server_info(line):
    """Парсит адрес и порт из конфига"""
    try:
        if line.startswith('ss://'):
            # Для Shadowsocks извлекаем адрес после @
            content = line.split('://')[1].split('#')[0]
            if '@' in content:
                server_data = content.split('@')[1]
            else:
                # Если закодировано в base64
                decoded = base64.b64decode(content).decode('utf-8')
                server_data = decoded.split('@')[1]
            host, port = server_data.split(':')
            return host, port
        else:
            # Для VLESS/Trojan/VMess
            parsed = urlparse(line)
            return parsed.hostname, parsed.port
    except:
        return None, None

def scrape():
    with_country = []
    without_country = []
    unique_lines = set()
    
    print("--- Start Scraping + Health Check ---")
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15, verify=False)
            if r.status_code == 200:
                text = r.text
                try: text = base64.b64decode(text).decode('utf-8')
                except: pass
                
                for line in text.splitlines():
                    line = line.strip()
                    if any(line.startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://']):
                        if line not in unique_lines:
                            # ПРОВЕРКА ПОРТА (чтобы не было мертвых серверов)
                            host, port = get_server_info(line)
                            if host and port:
                                if check_port(host, port):
                                    unique_lines.add(line)
                                    
                                    # Определяем страну и чистим имя
                                    line_upper = line.upper()
                                    proto = line.split("://")[0].upper()
                                    found_country = None
                                    for key, val in COUNTRIES.items():
                                        if key in line_upper:
                                            found_country = val
                                            break
                                    
                                    base_config = line.split("#")[0]
                                    idx = len(unique_lines)
                                    
                                    if found_country:
                                        new_line = f"{base_config}#{found_country} {proto} {idx}"
                                        with_country.append(new_line)
                                    else:
                                        new_line = f"{base_config}#🏳️ UNKNOWN {proto} {idx}"
                                        without_country.append(new_line)
        except: continue

    # Сортировка и сборка
    with_country.sort()
    without_country.sort()
    final = with_country + without_country
    
    if final:
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final))
        with open("last_update.txt", "w", encoding="utf-8") as f:
            f.write(datetime.now().isoformat())
        print(f"🏁 Done! Alive: {len(final)} (Verified)")
    else:
        print("⚠ No alive servers found!")

if __name__ == "__main__":
    scrape()
