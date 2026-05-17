import os
import re
import requests
from config import STUBHUB_URL, EVENT_KEYWORDS, SECTION_TARGET

def get_prices():
    prices = []
    token = os.getenv("BROWSERLESS_TOKEN")
    
    if not token:
        print("ERROR: Falta configurar BROWSERLESS_TOKEN en Railway")
        return []

    print("Scraper iniciando... Conectando al endpoint /smart-scrape de Browserless")
    
    api_url = f"https://chrome.browserless.io/smart-scrape?token={token}"
    
    payload = {
        "url": STUBHUB_URL,
        "formats": ["html"]
    }

    cabeceras = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=cabeceras, timeout=90)
        
        if response.status_code != 200:
            print(f"Error en la API de Browserless (Código {response.status_code})")
            return []

        response_json = response.json()
        
        # 🔥 SOLUCIÓN: Extraemos el HTML directamente de la llave 'content' que vimos en el log
        content = response_json.get("content", "")

        if not content:
            print("Error: La llave 'content' llegó vacía.")
            return []

        print("Página HTML extraída con éxito de la API.")

        # Convertimos a minúsculas para búsquedas flexibles
        content_lower = content.lower()
        keywords_lower = [k.lower() for k in EVENT_KEYWORDS]
        section_lower = SECTION_TARGET.lower()

        if not any(k in content_lower for k in keywords_lower):
            print("EVENT NOT FOUND - Las palabras clave del concierto no aparecen en el HTML.")
            return []

        if section_lower not in content_lower:
            print(f"SECTION '{SECTION_TARGET}' NOT FOUND - La sección no aparece en el HTML.")
            return []

        # Extracción matemática de los precios ($X)
        raw_prices = re.findall(r"\$(\d+)", content)

        for p in raw_prices:
            price = int(p)
            if 20 < price < 5000:
                prices.append(price)

        print("PRICES FOUND:", prices)

    except Exception as e:
        print(f"Error crítico en el scraper /smart-scrape: {e}")

    return prices
