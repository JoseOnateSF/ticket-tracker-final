from flask import Flask, jsonify, Response
import threading
import time
import requests

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

# PROXY INTERMEDIO PARA EL AUDIO
@app.route("/play_hooligan")
def play_hooligan():
    url_real = "https://stream.nct.vn/resa/2603/38/c5/c8y91sy70s_hq.mp3"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "" 
    }
    try:
        req = requests.get(url_real, headers=headers, stream=True, timeout=15)
        def generate():
            for chunk in req.iter_content(chunk_size=4096):
                yield chunk
        return Response(generate(), content_type="audio/mpeg")
    except Exception as e:
        print("PROXY AUDIO ERROR:", e)
        return "Error cargando streaming", 500


@app.route("/")
def home():
    best = data.get("best")
    prices = data.get("prices", [])
    drop = data.get("drop", 0)
    status = data.get("status", "desconocido")
    
    status_label = "Radar Conectado" if status == "running" else f"Estado: {status}"

    # Bloque HTML Principal Inicial
    html_premium = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arirang Ticket Radar | BTS 2026</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .bts-gradient {{
            background: linear-gradient(135deg, #18181b 0%, #030303 100%);
        }}
        .spinning {{
            animation: spin 8s linear infinite;
        }}
        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        /* 🔥 Remueve por completo el recuadro blanco exterior aislando solo el logo de las compuertas */
        .blend-logo {{
            filter: invert(1) brightness(2) contrast(150%);
            mix-blend-mode: lighten;
        }}
    </style>
</head>
<body class="bts-gradient text-zinc-100 font-sans min-h-screen relative selection:bg-purple-500/30 pb-24">

    <div class="absolute top-0 right-0 w-96 h-96 bg-purple-900/10 rounded-full blur-3xl pointer-events-none"></div>

    <audio id="arirang-audio" loop src="/play_hooligan"></audio>

    <div class="max-w-4xl mx-auto px-4 py-8 relative z-10">
        
        <header class="flex flex-col md:flex-row md:justify-between md:items-center border-b border-zinc-800 pb-6 mb-8 gap-4">
            <div class="flex items-center gap-4">
                <div class="w-16 h-16 flex items-center justify-center overflow-hidden bg-transparent">
                    <img src="https://e7.pngegg.com/pngimages/932/472/png-clipart-bts-logo-k-pop-design-bts-logo-angle-white-thumbnail.png" alt="BTS Logo" class="w-full h-full object-contain blend-logo">
                </div>
                <div>
                    <div class="flex items-center gap-2 text-zinc-400 font-medium text-xs tracking-widest uppercase">
                        <i class="fa-solid fa-wand-magic-sparkles"></i> ARIRANG SPECIAL EDITION
                    </div>
                    <h1 class="text-3xl font-black tracking-tight text-white bg-gradient-to-r from-white via-zinc-400 to-zinc-200 bg-clip-text text-transparent">BTS Stanford 2026</h1>
                    <p class="text-zinc-500 text-sm mt-0.5"><i class="fa-solid fa-gantry mr-1 text-purple-600"></i> Stanford Football Stadium — Sección 120</p>
                </div>
            </div>
            
            <div class="bg-zinc-950/80 border border-zinc-800 backdrop-blur-md rounded-full px-4 py-2 flex items-center gap-2 self-start md:self-auto shadow-inner">
                <span class="relative flex h-2.5 w-2.5">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
                <span class="text-xs font-semibold tracking-wide uppercase text-zinc-400">{status_label}</span>
            </div>
        </header>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            <div class="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm hover:border-purple-500/20 transition-all group">
                <div class="flex justify-between items-center text-zinc-500 mb-2">
                    <span class="text-xs font-bold tracking-wider uppercase">Mejor Precio Web</span>
                    <i class="fa-solid fa-bolt text-purple-400 group-hover:scale-110 transition-transform"></i>
                </div>
                <div class="text-4xl font-black text-white tracking-tight">
                    {"$" + str(best) if best else '<span class="text-xl font-normal text-zinc-600">Escaneando...</span>'}
                </div>
                <p class="text-[11px] text-purple-500/80 mt-2 font-medium"><i class="fa-solid fa-circle-check mr-1"></i>Sincronizado al instante con StubHub</p>
            </div>

            <div class="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm hover:border-amber-500/20 transition-all group">
                <div class="flex justify-between items-center text-zinc-500 mb-2">
                    <span class="text-xs font-bold tracking-wider uppercase">Objetivo Army</span>
                    <i class="fa-solid fa-crown text-amber-400 group-hover:scale-110 transition-transform"></i>
                </div>
                <div class="text-4xl font-black text-amber-500 tracking-tight">
                    ${BASE_PRICE}
                </div>
                <p class="text-[11px] text-amber-500/80 mt-2 font-medium"><i class="fa-solid fa-bell mr-1"></i>Alerta directa al supergrupo</p>
            </div>

            <div class="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm hover:border-zinc-700 transition-all sm:col-span-2 lg:col-span-1">
                <div class="flex justify-between items-center text-zinc-500 mb-2">
                    <span class="text-xs font-bold tracking-wider uppercase">Drop Porcentual</span>
                    <i class="fa-solid fa-chart-line text-zinc-400"></i>
                </div>
                <div class="text-4xl font-black text-white tracking-tight">
                    {f'<span class="text-emerald-400">{drop}%</span>' if drop and drop > 0 else '<span class="text-zinc-600 text-2xl font-bold">0.00%</span>'}
                </div>
                <p class="text-[11px] text-zinc-600 mt-2">Diferencia respecto a la Base</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            
            <main class="lg:col-span-2 bg-zinc-950/60 border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-md">
                <div class="px-6 py-4 bg-zinc-900/20 border-b border-zinc-800 flex justify-between items-center">
                    <h2 class="text-sm font-bold uppercase tracking-widest text-zinc-300"><i class="fa-solid fa-ticket-simple mr-2 text-amber-500"></i>Boletos Disponibles — Sección 120</h2>
                    <span class="bg-zinc-900 text-zinc-400 text-xs px-2.5 py-1 rounded-full font-bold border border-zinc-800">
                        {len(prices) if prices else 0} EN LISTA
                    </span>
                </div>

                <div class="divide-y divide-zinc-900">"""

    if prices:
        for price in prices:
            html_premium += f"""
                    <a href="{STUBHUB_URL}" target="_blank" class="px-6 py-4 flex justify-between items-center hover:bg-zinc-900/40 transition-all group block cursor-pointer">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-purple-400 group-hover:bg-purple-500/20 group-hover:text-purple-300 transition-all">
                                <i class="fa-solid fa-cart-shopping text-xs group-hover:scale-110 transition-transform"></i>
                            </div>
                            <div>
                                <p class="font-semibold text-sm text-zinc-300 group-hover:text-white transition-colors flex items-center gap-1.5">
                                    1 Ticket disponible <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-zinc-600 group-hover:text-purple-400 transition-colors"></i>
                                </p>
                                <p class="text-xs text-zinc-500">Clic para ir a comprar en StubHub</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="text-2xl font-black text-white tracking-tight group-hover:text-purple-300 transition-colors">${price}</p>
                            <span class="text-[9px] uppercase tracking-widest font-bold text-amber-500/80">Comprar ya</span>
                        </div>
                    </a>"""
    else:
        html_premium += """
                    <div class="p-16 text-center">
                        <div class="text-zinc-800 text-5xl mb-3 animate-pulse">⟭⟬</div>
                        <p class="text-zinc-500 font-medium text-sm tracking-wide">Esperando respuesta del servidor...</p>
                    </div>"""

    html_premium += f"""
                </div>
            </main>

            <div class="bg-zinc-950/60 border border-zinc-800 rounded-2xl p-5 shadow-2xl backdrop-blur-md flex flex-col items-center justify-center text-center">
                <div class="text-zinc-600 font-bold text-[10px] tracking-widest uppercase mb-3"><i class="fa-solid fa-compact-disc mr-1 text-purple-600"></i> ARIRANG ALBUM CONCEPT</div>
                <div class="w-full h-64 rounded-xl overflow-hidden shadow-inner border border-zinc-800 bg-zinc-950 flex items-center justify-center p-1 group">
                    <img src="https://s1.ticketm.net/dam/a/cac/79200b54-8f97-4909-a952-46af7db06cac_TABLET_LANDSCAPE_LARGE_16_9.jpg" alt="BTS Arirang Official Album Cover" class="w-full h-full object-fill transition-transform duration-700 group-hover:scale-102">
                </div>
                <div class="mt-4">
                    <p class="text-xs font-extrabold text-white tracking-wide">ARIRANG (아리랑)</p>
                    <p class="text-[10px] text-purple-500 font-bold uppercase mt-0.5 tracking-widest">Concept Photo #1 — BTS Back</p>
                </div>
            </div>

        </div>

        <section class="bg-zinc-950/40 border border-zinc-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm mb-8">
            <h2 class="text-sm font-bold uppercase tracking-widest text-purple-500 mb-4"><i class="fa-solid fa-icons mr-2"></i> Army Space & Hype Zone</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div class="bg-zinc-900/60 border border-zinc-800 rounded-xl p-4 text-center">
                    <span class="text-3xl">⚔️🔥</span>
                    <p class="text-xs font-bold text-zinc-300 mt-2 tracking-wider">TRACK EN REPRODUCCIÓN</p>
                    <p class="text-[11px] text-zinc-500 mt-1 px-4">"Hooligan" de BTS sonando de fondo. ¡Prepárate para el rap agresivo y las cuerdas tradicionales!</p>
                </div>
                <div class="bg-zinc-900/60 border border-zinc-800 rounded-xl p-4 text-center">
                    <span class="text-3xl">💸😭</span>
                    <p class="text-xs font-bold text-zinc-300 mt-2 tracking-wider">ESTADO DE LA BILLETERA</p>
                    <p class="text-[11px] text-zinc-500 mt-1 px-4">"Army calculando cómo sobrevivir el mes después de ver los precios de la Sección 120 en StubHub"</p>
                </div>
            </div>
        </section>

        <footer class="mt-12 text-center text-zinc-600 text-[11px] font-medium tracking-wider flex flex-col sm:flex-row sm:justify-between gap-2 px-2">
            <p>© 2026 ARIRANG TRACKING RADAR — ARMY SPECIAL DEV EDITION</p>
            <p><i class="fa-solid fa-shield-heart mr-1 text-purple-800"></i> Conexión Encriptada Activa</p>
        </footer>

    </div>

    <div class="fixed bottom-4 right-4 bg-zinc-950/90 border border-zinc-800 backdrop-blur-md px-4 py-2.5 rounded-2xl shadow-xl flex items-center gap-3 max-w-xs z-50">
        <div id="disc-icon" class="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-700 to-zinc-700 flex items-center justify-center text-white text-xs border border-zinc-700 shadow-inner">
            <i class="fa-solid fa-compact-disc"></i>
        </div>
        <div class="flex-1 min-w-0 pr-2">
            <p class="text-xs font-bold text-white truncate">Hooligan (Track 2)</p>
            <p class="text-[10px] text-purple-400 font-semibold uppercase tracking-wider">BTS — ARIRANG ALBUM</p>
        </div>
        <button onclick="toggleAudio()" class="w-7 h-7 rounded-full bg-zinc-800 hover:bg-zinc-700 text-zinc-300 flex items-center justify-center transition-all text-xs border border-zinc-700">
            <i id="play-icon" class="fa-solid fa-play"></i>
        </button>
    </div>

    <script>
        const audio = document.getElementById('arirang-audio');
        const playIcon = document.getElementById('play-icon');
        const discIcon = document.getElementById('disc-icon');

        function toggleAudio() {{
            if (audio.paused) {{
                audio.play().then(() => {{
                    playIcon.classList.remove('fa-play');
                    playIcon.classList.add('fa-pause');
                    discIcon.add('spinning');
                }}).catch(e => console.log("Interacción requerida:", e));
            }} else {{
                audio.pause();
                playIcon.classList.remove('fa-pause');
                playIcon.classList.add('fa-play');
                discIcon.remove('spinning');
            }}
        }}
    </script>

</body>
</html>"""
    return html_premium

@app.route("/api")
def api():
    return jsonify(data)

@app.route("/health")
def health():
    return {"ok": True}
