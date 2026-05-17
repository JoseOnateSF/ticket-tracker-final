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

    print("Scraper iniciando... Enviando script de automatización a la API /function de Browserless")
    
    # 🔥 CAMBIO CLAVE: Usamos el endpoint /function que sí permite acciones y evasión avanzada
    api_url = f"https://chrome.browserless.io/function?token={token}"
    
    # Escribimos un micro-script en JavaScript que se ejecutará dentro de Browserless
    # Esto imita exactamente el comportamiento del botón "Run" de su página web
    js_code = f"""
    module.exports = async ({{ page }}) => {{
        // 1. Configurar un User-Agent humano real
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36');
        
        // 2. Navegar a la URL de StubHub
        console.log('Navegando...');
        await page.goto('{STUBHUB_URL}', {{ waitUntil: 'domcontentloaded', timeout: 60000 }});
        
        // 3. Esperar un momento a que aparezca el popup
        await page.waitForTimeout(4000);
        
        // 4. Hacer clic en el botón '1' para romper el popup de boletos y cargar React
        try {{
            await page.click('text=1', {{ timeout: 5000 }});
            console.log('¡Clic en selector de 1 boleto exitoso!');
            await page.waitForTimeout(6000); // Esperar a que carguen los precios reales
        }} catch (err) {{
            console.log('El popup no apareció, continuando...');
        }}
        
        // 5. Retornar el HTML completamente renderizado y con los precios expuestos
        const html = await page.content();
        return {{ data: html }};
    }};
    """

    payload = {
        "code": js_code
    }

    try:
        # Enviamos el script al motor de Browserless
        response = requests.post(api_url, json=payload, headers={{"Content-Type": "application/json"}}, timeout=90)
        
        if response.status_code != 200:
            print(f"Error en la API de Browserless (Código {response.status_code})")
            print(f"Detalle del error: {response.text}")
            return []

        # El endpoint /function devuelve un JSON con la estructura {"result": {"data": "HTML..."}}
        response_json = response.json()
        content = response_json.get("result", {}).get("data", "")
        
        if not content:
            print("Error: La API de Browserless respondió con éxito pero el HTML está vacío.")
            return []

        print("Página recibida y procesada con éxito a nivel de código.")

        # Verificación de Cortafuegos en el HTML devuelto
        if "The request could not be satisfied" in content or "Pardon Our Interruption" in content:
            print("ALERTA CRÍTICA: CloudFront bloqueó la petición incluso a través de /function.")
            return []

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
        print(f"Error crítico en el scraper /function: {e}")

    return prices
