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
    
    # Endpoint REST oficial de Browserless para extraer contenido
    api_url = f"https://chrome.browserless.io/content?token={token}"
    
    # Estructura de carga (Payload) con el formato de acciones corregido
    payload = {
        "url": STUBHUB_URL,
        "stealth": True,
        "rejectResourceTypes": ["image", "media", "font"],  # Optimiza el consumo de datos
        "waitFor": 7000,  # Espera inicial para que cargue la estructura de la página
        "actions": [
            {
                "type": "click",
                "selector": "text=1"  # 🔥 Formato correcto: Hace clic en el "1" para desbloquear precios
            }
        ]
    }

    try:
        # Enviamos la petición POST emulando la herramienta de su web principal
        response = requests.post(api_url, json=payload, timeout=90)
        
        if response.status_code != 200:
            print(f"Error en la API de Browserless (Código {response.status_code})")
            print(f"Detalle del error: {response.text}")
            return []

        content = response.text
        print("Página recibida y procesada con éxito por la API de Browserless.")

        # Verificación de Cortafuegos en el HTML devuelto por si acaso
        if "The request could not be satisfied" in content or "Pardon Our Interruption" in content:
            print("ALERTA CRÍTICA: CloudFront logró bloquear la petición de la API.")
            return []

        # Convertimos a minúsculas para que las búsquedas no fallen por diferencias de letras
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
