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
            print(f"Detalle del error: {response.text}")
            return []

        response_json = response.json()
        
        # 🔥 NUEVO: Imprimimos las llaves del JSON para ver cómo estructuran la respuesta
        print("Estructura JSON recibida de la API:", response_json.keys())

        # Intentamos extraer el HTML buscando en las dos estructuras más comunes de Browserless
        content = ""
        
        # Opción A: Viene como un string directo en 'data' (Formato común en Smart Scrape)
        if "data" in response_json and isinstance(response_json["data"], str):
            content = response_json["data"]
        # Opción B: Viene dentro de un diccionario/objeto estructurado
        elif "data" in response_json and isinstance(response_json["data"], dict):
            content = response_json["data"].get("html", "")
        # Opción C: Formato estándar de respuesta combinada
        elif "html" in response_json:
            content = response_json["html"]

        if not content:
            # Si ninguna funcionó, imprimimos un pedazo del JSON para inspeccionarlo en el log
            print("Estructura cruda del JSON:", str(response_json)[:300])
            print("Error: El HTML no se encontró en las llaves conocidas.")
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
