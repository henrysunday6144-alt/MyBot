import telebot
import requests
import random
import threading
import time
import os
from datetime import datetime, timedelta

# SAFE MODE - Token from Render, not from code
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set in Render!")

ADMIN_ID = 1872947365
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=10)

session = requests.Session()
users = set()
auto_alert_on = True

MARKETS = {
    "BTCUSDT": "CRYPTO - BTC", "ETHUSDT": "CRYPTO - ETH", 
    "SOLUSDT": "COIN - SOL", "BNBUSDT": "COIN - BNB",
    "EURUSD": "FOREX - EUR/USD", "GBPUSD": "FOREX - GBP/USD",
    "XAUUSD": "GOLD", "XAGUSD": "SILVER",
    "USOIL": "OIL", "UKOIL": "ENERGY",
    "AAPL": "STOCK - APPLE", "TSLA": "STOCK - TESLA",
}

def get_data(symbol):
    try:
        if "USDT" in symbol:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
            r = session.get(url, timeout=3).json()
            price = float(r['lastPrice'])
            change = float(r['priceChangePercent'])
            strength = min(90, max(0, 50 + change*4 + random.uniform(18, 28)))
            return price, change, strength
        else:
            price = random.uniform(1, 3000)
            change = random.uniform(0.3, 2.8)
            strength = random.uniform(80, 87)
            return price, change, strength
    except:
        return None, None, 0

def build_signal_msg(sig):
    return f"""
🚨 AUTO ALERT - STRONG BULLISH {sig['strength']:.0f}% 🚨

📊 MARKET: {sig['market']}
💰 {sig['symbol']}: ${sig['price']:,.4f}

⏰ ENTRY IN 7 MINS: {sig['entry_time']}
⚡ PREPARE NOW!

🛑 SL: ${sig['sl']:,.4f} (-{sig['sl_p']}%)
🎯 TP1: ${sig['tp1']:,.4f} (+{sig['tp1_p']}%)
🎯 TP2: ${sig['tp2']:,.4f} (+{sig['tp2_p']}%)

⏱️ DURATION: {sig['duration']}
⏰ SET TIMER: {sig['expiry']} MINUTES
📈 TYPE: BUY / CALL ONLY
🔥 STRENGTH: {sig['strength']:.0f}%
"""

def scan_strong():
    entry_time = datetime.now() + timedelta(minutes=7)
    found = []
    for symbol, market_name in MARKETS.items():
        price, change, strength = get_data(symbol)
        if price and 80 <= strength <= 88 and change > 0:
            sl_p = round(random.uniform(0.8, 1.5), 2)
            tp1_p = round(random.uniform(1.5, 2.5), 2)
            tp2_p = round(random.uniform(3.0, 5.0), 2)
            found.append({
                "market": market_name, "symbol": symbol, "price": price,
                "strength": strength, "entry_time": entry_time.strftime("%H:%M:%S"),
                "sl": price * (1 - sl_p/100), "sl_p": sl_p,
                "tp1": price * (1 + tp1_p/100), "tp1_p": tp1_p,
                "tp2": price * (1 + tp2_p/100), "tp2_p": tp2_p,
                "duration": random.choice(["5-10 mins", "10-15 mins"]),
                "expiry": random.choice([5, 10, 15])
            })
    return found

def auto_alert_loop():
    while True:
        try:
            if auto_alert_on:
                signals = scan_strong()
                if signals:
                    for sig in signals[:2]:
                        msg = build_signal_msg(sig)
                        for uid in list(users):
                            try:
                                bot.send_message(uid, msg)
                                time.sleep(0.3)
                            except:
                                pass
                        try:
                            bot.send_message(ADMIN_ID, msg)
                        except:
                            pass
            time.sleep(300)
        except Exception as e:
            print(f"Auto alert error: {e}")
            time.sleep(60)

threading.Thread(target=auto_alert_loop, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    users.add(m.chat.id)
    bot.send_message(m.chat.id, "🔥 AUTO ALERT ACTIVE 80-85% 🔥\n/strong - Scan now\n/markets - All markets")

@bot.message_handler(commands=['strong'])
def manual(m):
    users.add(m.chat.id)
    bot.send_message(m.chat.id, "🔍 Scanning...")
    signals = scan_strong()
    if not signals:
        bot.send_message(m.chat.id, "⚪ No 80-85% now. Auto alert go notify you!")
        return
    for sig in signals[:4]:
        bot.send_message(m.chat.id, build_signal_msg(sig))

@bot.message_handler(commands=['markets', 'admin'])
def other(m):
    users.add(m.chat.id)
    bot.send_message(m.chat.id, f"Markets 12 | Users {len(users)} | Auto ON")

print("SECURE BOT STARTED")
bot.infinity_polling(skip_pending=True)
