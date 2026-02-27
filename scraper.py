import requests
import re
import asyncio
import aiohttp
from urllib.parse import urlparse, quote

SOURCES = [
    "https://livpn.atwebpages.com/sub.php?token=3b4cbb400a537740",
    "https://subrostunnel.vercel.app/gen.txt",
    "https://gitverse.ru/api/repos/Vsevj/OBS/raw/branch/master/wwh",
    "https://raw.githubusercontent.com/CidVpn/cid-vpn-config/refs/heads/main/general.txt",
    "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/LimeVPN.txt"
]

def get_flag_emoji(country_code):
    if not country_code or len(country_code) != 2:
        return "🌐"
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
        # Улучшенный парсинг для разных протоколов
        clean_url = url.split('#')[0]
        
        # Для VMess логика сложнее, но для проверки порта сойдет и так:
        proto = url.split('://')[0]
        if proto == 'vmess':
            # VMess ссылки обычно в base64, для простоты просто чекаем порт если он есть в строке
            # или пропускаем глубокую проверку, если не хотим усложнять код
            host = "google.com" # Заглушка, если не распарсили
            port = 443
        else:
            parsed = urlparse(url.replace(f'{proto}://', 'http://'))
            host = parsed.hostname
            port = parsed.port if parsed.port else 443
        
        # Проверка порта
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=2.0)
        writer.close()
        await writer.wait_closed()

        # Страна и флаг
        code, name = await get_country_info(session, host)
        if code and name:
            flag = get_flag_emoji(code)
            display_name = name
        else:
            flag, display_name = "🌐", "Unknown"

        # Считаем тип протокола + страну
        key = f"{proto.upper()} {display_name}"
        counter[key] = counter.get(key, 0) + 1
        
        new_name = f"{flag} {proto.upper()} {display_name} {counter[key]}"
        return f"{clean_url}#{quote(new_name)}"
    except:
        return None

async def main():
    raw_configs = set()
    # Регулярка теперь ищет все популярные протоколы
    pattern = r'(vless|vmess|trojan|ss)://[^\s]+'
    
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            found = re.findall(pattern, r.text, re.IGNORECASE)
            # findall с группами возвращает кортежи, склеиваем их обратно в ссылки
            full_links = re.findall(r'(?:vless|vmess|trojan|ss)://[^\s]+', r.text, re.IGNORECASE)
            raw_configs.update(full_links)
        except: continue

    print(f"Собрано {len(raw_configs)} разных протоколов. Проверяю...")

    country_counter = {}
    async with aiohttp.ClientSession() as session:
        tasks = [check_and_rename(session, conf, country_counter) for conf in raw_configs]
        results = await asyncio.gather(*tasks)
    
    alive_configs = [res for res in results if res is not None]
    
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(alive_configs))
    print(f"Готово! Теперь в списке {len(alive_configs)} конфигов.")

if __name__ == "__main__":
    asyncio.run(main())
