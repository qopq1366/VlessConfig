import requests
import base64
import os
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SOURCES = [
    "https://livpn.atwebpages.com/sub.php?token=3b4cbb400a537740",
    "https://subrostunnel.vercel.app/gen.txt",
    "https://gitverse.ru/api/repos/Vsevj/OBS/raw/branch/master/wwh",
    "https://raw.githubusercontent.com/CidVpn/cid-vpn-config/refs/heads/main/general.txt",
    "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/LimeVPN.txt",
    "http://livpnsub.dpdns.org/sub.php?token=d712619499224ddb",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/ee6d4bfcb84d006d669d5c38a3111b42917171a2/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/other",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS_mobile.txt",
    "http://allvpn.x10.mx/sub.php"
]

# Тот самый расширенный список стран из первого варианта
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
    "CANADA": "🇨🇦 CA", " UA ": "🇺🇦 UA", "UKRAINE": "🇺🇦 UA"
}

def process_line(line, idx):
    line_upper = line.upper()
    proto = line.split("://")[0].upper()
    found_geo = "🏳️ UNKNOWN"
    
    for key, val in COUNTRIES.items():
        if key in line_upper:
            found_geo = val
            break
            
    # Убираем старое имя и рекламу (все что после #)
    base_part = line.split("#")[0]
    # Формируем новое чистое имя
    new_name = f"{found_geo} {proto} {idx}"
    return f"{base_part}#{new_name}", found_geo != "🏳️ UNKNOWN"

def scrape():
    unique_configs = set()
    print("🚀 Сбор данных...")
    
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10, verify=False)
            if r.status_code == 200:
                content = r.text
                try: content = base64.b64decode(content).decode('utf-8')
                except: pass
                
                for l in content.splitlines():
                    l = l.strip()
                    if any(l.startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://']):
                        unique_configs.add(l)
        except: continue

    with_country = []
    without_country = []
    
    # Обрабатываем каждый конфиг
    for i, line in enumerate(list(unique_configs)):
        new_line, has_geo = process_line(line, i + 1)
        if has_geo:
            with_country.append(new_line)
        else:
            without_country.append(new_line)

    # Сортируем: сначала страны по алфавиту, потом неизвестные
    final_list = sorted(with_country) + sorted(without_country)

    if final_list:
        with open("sub.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_list))
        print(f"✅ Готово! Собрано: {len(final_list)}")
    else:
        print("❌ Ничего не найдено")

if __name__ == "__main__":
    scrape()
