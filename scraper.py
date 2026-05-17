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
        page.goto(STUBHUB_URL)

        # esperar render React
        page.wait_for_timeout(12000)

        content = page.inner_text("body")

        browser.close()

        # 🔥 FILTRO 1: evento correcto
        if not any(k in content for k in EVENT_KEYWORDS):
            return []

        # 🔥 FILTRO 2: sección correcta
        if SECTION_TARGET not in content:
            return []

        # 🔥 extracción precios
        raw_prices = re.findall(r"\$(\d+)", content)

        for p in raw_prices:
            price = int(p)

            if 20 < price < 5000:
                prices.append(price)

    return prices
