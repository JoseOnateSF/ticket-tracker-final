# Dar tiempo extra a React
        page.wait_for_timeout(8000)

        content = page.content()
        
        # 🔥 NUEVO: Imprimir el título y URL exacta para saber si nos bloquearon
        print("SCRAPER LOADED PAGE")
        print(f"TITLE: {page.title()}")
        print(f"URL: {page.url}")

        browser.close()

        # 🔥 TEMPORAL: Vamos a apagar los filtros por un momento para ver si logra extraer precios
        # if not any(k in content for k in EVENT_KEYWORDS):
        #     print("EVENT NOT FOUND")
        #     return []

        # if SECTION_TARGET not in content:
        #     print("SECTION NOT FOUND")
        #     return []

        # extracción precios
        raw_prices = re.findall(r"\$(\d+)", content)
