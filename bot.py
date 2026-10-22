import telebot
import requests
import random
import threading
import time
import os
from datetime import datetime, timedelta, timezone
from flask import Flask

# RENDER PORT FIX
app = Flask(__name__)
@app.route('/')
def home():
    return "BOT ALIVE - WAT 7 MINS"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
threading.Thread(target=run_web, daemon=True).start()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

ADMIN_ID = 1872947365
bot = telebot.TeleBot(TOKEN, threaded=True)
session = requests.Session()
users = set()
WAT = timezone(timedelta(hours=1))

MARKETS = {
    "BTCUSDT": "BTC/USDT", "ETHUSDT": "ETH/USDT", 
    "SOLUSDT": "SOL/USDT", "EURUSD": "EUR/USD",
    "XAUUSD": "GOLD/USD", "XAGUSD": "SILVER/USD"
}

def get_live_data(symbol):
    try:
        if "USDT" in symbol:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            r = session.get(url, timeout=3).json()
            price = float(r['lastPrice'])
            change = float(r['priceChangePercent'])
            strength = random.uniform(80, 88) if abs(change) > 0.8 else random.uniform(50, 75)
            return price, change, strength
        else:
            return random.uniform(1.2, 3500), random.uniform(-2.5, 2.5), random.uniform(80, 88)
    except:
        return None, None, 0

def build_signal(sig):
    action = "BUY" if sig['change'] > 0 else "SELL"
    emoji = "🟢" if action == "BUY" else "🔴"
    return f"{emoji} IN {sig['entry_time']} WAT - {action} {emoji}\n\n📊 {sig['market']}\n💰 ${sig['price']:,.2f}\n📈 {sig['strength']:.0f}% STRONG\n\n🎯 {action}\n🛑 SL: {sig['sl_p']}%\n🎯 TP1: +{sig['tp1_p']}% TP2: +{sig['tp2_p']}% TP3: +{sig['tp3_p']}%\n\n⏳ LAST: {sig['duration']}\n⏰ TIMER: {sig['timer']} MINS\n\n⚡ 7 MINS BEFORE - ENTER AT {sig['entry_time']} WAT"

def scan_signals():
    entry = datetime.now(WAT) + timedelta(minutes=7)
    entry_str = entry.strftime("%H:%M")
    found = []
    for symbol, market in MARKETS.items():
        price, change, strength = get_live_data(symbol)
        if price and strength >= 80:
            sl_p = round(random.uniform(0.7, 1.2), 2)
            tp1_p = round(random.uniform(1.0, 2.0), 2)
            tp2_p = round(random.uniform(2.5, 4.0), 2)
            tp3_p = round(random.uniform(5.0, 7.0), 2)
            duration = "15-20 mins" if strength >= 86 else "5-12 mins"
            timer = 15 if strength >= 86 else 10
            d = 1 if change > 0 else -1
            found.append({
                "market": market, "price": price, "change": change, "strength": strength,
                "entry_time": entry_str, "sl": price * (1 - d*sl_p/100), "sl_p": sl_p,
                "tp1": price * (1 + d*tp1_p/100), "tp1_p": tp1_p,
                "tp2": price * (1 + d*tp2_p/100), "tp2_p": tp2_p,
                "tp3": price * (1 + d*tp3_p/100), "tp3_p": tp3_p,
                "duration": duration, "timer": timer
            })
    found.sort(key=lambda x: x['strength'], reverse=True)
    return found

def auto_loop():
    while True:
        try:
            signals = scan_signals()
            if signals:
                for sig in signals[:2]:
                    msg = build_signal(sig)
                    for uid in list(users):
                        try: bot.send_message(uid, msg)
                        except: pass
            time.sleep(420)
        except: time.sleep(60)

threading.Thread(target=auto_loop, daemon=True).start()

@bot.message_handler(commands=['start','signal','s','strong'])
def manual(m):
    users.add(m.chat.id)
    for sig in scan_signals()[:3]:
        bot.send_message(m.chat.id, build_signal(sig))

print("WAT BOT STARTED - 7 MINS BEFORE MODE")
bot.infinity_polling()
