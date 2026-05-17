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

# ARRANQUE DEL MONITOR EN SEGUNDO PLANO
threading.Thread(target=monitor, daemon=True).start()

@app.route("/")
def home():
    best = data.get("best")
    prices = data.get("prices", [])
    drop = data.get("drop", 0)
    status = data.get("status", "desconocido")
    
    status_color = "bg-emerald-500" if status == "running" else "bg-amber-500"
    status_label = "Radar Conectado" if status == "running" else f"Estado: {status}"

    html_premium = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Arirang Ticket Radar | BTS 2026</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            .bts-gradient {{
                background: linear-gradient(135deg, #1e1b4b 0%, #030712 100%);
            }}
            .gold-text {{
                color: #f59e0b;
            }}
            /* Animación para el disco cuando la música suena */
            .spinning {{
                animation: spin 6s linear infinite;
            }}
            @keyframes spin {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body class="bts-gradient text-slate-100 font-sans min-h-screen relative selection:bg-purple-500/30 pb-24">

        <div class="absolute top-0 right-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute bottom-20 left-0 w-96 h-96 bg-amber-600/5 rounded-full blur-3xl pointer-events-none"></div>

        <audio id="arirang-audio" loop src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"></audio>

        <div class="max-w-4xl mx-auto px-4 py-8 relative z-10">
            
            <header class="flex flex-col md:flex-row md:justify-between md:items-center border-b border-purple-900/40 pb-6 mb-8 gap-4">
                <div class="flex items-center gap-4">
                    <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-purple-600 to-amber-500 p-[2px] shadow-lg shadow-purple-900/40">
                        <div class="w-full h-full bg-slate-950 rounded-2xl flex items-center justify-center text-xl font-bold text-purple-400 tracking-wider">
                            ⟭⟬
                        </div>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 text-amber-400 font-medium text-xs tracking-widest uppercase">
                            <i class="fa-solid fa-wand-magic-sparkles"></i> Arirang Special Edition
                        </div>
                        <h1 class="text-3xl font-black tracking-tight text-white bg-gradient-to-r from-white via-purple-200 to-amber-200 bg-clip-text text-transparent">BTS Stanford 2026</h1>
                        <p class="text-slate-400 text-sm mt-0.5"><i class="fa-solid fa-gantry mr-1 text-purple-400"></i> Stanford Football Stadium — Sección 120</p>
                    </div>
                </div>
                
                <div class="bg-slate-950/80 border border-purple-500/20 backdrop-blur-md rounded-full px-4 py-2 flex items-center gap-2 self-start md:self-auto shadow-inner">
                    <span class="relative flex h-2.5 w-2.5">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                    </span>
                    <span class="text-xs font-semibold tracking-wide uppercase text-slate-300">{status_label}</span>
                </div>
            </header>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
                <div class="bg-slate-950/40 border border-purple-900/30 rounded-2xl p-6 shadow-xl backdrop-blur-sm hover:border-purple-500/40 transition-all group">
                    <div class="flex justify-between items-center text-slate-400 mb-2">
                        <span class="text-xs font-bold tracking-wider uppercase">Mejor Precio Web</span>
                        <i class="fa-solid fa-bolt text-purple-400 group-hover:scale-110 transition-transform"></i>
                    </div>
                    <div class="text-4xl font-black text-white tracking-tight">
                        {"$" + str(best) if best else '<span class="text-xl font-normal text-slate-500">Buscando...</span>'}
                    </div>
                    <p class="text-[11px] text-purple-400/80 mt-2 font-medium"><i class="fa-solid fa-circle-check mr-1"></i>Precios con tarifas incluidas</p>
                </div>

                <div class="bg-slate-950/40 border border-purple-900/30 rounded-2xl p-6 shadow-xl backdrop-blur-sm hover:border-amber-500/40 transition-all group">
                    <div class="flex justify-between items-center text-slate-400 mb-2">
                        <span class="text-xs font-bold tracking-wider uppercase">Tu Objetivo Army</span>
                        <i class="fa-solid fa-crown text-amber-400 group-hover:scale-110 transition-transform"></i>
                    </div>
                    <div class="text-4xl font-black gold-text tracking-tight">
                        ${BASE_PRICE}
                    </div>
                    <p class="text-[11px] text-amber-500/80 mt-2 font-medium"><i class="fa-solid fa-bell mr-1"></i>Mensajes directo al Grupo</p>
                </div>

                <div class="bg-slate-950/40 border border-purple-900/30 rounded-2xl p-6 shadow-xl backdrop-blur-sm hover:border-blue-500/40 transition-all sm:col-span-2 lg:col-span-1">
                    <div class="flex justify-between items-center text-slate-400 mb-2">
                        <span class="text-xs font-bold tracking-wider uppercase">Descuento de la Base</span>
                        <i class="fa-solid fa-chart-line text-blue-400"></i>
                    </div>
                    <div class="text-4xl font-black text-white tracking-tight">
                        {f'<span class="text-emerald-400">{drop}%</span>' if drop and drop > 0 else '<span class="text-slate-600 text-2xl font-bold">0.00%</span>'}
                    </div>
                    <p class="text-[11px] text-slate-500 mt-2">Margen actual frente al límite</p>
                </div>
            </div>

            <main class="bg-slate-950/60 border border-purple-900/40 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-md mb-8">
                <div class="px-6 py-4 bg-purple-950/20 border-b border-purple-900/30 flex justify-between items-center">
                    <h2 class="text-sm font-bold uppercase tracking-widest text-purple-200"><i class="fa-solid fa-ticket-simple mr-2 gold-text"></i>Lista de Asientos Disponibles</h2>
                    <span class="bg-purple-950 text-purple-300 text-xs px-2.5 py-1 rounded-full font-bold border border-purple-800/50">
                        {len(prices) if prices else 0} EN LISTA
                    </span>
                </div>

                <div class="divide-y divide-purple-950/40">
    """

    if prices:
        for price in prices:
            html_premium += f"""
                    <div class="px-6 py-4 flex justify-between items-center hover:bg-purple-950/10 transition-colors group">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 group-hover:bg-purple-500/20 transition-all">
                                <i class="fa-solid fa-music text-xs group-hover:animate-bounce"></i>
                            </div>
                            <div>
                                <p class="font-semibold text-sm text-slate-200 group-hover:text-white transition-colors">Sección 120 — Fila Filtrada (1 Ticket)</p>
                                <p class="text-xs text-slate-400">Verificado vía Browserless Smart Engine</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="text-2xl font-black text-white tracking-tight">${price}</p>
                            <span class="text-[9px] uppercase tracking-widest font-bold text-amber-500/80">Confirmado</span>
                        </div>
                    </div>
            """
    else:
        html_premium += """
                    <div class="p-16 text-center">
                        <div class="text-purple-900/60 text-5xl mb-3 animate-pulse">⟭⟬</div>
                        <p class="text-slate-400 font-medium text-sm tracking-wide">Esperando respuesta del servidor...</p>
                    </div>
        """

    # 🔥 NUEVA SECCIÓN: ZONA DE MEMES & ALBUM CONCEPT ART
    html_premium += """
                </div>
            </main>

            <section class="bg-slate-950/40 border border-purple-900/30 rounded-2xl p-6 shadow-xl backdrop-blur-sm mb-8">
                <h2 class="text-sm font-bold uppercase tracking-widest text-amber-400 mb-4"><i class="fa-solid fa-icons mr-2"></i> Arirang Concept Zone & Army Memes</h2>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    
                    <div class="bg-slate-900/80 border border-purple-500/10 rounded-xl overflow-hidden p-3 text-center">
                        <div class="w-full h-48 bg-gradient-to-br from-purple-900 to-slate-950 rounded-lg mb-2 flex flex-col items-center justify-center p-4 border border-purple-500/5">
                            <span class="text-4xl mb-1">💿</span>
                            <p class="text-xs font-bold text-purple-300 tracking-wider">ARIRANG ALBUM COVER</p>
                            <p class="text-[10px] text-slate-500 mt-1 px-4">Inserta aquí el arte promocional oficial del regreso de BTS</p>
                        </div>
                        <p class="text-xs font-semibold text-slate-300">Concept Photo #1</p>
                    </div>

                    <div class="bg-slate-900/80 border border-purple-500/10 rounded-xl overflow-hidden p-3 text-center">
                        <div class="w-full h-48 bg-gradient-to-br from-amber-950/30 to-slate-950 rounded-lg mb-2 flex flex-col items-center justify-center p-4 border border-amber-500/5">
                            <span class="text-4xl mb-1">😭💸</span>
                            <p class="text-xs font-bold text-amber-400 tracking-wider">YO REVISANDO ESTE RADAR</p>
                            <p class="text-[10px] text-slate-500 mt-1 px-4">"Mi cuenta bancaria viendo que la Sección 120 no baja de $300"</p>
                        </div>
                        <p class="text-xs font-semibold text-slate-300">Army Mood Status</p>
                    </div>

                </div>
            </section>

            <footer class="mt-12 text-center text-purple-400/40 text-[11px] font-medium tracking-wider flex flex-col sm:flex-row sm:justify-between gap-2 px-2">
                <p>© 2026 ARIRANG TRACKING RADAR — ARMY SPECIAL DEV EDITION</p>
                <p><i class="fa-solid fa-shield-heart mr-1 gold-text"></i> Monitoreo Activo</p>
            </footer>

        </div>

        <div class="fixed bottom-4 right-4 bg-slate-950/90 border border-purple-500/20 backdrop-blur-md px-4 py-2.5 rounded-2xl shadow-xl flex items-center gap-3 max-w-xs z-50">
            <div id="disc-icon" class="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-600 to-amber-500 flex items-center justify-center text-white text-xs">
                <i class="fa-solid fa-compact-disc"></i>
            </div>
            <div class="flex-1 min-w-0 pr-2">
                <p class="text-xs font-bold text-white truncate">Arirang (Title Track)</p>
                <p class="text-[10px] text-purple-400 font-semibold uppercase tracking-wider">BTS — New Album</p>
            </div>
            <button onclick="toggleAudio()" class="w-7 h-7 rounded-full bg-purple-600/20 hover:bg-purple-600/40 text-purple-400 flex items-center justify-center transition-all text-xs">
                <i id="play-icon" class="fa-solid fa-play"></i>
            </button>
        </div>

        <script>
            const audio = document.getElementById('arirang-audio');
            const playIcon = document.getElementById('play-icon');
            const discIcon = document.getElementById('disc-icon');

            function toggleAudio() {{
                if (audio.paused) {{
                    audio.play();
                    playIcon.classList.remove('fa-play');
                    playIcon.classList.add('fa-pause');
                    discIcon.classList.add('spinning');
                }} else {{
                    audio.pause();
                    playIcon.classList.remove('fa-pause');
                    playIcon.classList.add('fa-play');
                    discIcon.classList.remove('spinning');
                }}
            }}
        </script>

    </body>
    </html>
    """
    
    return html_premium

@app.route("/api")
def api():
    return jsonify(data)

@app.route("/health")
def health():
    return {"ok": True}
