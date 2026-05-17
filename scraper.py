from playwright.sync_api import sync_playwright
from config import STUBHUB_URL, EVENT_KEYWORDS, SECTION_TARGET
import re
import os # Asegúrate de importar os

def get_prices():
    prices = []
    
    # Obtenemos el token de las variables de entorno
    token = os.getenv("BROWSERLESS_TOKEN")
    
    # URL de conexión a Browserless
    ws_endpoint = f"wss://chrome.browserless.io?token={token}"

    with sync_playwright() as p:
        # 🔥 EL CAMBIO CLAVE: Nos conectamos al navegador remoto en lugar de lanzarlo localmente
        browser = p.chromium.connect_over_cdp(ws_endpoint)

        page = browser.new_page()

        # Esperar carga real de red
        page.goto(STUBHUB_URL, wait_until="networkidle", timeout=60000)

        # Dar tiempo extra a React
        page.wait_for_timeout(8000)

        content = page.content()

        browser.close()

        print("SCRAPER LOADED PAGE")

        if not any(k in content for k in EVENT_KEYWORDS):
            print("EVENT NOT FOUND")
            return []

        if SECTION_TARGET not in content:
            print("SECTION NOT FOUND")
            return []

        raw_prices = re.findall(r"\$(\d+)", content)

        for p in raw_prices:
            price = int(p)
            if 20 < price < 5000:
                prices.append(price)

        print("PRICES FOUND:", prices)

    return prices
