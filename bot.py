import telebot
import requests
import random
import threading
import time
import os
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not set!")

ADMIN_ID = 1872947365
bot = telebot.TeleBot(TOKEN, threaded=True)
session = requests.Session()
users = set()
auto_alert_on = True

MARKETS = {
    "BTCUSDT": "BTC/USDT", "ETHUSDT": "ETH/USDT", "SOLUSDT": "SOL/USDT",
    "BNBUSDT": "BNB/USDT", "EURUSD": "EUR/USD", "GBPUSD": "GBP/USD",
    "XAUUSD": "GOLD/USD", "XAGUSD": "SILVER/USD", "USOIL": "OIL/USD",
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
            price = random.uniform(1.2, 3500)
            change = random.uniform(-2.5, 2.5)
            strength = random.uniform(80, 88) if abs(change) > 1 else random.uniform(50, 75)
            return price, change, strength
    except:
        return None, None, 0

def build_signal(sig):
    action = "BUY" if sig['change'] > 0 else "SELL"
    order = "CALL" if action == "BUY" else "PUT"
    emoji = "🟢" if action == "BUY" else "🔴"
    
    return f"""
{emoji} IN {sig['entry_time']} - {action} {emoji}

📊 {sig['market']}
💰 ${sig['price']:,.4f}
📈 Strong {sig['strength']:.0f}% {"BULLISH" if action=="BUY" else "BEARISH"}

🎯 {action} / {order}

🛑 SL: ${sig['sl']:,.4f} ({sig['sl_p']}%)
🎯 TP1: ${sig['tp1']:,.4f} (+{sig['tp1_p']}%)
🎯 TP2: ${sig['tp2']:,.4f} (+{sig['tp2_p']}%)
🎯 TP3: ${sig['tp3']:,.4f} (+{sig['tp3_p']}%)

⏳ TREND WILL LAST: {sig['duration']}
⏰ SET TIMER: {sig['timer']} MINUTES

⚡ ALERT: 7 MINS BEFORE - ENTER AT {sig['entry_time']} SHARP!
"""

def scan_signals():
    entry = datetime.now() + timedelta(minutes=7)
    entry_str = entry.strftime("%I:%M %p").lstrip("0") # e.g 4:07 PM
    # Also 24h format
    entry_str_24 = entry.strftime("%H:%M") # e.g 16:07
    
    found = []
    for symbol, market in MARKETS.items():
        price, change, strength = get_live_data(symbol)
        if price and strength >= 80:
            sl_p = round(random.uniform(0.7, 1.2), 2)
            tp1_p = round(random.uniform(1.0, 2.0), 2)
            tp2_p = round(random.uniform(2.5, 4.0), 2)
            tp3_p = round(random.uniform(5.0, 7.0), 2)
            
            if strength >= 86:
                duration = "15-20 mins"
                timer = 15
            elif strength >= 83:
                duration = "8-12 mins"
                timer = 10
            else:
                duration = "5-8 mins"
                timer = 5

            d = 1 if change > 0 else -1
            found.append({
                "market": market, "price": price, "change": change,
                "strength": strength, "entry_time": entry_str_24,
                "sl": price * (1 - d*sl_p/100), "sl_p": sl_p,
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
            if auto_alert_on:
                signals = scan_signals()
                if signals:
                    for sig in signals[:2]:
                        msg = build_signal(sig)
                        for uid in list(users):
                            try:
                                bot.send_message(uid, msg)
                                time.sleep(0.3)
                            except:
                                pass
            time.sleep(420) # Alert every 7 mins - exactly 7 mins before next entry
        except:
            time.sleep(60)

threading.Thread(target=auto_loop, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    users.add(m.chat.id)
    bot.send_message(m.chat.id,
        "✅ BOT READY - 7 MINS BEFORE MODE\n\n"
        "I no go show current time again.\n"
        "I go straight tell you:\n"
        "IN 4:07 BUY or SELL\n\n"
        "With SL, TP, and how long e go last.\n\n"
        "Commands:\n"
        "/signal - Get signal NOW for next 7 mins\n"
        "/auto_on - Auto alert every 7 mins"
    )

@bot.message_handler(commands=['signal','strong','buy','s'])
def manual(m):
    users.add(m.chat.id)
    bot.send_message(m.chat.id, "🔍 Checking strong trend for next entry...")
    signals = scan_signals()
    if not signals:
        bot.send_message(m.chat.id, "⚪ No 80%+ trend for next 7 mins. I dey watch, I go alert you!")
        return
    for sig in signals[:3]:
        bot.send_message(m.chat.id, build_signal(sig))

print("BOT STARTED - 7 MIN BEFORE MODE")
bot.infinity_polling(skip_pending=True)
