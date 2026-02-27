import requests
import re
import asyncio
import aiohttp
from datetime import datetime
from urllib.parse import urlparse, quote

import requests
import base64
import re
import os
from datetime import datetime

# ОГРОМНЫЙ СПИСОК ИСТОЧНИКОВ (собираем отовсюду)
SOURCES = [
    "https://livpn.atwebpages.com/sub.php?token=3b4cbb400a537740",
    "https://subrostunnel.vercel.app/gen.txt",
    "https://gitverse.ru/api/repos/Vsevj/OBS/raw/branch/master/wwh",
    "https://raw.githubusercontent.com/CidVpn/cid-vpn-config/refs/heads/main/general.txt",
    "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/LimeVPN.txt"
]

def decode_content(text):
    """Декодирует Base64, если это необходимо, или возвращает текст как есть"""
    try:
        # Пробуем декодировать (некоторые подписки целиком в base64)
        return base64.b64decode(text).decode('utf-8')
    except:
        return text

def scrape():
    raw_configs = []
    
    print("🚀 Начинаю масштабный сбор...")
    
    for url in SOURCES:
        try:
            print(f"📡 Запрос к: {url}")
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                content = decode_content(res.text)
                # Ищем всё, что похоже на конфиг через регулярные выражения
                found = re.findall(r'(vless://|vmess://|trojan://|ss://|ssr://)[\w\-\.\%\?\=\&\#\:\/]+', content)
                
                # Собираем найденные строки обратно в полные конфиги
                lines = content.splitlines()
                current_found = 0
                for line in lines:
                    line = line.strip()
                    if any(line.startswith(p) for p in ['vless://', 'vmess://', 'trojan://', 'ss://', 'ssr://']):
                        raw_configs.append(line)
                        current_found += 1
                print(f"✅ Найдено: {current_found}")
        except Exception as e:
            print(f"❌ Ошибка на {url}: {e}")

    # Убираем дубликаты
    unique_configs = list(set(raw_configs))
    
    # ГРУППИРОВКА ПО ПРОТОКОЛАМ (как ты просил)
    vless = [c for c in unique_configs if c.startswith('vless://')]
    trojan = [c for c in unique_configs if c.startswith('trojan://')]
    ss = [c for c in unique_configs if c.startswith('ss://')]
    ssr = [c for c in unique_configs if c.startswith('ssr://')]
    vmess = [c for c in unique_configs if c.startswith('vmess://')]
    
    # Собираем финальный список в строгом порядке
    final_output = vless + trojan + ss + ssr + vmess
    
    if not final_output:
        print("☠️ Ничего не найдено! Проверь источники.")
        return

    # Записываем подписки
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))
    
    # Записываем время для таймера (в самом конце)
    with open("last_update.txt", "w", encoding="utf-8") as f:
        f.write(datetime.now().isoformat())
        
    print(f"🏁 Успех! Собрано всего: {len(final_output)}")
    print(f"📊 Распределение: VLESS:{len(vless)}, Trojan:{len(trojan)}, SS:{len(ss)}, VMess:{len(vmess)}")

if __name__ == "__main__":
    scrape()

def get_flag_emoji(country_code):
    if not country_code or len(country_code) != 2:
        return None
    return "".join(chr(127397 + ord(c)) for c in country_code.upper())

async def get_country_info(session, ip):
    try:
        async with session.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode,country", timeout=2) as resp:
            data = await resp.json()
            if data.get('status') == 'success':
                return data['countryCode'], data['country']
    except: pass
    return None, None

async def check_and_rename(session, url, counter):
    try:
        clean_url = url.split('#')[0]
        proto = clean_url.split('://')[0].lower()
        
        if proto == 'vmess':
            host, port = "1.1.1.1", 443 # Заглушка для vmess
        else:
            parsed = urlparse(clean_url.replace(f'{proto}://', 'http://'))
            host, port = parsed.hostname, (parsed.port if parsed.port else 443)

        # Проверка порта
        try:
            conn = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(conn, timeout=2.0)
            writer.close()
            await writer.wait_closed()
        except: return None

        code, name = await get_country_info(session, host)
        flag = get_flag_emoji(code)
        
        if flag and name:
            key = f"{flag} {proto.upper()} {name}"
            counter[key] = counter.get(key, 0) + 1
            new_name = f"{key} {counter[key]}"
            sort_key = f"0_{name}_{proto}_{counter[key]}"
        else:
            counter["Unknown"] = counter.get("Unknown", 0) + 1
            new_name = f"🌐 {proto.upper()} Unknown Node {counter['Unknown']}"
            sort_key = f"1_Unknown_{proto}_{counter['Unknown']}"

        return (f"{clean_url}#{quote(new_name)}", sort_key)
    except: return None

async def main():
    raw_configs = set()
    pattern = r'(?:vless|vmess|trojan|ss|ssr)://[^\s]+'
    
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            raw_configs.update(re.findall(pattern, r.text, re.IGNORECASE))
        except: continue

    country_counter = {}
    async with aiohttp.ClientSession() as session:
        tasks = [check_and_rename(session, conf, country_counter) for conf in raw_configs]
        results = await asyncio.gather(*tasks)
    
    valid = sorted([r for r in results if r is not None], key=lambda x: x[1])
    final_links = [item[0] for item in valid]

    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(final_links))
    
    with open("last_update.txt", "w") as f:
        f.write(datetime.now().isoformat())
    
    print(f"Done! Servers: {len(final_links)}")

if __name__ == "__main__":
    asyncio.run(main())
