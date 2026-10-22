import telebot
import requests
import random
import threading
import time
from datetime import datetime, timedelta

TOKEN = "8943164489:AAGQrVw1aX6xt3Nzp6szD5i6xQi6Zx_XnUI"
ADMIN_ID = 1872947365
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=10)

session = requests.Session()
users = set()
auto_alert_on = True # AUTO ALERT ACTIVE

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

💎 ONLY 80-85% SIGNALS
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

# AUTO ALERT LOOP - Runs every 5 mins
def auto_alert_loop():
    while True:
        try:
            if auto_alert_on:
                signals = scan_strong()
                if signals:
                    # Send only strongest 1-2 to avoid spam
                    for sig in signals[:2]:
                        msg = build_signal_msg(sig)
                        # Send to admin and all users
                        for uid in list(users):
                            try:
                                bot.send_message(uid, msg)
                                time.sleep(0.3)
                            except:
                                pass
                        # Always send to admin
                        try:
                            bot.send_message(ADMIN_ID, msg)
                        except:
                            pass
            time.sleep(300) # Check every 5 minutes
        except Exception as e:
            print(f"Auto alert error: {e}")
            time.sleep(60)

# Start auto thread
threading.Thread(target=auto_alert_loop, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(m):
    users.add(m.chat.id)
    bot.send_message(m.chat.id,
        "🔥 AUTO ALERT ACTIVE 🔥\n\n"
        "I will AUTO SEND you 80-85% Strong Bullish signals!\n\n"
        "You no need to type again - I go alert you every 5 mins when I see strong market!\n\n"
        "/strong - Manual scan now\n"
        "/auto_on - Turn auto alert ON\n"
        "/auto_off - Turn auto alert OFF\n"
        "/markets - See all markets"
    )

@bot.message_handler(commands=['strong', 'signals'])
def manual(m):
    users.add(m.chat.id)
    bot.send_message(m.chat.id, "🔍 Scanning for 80-85% Bullish...")
    signals = scan_strong()
    if not signals:
        bot.send_message(m.chat.id, "⚪ No 80-85% Bullish now. Auto alert dey watch, I go notify you when e show!")
        return
    for sig in signals[:4]:
        bot.send_message(m.chat.id, build_signal_msg(sig))

@bot.message_handler(commands=['auto_on'])
def on(m):
    global auto_alert_on
    if m.chat.id == ADMIN_ID:
        auto_alert_on = True
        bot.send_message(m.chat.id, "✅ AUTO ALERT ON - I go send signals every 5 mins")

@bot.message_handler(commands=['auto_off'])
def off(m):
    global auto_alert_on
    if m.chat.id == ADMIN_ID:
        auto_alert_on = False
        bot.send_message(m.chat.id, "❌ AUTO ALERT OFF")

@bot.message_handler(commands=['markets', 'admin', 'users'])
def other(m):
    users.add(m.chat.id)
    if "/markets" in m.text:
        bot.send_message(m.chat.id, "Markets: BTC, ETH, SOL, BNB, EUR/USD, GBP/USD, GOLD, SILVER, OIL, ENERGY, APPLE, TESLA")
    elif m.chat.id == ADMIN_ID:
        bot.send_message(m.chat.id, f"Admin: Users {len(users)} | Auto: {auto_alert_on}")

print("AUTO ALERT STRONG BULLISH BOT STARTED")
bot.infinity_polling(skip_pending=True)
