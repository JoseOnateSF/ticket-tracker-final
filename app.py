from flask import Flask, jsonify
import threading
import time

from scraper import get_prices
from notifier import send_telegram
from config import BASE_PRICE, CHECK_INTERVAL, STUBHUB_URL

app = Flask(__name__)

data = {
    "prices": [],
    "best": None,
    "drop": 0,
    "status": "starting"
}

def get_level(drop):
    if drop >= 30:
        return "💥 CRÍTICO"
    elif drop >= 20:
        return "🔴 FUERTE"
    elif drop >= 10:
        return "🟡 MEDIA"
    elif drop >= 5:
        return "🔵 LEVE"
    return None

def monitor():
    time.sleep(5)  # deja arrancar Flask

    last_level = None

    while True:
        try:
            prices = get_prices()

            if prices:
                best = min(prices)
                drop = ((BASE_PRICE - best) / BASE_PRICE) * 100

                data["prices"] = prices
                data["best"] = best
                data["drop"] = round(drop, 2)
                data["status"] = "running"

                level = get_level(drop)

                if level and level != last_level:
                    send_telegram(
                        f"{level}\n"
                        f"🎟 Price: ${best}\n"
                        f"📉 Drop: {round(drop,2)}%\n"
                        f"💰 Base: ${BASE_PRICE}\n"
                        f"{STUBHUB_URL}"
                    )
                    last_level = level
            else:
                data["status"] = "no data / scanning..."

        except Exception as e:
            print("MONITOR ERROR:", e)
            data["status"] = str(e)

        time.sleep(CHECK_INTERVAL)

# 🚀 ARRANQUE DEL HILO EN SEGUNDO PLANO
threading.Thread(target=monitor, daemon=True).start()

# 🔥 NUEVA RUTA VISTA: Cambiamos jsonify por el Dashboard Interactivo
@app.route("/")
def home():
    # Extraemos los valores actuales del diccionario en vivo
    best = data.get("best")
    prices = data.get("prices", [])
    drop = data.get("drop", 0)
    status = data.get("status", "desconocido")
    
    # Configuramos el color del indicador dinámico según el estado
    status_color = "bg-emerald-500" if status == "running" else "bg-amber-500"
    status_ping = "bg-emerald-400" if status == "running" else "bg-amber-400"
    status_label = "Bot Activo" if status == "running" else f"Estado: {status}"

    html_premium = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Radar de Boletos | BTS Stanford</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-slate-900 text-slate-100 font-sans min-h-screen">

        <div class="max-w-4xl mx-auto px-4 py-8">
            
            <header class="flex flex-col md:flex-row md:justify-between md:items-center border-b border-slate-800 pb-6 mb-8 gap-4">
                <div>
                    <div class="flex items-center gap-2 text-purple-400 font-semibold text-sm tracking-wider uppercase">
                        <i class="fa-solid fa-circle-nodes animate-pulse"></i> Sistema de Monitoreo
                    </div>
                    <h1 class="text-3xl font-bold tracking-tight mt-1 text-white">BTS Stanford 2026</h1>
                    <p class="text-slate-400 text-sm mt-1"><i class="fa-solid fa-location-dot mr-1"></i> Stanford Football Stadium — Sección 120</p>
                </div>
                
                <div class="bg-slate-800 border border-slate-700 rounded-full px-4 py-2 flex items-center gap-2 self-start md:self-auto shadow-sm">
                    <span class="relative flex h-3 w-3">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full {status_ping} opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-3 w-3 {status_color}"></span>
                    </span>
                    <span class="text-sm font-medium text-slate-300">{status_label}</span>
                </div>
            </header>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                
                <div class="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-md hover:border-purple-500/50 transition-all">
                    <div class="flex justify-between items-center text-slate-400 mb-2">
                        <span class="text-sm font-medium">Mejor Precio Web</span>
                        <i class="fa-solid fa-tags text-purple-400 text-lg"></i>
                    </div>
                    <div class="text-4xl font-extrabold text-white">
                        {"$" + str(best) if best else '<span class="text-xl font-normal text-slate-500">Escaneando...</span>'}
                    </div>
                    <p class="text-xs text-slate-400 mt-2">Sincronizado con tarifas estimadas</p>
                </div>

                <div class="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-md hover:border-amber-500/50 transition-all">
                    <div class="flex justify-between items-center text-slate-400 mb-2">
                        <span class="text-sm font-medium">Precio Alerta (Target)</span>
                        <i class="fa-solid fa-bell text-amber-400 text-lg"></i>
                    </div>
                    <div class="text-4xl font-extrabold text-amber-400">
                        ${BASE_PRICE}
                    </div>
                    <p class="text-xs text-slate-400 mt-2">Disparador para mensaje a Telegram</p>
                </div>

                <div class="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-md hover:border-blue-500/50 transition-all sm:col-span-2 lg:col-span-1">
                    <div class="flex justify-between items-center text-slate-400 mb-2">
                        <span class="text-sm font-medium">Estatus de Caída</span>
                        <i class="fa-solid fa-arrow-trend-down text-blue-400 text-lg"></i>
                    </div>
                    <div class="text-4xl font-extrabold text-white">
                        {f'<span class="text-emerald-400">{drop}%</span>' if drop and drop > 0 else '<span class="text-slate-500 text-2xl font-semibold">Sin cambios</span>'}
                    </div>
                    <p class="text-xs text-slate-400 mt-2">Diferencia respecto a la Base</p>
                </div>

            </div>

            <main class="bg-slate-800 border border-slate-700 rounded-2xl shadow-xl overflow-hidden">
                <div class="px-6 py-4 bg-slate-800/50 border-b border-slate-700 flex justify-between items-center">
                    <h2 class="text-lg font-semibold text-white"><i class="fa-solid fa-list-ul mr-2 text-purple-400"></i>Boletos Disponibles en Sección 120</h2>
                    <span class="bg-slate-700 text-slate-300 text-xs px-2.5 py-1 rounded-full font-medium">
                        {len(prices) if prices else 0} detectados
                    </span>
                </div>

                <div class="divide-y divide-slate-700/60">
    """

    # Inyectamos de forma dinámica cada fila de boletos
    if prices:
        for price in prices:
            html_premium += f"""
                    <div class="px-6 py-4 flex justify-between items-center hover:bg-slate-750 transition-colors group">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 group-hover:bg-purple-500/20 transition-all">
                                <i class="fa-solid fa-ticket"></i>
                            </div>
                            <div>
                                <p class="font-medium text-white">1 Entrada — Fila Seleccionada</p>
                                <p class="text-xs text-slate-400">Verificado vía Browserless /smart-scrape</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="text-2xl font-bold text-white tracking-tight">${price}</p>
                            <span class="text-[10px] uppercase tracking-wider font-semibold text-slate-500">Precio Final</span>
                        </div>
                    </div>
            """
    else:
        html_premium += """
                    <div class="p-12 text-center">
                        <div class="text-slate-600 text-4xl mb-3">
                            <i class="fa-solid fa-couch"></i>
                        </div>
                        <p class="text-slate-400 font-medium">Buscando listados...</p>
                        <p class="text-slate-500 text-xs mt-1">El bot está leyendo la información en segundo plano.</p>
                    </div>
        """

    html_premium += """
                </div>
            </main>

            <footer class="mt-8 text-center text-slate-500 text-xs flex flex-col sm:flex-row sm:justify-between gap-2 px-2">
                <p>© 2026 Radar Engine v2.5 — Diseñado para Luisa</p>
                <p><i class="fa-solid fa-clock mr-1"></i> Actualización automática en tiempo real</p>
            </footer>

        </div>

    </body>
    </html>
    """
    
    return html_premium

# Mantenemos las rutas API limpias por si necesitas los datos crudos en otro lado
@app.route("/api")
def api():
    return jsonify(data)

@app.route("/health")
def health():
    return {"ok": True}
