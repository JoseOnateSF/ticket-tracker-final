import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
STUBHUB_URL = os.getenv("STUBHUB_URL")

BASE_PRICE = float(os.getenv("BASE_PRICE", 300))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))  # 1 hour default

# 🎯 filtros clave
EVENT_KEYWORDS = ["May 19", "Stanford", "BTS"]
SECTION_TARGET = "Section 120"
