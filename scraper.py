from playwright.sync_api import sync_playwright
from config import STUBHUB_URL, EVENT_KEYWORDS, SECTION_TARGET
import re

def get_prices():
    prices = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        # 🔥 esperar carga real de red
        page.goto(STUBHUB_URL, wait_until="networkidle", timeout=60000)

        # 🔥 dar tiempo extra a React
        page.wait_for_timeout(8000)

        content = page.content()  # mejor que inner_text

        browser.close()

        # 🔥 debug importante
        print("SCRAPER LOADED PAGE")

        # filtro evento
        if not any(k in content for k in EVENT_KEYWORDS):
            print("EVENT NOT FOUND")
            return []

        # filtro sección
        if SECTION_TARGET not in content:
            print("SECTION NOT FOUND")
            return []

        # extracción precios
        raw_prices = re.findall(r"\$(\d+)", content)

        for p in raw_prices:
            price = int(p)
            if 20 < price < 5000:
                prices.append(price)

        print("PRICES FOUND:", prices)

    return prices
