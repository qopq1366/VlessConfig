import requests, base64, os, urllib3, socket, time
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Твои источники
SOURCES = [
    "https://livpn.atwebpages.com/sub.php?token=3b4cbb400a537740",
    "https://subrostunnel.vercel.app/gen.txt",
    "https://gitverse.ru/api/repos/Vsevj/OBS/raw/branch/master/wwh",
    "https://raw.githubusercontent.com/CidVpn/cid-vpn-config/refs/heads/main/general.txt",
    "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/LimeVPN.txt"
]

def get_country_by_ip(ip):
    """Определяет страну через API (бесплатно)"""
    try:
        # Используем быстрое API ip-api.com
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode", timeout=2).json()
        if response.get("status") == "success":
            code = response.get("countryCode")
            # Превращаем код в флаг
            return f"{chr(ord(code[0]) + 127397)}{chr(ord(code[1]) + 127397)} {code}"
    except:
        pass
    return "🏳️ UNKNOWN"

def check_and_geo(line):
    """Проверяет порт и сразу узнает страну по IP"""
    try:
        if line.startswith('ss://'):
            content = line.split('://')[1].split('#')[0]
            server_data = base64.b64decode(content).decode('utf-8').split('@')[1] if '@' not in content else content.split('@')[1]
            host, port = server_data.split(':')
        else:
            parsed = urlparse(line)
            host, port = parsed.hostname, parsed.port

        # 1. Проверка порта
        with socket.create_connection((host, int(port)), timeout=1.5):
            # 2. Если живой, узнаем страну по IP (host)
            geo = get_country_by_ip(host)
            base = line.split("#")[0]
            proto = line.split("://")[0].upper()
            return f"{base}#{geo} {proto}"
    except:
        return None

def scrape():
    raw_configs = set()
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

    print(f"🔍 Проверка и Геолокация {len(raw_configs)} серверов...")
    
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(check_and_geo, raw_configs))
        alive = [r for r in results if r]

    # Сортировка: сначала страны (по флагу), потом неизвестные
    alive.sort(key=lambda x: ("UNKNOWN" in x, x.split("#")[1]))

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(alive))
    with open("last_update.txt", "w", encoding="utf-8") as f:
        f.write(datetime.now().isoformat())
    print(f"🏁 Успех! Найдено живых: {len(alive)}")

if __name__ == "__main__":
    scrape()
