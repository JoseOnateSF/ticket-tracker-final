from flask import Flask, jsonify
import multiprocessing
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


# 🤖 PROCESO SEPARADO (ESTO SÍ FUNCIONA EN RAILWAY)
def monitor():
    last_level = None

    while True:
        try:
            prices = get_prices()

            print("PRICES:", prices)

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
                data["status"] = "no data"

        except Exception as e:
            data["status"] = str(e)
            print("ERROR:", e)

        time.sleep(CHECK_INTERVAL)


# 🚀 ARRANQUE SEGURO EN RAILWAY
process = multiprocessing.Process(target=monitor)
process.start()


@app.route("/")
def home():
    return jsonify(data)


@app.route("/api")
def api():
    return jsonify(data)
