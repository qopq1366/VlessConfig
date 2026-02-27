import requests
import base64
import os
import urllib3
from datetime import datetime

# Отключаем ошибки SSL для "проблемных" источников
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SOURCES = [
    "https://livpn.atwebpages.com/sub.php?token=3b4cbb400a537740",
    "https://subrostunnel.vercel.app/gen.txt",
    "https://gitverse.ru/api/repos/Vsevj/OBS/raw/branch/master/wwh",
    "https://raw.githubusercontent.com/CidVpn/cid-vpn-config/refs/heads/main/general.txt",
    "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/LimeVPN.txt"
]

def add_country_flags(config):
    """Добавляет эмодзи флага в название конфига для красоты"""
    flags = {
        "DE": "🇩🇪", "US": "🇺🇸", "RU": "🇷🇺", "TR": "🇹🇷", 
        "FR": "🇫🇷", "GB": "🇬🇧", "NL": "🇳🇱", "FI": "🇫🇮"
    }
    if "#" in config:
        name_part = config.split("#")[-1].upper()
        for code, emoji in flags.items():
            if code in name_part:
                return config + f" {emoji}"
    return config

def decode_content(text):
    try:
        return base64.b64decode(text).decode('utf-8')
    except:
        return text

def scrape():
    raw_configs = []
    print(f"🚀 Начало сбора: {datetime.now().strftime('%H:%M:%S')}")
    
    for url in SOURCES:
        try:
            # verify=False игнорирует ошибки сертификатов
            res = requests.get(url, timeout=15, verify=False)
            if res.status_code == 200:
                content = decode_content(res.text)
                found = 0
                for line in content.splitlines():
                    line = line.strip()
                    if any(line.startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://', 'ssr://']):
                        # Добавляем флаг к названию
                        line = add_country_flags(line)
                        raw_configs.append(line)
                        found += 1
                print(f"✅ {url} -> Найдено: {found}")
        except Exception as e:
            print(f"❌ Ошибка на {url}: {e}")

    # Убираем дубликаты и пустые строки
    unique_configs = list(set([c for c in raw_configs if c]))

    # Сортировка: VLESS -> Trojan -> SS -> Остальное
    vless = [c for c in unique_configs if c.startswith('vless://')]
    trojan = [c for c in unique_configs if c.startswith('trojan://')]
    ss = [c for c in unique_configs if c.startswith('ss://')]
    others = [c for c in unique_configs if not any(c.startswith(p) for p in ['vless://', 'trojan://', 'ss://'])]

    final_list = vless + trojan + ss + others

    if final_list:
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_list))
        
        with open("last_update.txt", "w", encoding="utf-8") as f:
            f.write(datetime.now().isoformat())
        
        print(f"🏁 Успех! Собрано всего: {len(final_list)}")
    else:
        print("⚠ Новых конфигов не найдено.")

if __name__ == "__main__":
    scrape()
