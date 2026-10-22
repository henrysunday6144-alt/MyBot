import telebot
import requests
import time
import threading
from flask import Flask
from datetime import datetime
import pytz

BOT_TOKEN = 8943164489:AAFZeHwLLm9g6zh9TWB6cuvzGLwkO3c_Xu0
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)
@app.route('/')
def home():
    return "WAT BOT LIVE - REAL TA MODE"

# --- REAL TECHNICAL ANALYSIS ---
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

def get_real_signal():
    wat = pytz.timezone('Africa/Lagos')
    now = datetime.now(wat)
    
    # Use BTC as main market trend - most accurate
    closes = get_klines("BTCUSDT", 50)
    if not closes:
        return None
    
    price = closes[-1]
    rsi = calculate_rsi(closes)
    ema = calculate_ema(closes, 20)
    prev_price = closes[-2]
    
    # REAL LOGIC - NO FAKE SELL
    momentum_up = price > prev_price and price > ema
    momentum_down = price < prev_price and price < ema
    
    if rsi > 60 and momentum_up:
        signal = "BUY"
        reason = f"RSI {rsi} (Buyers Strong) | Price above EMA {round(ema,2)}"
    elif rsi < 40 and momentum_down:
        signal = "SELL"
        reason = f"RSI {rsi} (Sellers Strong) | Price below EMA {round(ema,2)}"
    else:
        return None # NO SIGNAL if market dey confuse - better no signal than wrong signal
    
    # 7 MINS BEFORE LOGIC
    future_time = now.timestamp() + (7*60)
    future_wat = datetime.fromtimestamp(future_time, wat).strftime("%H:%M")
    
    return f"🟢 IN {future_wat} WAT - {signal} 🟢\n📊 {reason}\n💰 BTC {round(price,2)} - Real TA Confirmed\n⏰ Now: {now.strftime('%H:%M:%S')} WAT"

# --- TELEGRAM HANDLER ---
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "✅ WAT BOT STARTED - REAL TA MODE (No More Fake Signals)\nI go only alert when RSI + EMA confirm trend!")

def signal_loop():
    sent_times = set()
    while True:
        try:
            wat = pytz.timezone('Africa/Lagos')
            now = datetime.now(wat)
            key = now.strftime("%H:%M")
            
            if key not in sent_times:
                sig = get_real_signal()
                if sig:
                    # Send to all users who started bot - you need to save chat_ids
                    # For now, log it - you go see am for Render logs
                    print(sig)
                    sent_times.add(key)
                    # Keep set small
                    if len(sent_times) > 100:
                        sent_times.clear()
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

# START THREAD
threading.Thread(target=signal_loop, daemon=True).start()
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

print("WAT BOT STARTED - REAL TA MODE - 7 MINS BEFORE")
bot.remove_webhook()
time.sleep(2)
bot.infinity_polling()
