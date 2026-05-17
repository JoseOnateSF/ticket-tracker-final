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

    print("Scraper iniciando... Solicitando HTML renderizado a la API de Browserless")
    
    # Endpoint REST que imita el comportamiento de la página principal de Browserless
    api_url = f"https://chrome.browserless.io/content?token={token}"
    
    # Configuramos la petición con el "Disfraz" y la acción del clic integrada
    payload = {
        "url": STUBHUB_URL,
        "stealth": True,
        "rejectResourceTypes": ["image", "media", "font"], # Ahorra datos y acelera la carga
        "waitFor": 7000, # Espera 7 segundos a que React responda inicializado
        "actions": [
            {
                "click": "text=1" # 🔥 SIMULA EL CLIC: Busca el texto "1" del popup y le hace clic automáticamente
            }
        ]
    }

    try:
        # Enviamos la orden directa al motor de Browserless
        response = requests.post(api_url, json=payload, timeout=90)
        
        if response.status_code != 200:
            print(f"Error en la API de Browserless (Código {response.status_code})")
            return []

        content = response.text
        
        # Guardamos una pequeña muestra en el log para verificar qué cargó
        print("Página recibida con éxito de la API.")

        # Verificación de Cortafuegos en el HTML devuelto
        if "The request could not be satisfied" in content or "Pardon Our Interruption" in content:
            print("ALERTA CRÍTICA: CloudFront bloqueó la petición REST de Browserless.")
            return []

        # Convertimos todo a minúsculas para búsquedas flexibles que no fallen por una letra
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
        print(f"Error crítico en el scraper REST: {e}")

    return prices
