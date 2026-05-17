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

def level(drop):
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

                lvl = level(drop)

                if lvl and lvl != last_level:
                    send_telegram(
                        f"{lvl}\n"
                        f"🎟 Price: ${best}\n"
                        f"📉 Drop: {round(drop,2)}%\n"
                        f"💰 Base: ${BASE_PRICE}\n"
                        f"{STUBHUB_URL}"
                    )
                    last_level = lvl

        except Exception as e:
            data["status"] = str(e)

        time.sleep(CHECK_INTERVAL)


@app.route("/")
def home():
    return jsonify(data)


@app.route("/api")
def api():
    return data


if __name__ == "__main__":
    t = threading.Thread(target=monitor)
    t.daemon = True
    t.start()

    app.run(host="0.0.0.0", port=8080)
