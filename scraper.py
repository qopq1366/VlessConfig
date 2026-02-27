import requests
import re
import asyncio
import aiohttp
from urllib.parse import urlparse, quote

# Источники ссылок
SOURCES = [
    "https://livpn.atwebpages.com/sub.php?token=3b4cbb400a537740",
    "https://subrostunnel.vercel.app/gen.txt",
    "https://gitverse.ru/api/repos/Vsevj/OBS/raw/branch/master/wwh"
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
    except:
        pass
    return None, None

async def check_and_rename(session, url, counter):
    try:
        parsed = urlparse(url.replace('vless://', 'http://'))
        host = parsed.hostname
        port = parsed.port if parsed.port else 443
        
        # Проверка порта
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=2.5)
        writer.close()
        await writer.wait_closed()

        # Страна и флаг
        code, name = await get_country_info(session, host)
        if code and name:
            flag = get_flag_emoji(code)
            if name not in counter: counter[name] = 1
            else: counter[name] += 1
            new_name = f"{flag} {name} {counter[name]}"
        else:
            new_name = f"🌐 Unknown Node"

        base_part = url.split('#')[0]
        return f"{base_part}#{quote(new_name)}"
    except:
        return None

async def main():
    raw_configs = set()
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            found = re.findall(r'vless://[^\s]+', r.text)
            raw_configs.update(found)
        except: continue

    print(f"Собрано {len(raw_configs)}. Проверяю...")

    country_counter = {}
    async with aiohttp.ClientSession() as session:
        tasks = [check_and_rename(session, conf, country_counter) for conf in raw_configs]
        results = await asyncio.gather(*tasks)
    
    alive_configs = [res for res in results if res is not None]
    with open("sub.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(alive_configs))
    print(f"Готово! Живых: {len(alive_configs)}")

if __name__ == "__main__":
    asyncio.run(main())
