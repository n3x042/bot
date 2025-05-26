import os
import asyncio
from datetime import datetime, time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = os.getenv('BOT_TOKEN', '7760111660:AAELWxJEt39cW8rNhePTxzw-iT_ZuFImC88')
CHAT_ID = os.getenv('CHAT_ID', '5244395202')

bot = Bot(token=BOT_TOKEN)

async def pobierz_promocje_xkom():
    url = 'https://www.x-kom.pl/szukaj?q=zasilacz'

    headers = {
        'user-agent': 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/115.0.0.0 safari/537.36',
        'accept-language': 'pl-pl,pl;q=0.9,en-us;q=0.8,en;q=0.7',
        'accept-encoding': 'gzip, deflate, br',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'connection': 'keep-alive',
        'referer': 'https://www.x-kom.pl/',
        'origin': 'https://www.x-kom.pl'
    }

    try:
        with requests.Session() as session:
            r = session.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            produkty = soup.select('div.sc-1fcmfeb-0')

            promocje = []
            for p in produkty[:5]:
                nazwa = p.select_one('h3').text.strip() if p.select_one('h3') else 'brak nazwy'
                cena_stara = p.select_one('div.sc-1fcmfeb-1 span.sc-1l9z0g2-1')
                cena_nowa = p.select_one('div.sc-1fcmfeb-1 span.sc-1l9z0g2-3')

                if cena_stara and cena_nowa:
                    cena_stara = cena_stara.text.strip()
                    cena_nowa = cena_nowa.text.strip()
                    promocje.append(f"{nazwa}\nstara cena: {cena_stara}, nowa cena: {cena_nowa}\n")
        return "🔥 promocje na x-kom:\n" + "\n".join(promocje) if promocje else "Brak promocji na x-kom"
    except Exception as e:
        return f"x-kom scraper error: {e}"


async def pobierz_promocje_morele():
    url = 'https://www.morele.net/search?q=zasilacz'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        produkty = soup.select('div.cat-product-list__item')

        promocje = []
        for p in produkty[:5]:
            nazwa = p.select_one('a.cat-product-list__name').text.strip() if p.select_one('a.cat-product-list__name') else 'brak nazwy'
            cena_stara = p.select_one('span.price-old')
            cena_nowa = p.select_one('span.price-new')

            if cena_stara and cena_nowa:
                cena_stara = cena_stara.text.strip()
                cena_nowa = cena_nowa.text.strip()
                promocje.append(f"{nazwa}\nstara cena: {cena_stara}, nowa cena: {cena_nowa}\n")
        return "🔥 promocje na morele:\n" + "\n".join(promocje) if promocje else "Brak promocji na morele"
    except Exception as e:
        return f"morele scraper error: {e}"

async def pobierz_promocje():
    xkom = await pobierz_promocje_xkom()
    morele = await pobierz_promocje_morele()

    return f"{xkom}\n\n{morele}"

async def wyslij_wiadomosc(tekst):
    await bot.send_message(chat_id=CHAT_ID, text=tekst)

async def zadanie_dnia():
    promocja = await pobierz_promocje()
    await wyslij_wiadomosc(promocja)
    print(f"[{datetime.now()}] wysłano wiadomość na telegram.")

async def czekaj_na_8():
    while True:
        teraz = datetime.now().time()
        cel = time(8, 0)

        if teraz >= cel and teraz < (time(8, 1)):
            await zadanie_dnia()
            await asyncio.sleep(61)
        else:
            await asyncio.sleep(30)

if __name__ == '__main__':
    try:
        print("⏱️ bot startuje i czeka na 08:00...")
        asyncio.run(zadanie_dnia())
    except KeyboardInterrupt:
        print("bot zatrzymany ręcznie.")
