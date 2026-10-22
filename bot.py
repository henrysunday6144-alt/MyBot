import telebot
import requests
import time
import threading
import os
from flask import Flask
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    BOT_TOKEN = "PASTE_NEW_TOKEN_HERE_TEMP"

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)
@app.route('/')
def home():
    return "WAT BOT LIVE - REAL TA MODE"

def get_klines(symbol="BTCUSDT", limit=50):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit={limit}"
        r = requests.get(url, timeout=10).json()
        closes = [float(c[4]) for c in r]
        return closes
    except:
        return []

def calculate_rsi(prices, period=14):
    if len(prices) < period+1:
        return 50
    gains, losses = 0, 0
    for i in range(1, period+1):
        diff = prices[-i] - prices[-i-1]
        if diff > 0:
            gains += diff
        else:
            losses += abs(diff)
    if losses == 0:
        return 80
    rs = gains / losses
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def calculate_ema(prices, period=20):
    if len(prices) < period:
        return prices[-1]
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices:
        ema = price * k + ema * (1 - k)
    return ema

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "✅ WAT BOT - REAL TA MODE\nI go only alert when RSI + EMA confirm!")

def bot_thread():
    print("WAT BOT STARTED - REAL TA MODE")
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()

# START BOT IN BACKGROUND, FLASK IN MAIN
threading.Thread(target=bot_thread, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
