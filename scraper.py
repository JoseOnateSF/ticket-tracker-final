from playwright.sync_api import sync_playwright
from config import STUBHUB_URL, EVENT_KEYWORDS, SECTION_TARGET
import re
import os

def get_prices():
    prices = []
    token = os.getenv("BROWSERLESS_TOKEN")
    
    if not token:
        print("ERROR: Falta configurar BROWSERLESS_TOKEN en Railway")
        return []

    # 🔥 Agregamos stealth=true para evadir las defensas antibot de StubHub
    ws_endpoint = f"wss://chrome.browserless.io?token={token}&stealth=true"

    with sync_playwright() as p:
        try:
            # Conexión al navegador remoto
            browser = p.chromium.connect_over_cdp(ws_endpoint)
            
            # 🔥 DISFRAZ AVANZADO: Simulamos ser un humano en una Mac con Chrome actualizado
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"macOS"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
            page = context.new_page()

            print("Scraper iniciando... navegando a la URL")
            # domcontentloaded suele ser más rápido y menos propenso a timeouts por scripts de terceros
            page.goto(STUBHUB_URL, wait_until="domcontentloaded", timeout=60000)

            # 🔥 Dar tiempo extra a React para renderizar los precios
            page.wait_for_timeout(10000)

            content = page.content()
            title = page.title()
            
            print(f"PAGE TITLE: {title}")

            browser.close()

            # 🔥 Detección de bloqueo de StubHub o CloudFront
            if "Pardon Our Interruption" in title or "Security" in title:
                print("ALERTA: StubHub activó el Captcha de seguridad.")
                return []
            elif "The request could not be satisfied" in title:
                print("ALERTA CRÍTICA: CloudFront bloqueó la IP de Browserless.")
                return []

            # 🔥 Hacer la búsqueda insensible a mayúsculas/minúsculas
            content_lower = content.lower()
            keywords_lower = [k.lower() for k in EVENT_KEYWORDS]
            section_lower = SECTION_TARGET.lower()

            if not any(k in content_lower for k in keywords_lower):
                print("EVENT NOT FOUND - Las palabras clave no están en la página")
                return []

            if section_lower not in content_lower:
                print(f"SECTION '{SECTION_TARGET}' NOT FOUND")
                return []

            # Extracción de precios
            raw_prices = re.findall(r"\$(\d+)", content)

            for p in raw_prices:
                price = int(p)
                if 20 < price < 5000:
                    prices.append(price)

            print("PRICES FOUND:", prices)

        except Exception as e:
            print(f"Error crítico en el scraper: {e}")

    return prices
