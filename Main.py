import os
import time
import threading
import ccxt
from flask import Flask
import firebase_admin
from firebase_admin import db

# --- FLASK WEB SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Binance Sinyal Botu ve Firebase Entegrasyonu Aktif!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# --- FIREBASE KURULUMU ---
FIREBASE_URL = "https://yunusanaliz-fade1-default-rtdb.firebaseio.com/"

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={
        'databaseURL': FIREBASE_URL
    })

# --- BINANCE BOT ARAMA DÖNGÜSÜ ---
exchange = ccxt.binance()

TRY_PAIRS = [
    'BTC/TRY', 'ETH/TRY', 'USDT/TRY', 'SOL/TRY', 'AVAX/TRY', 
    'XRP/TRY', 'DOGE/TRY', 'PEPE/TRY', 'SHIB/TRY', 'ADA/TRY',
    'NEAR/TRY', 'MATIC/TRY', 'AR/TRY', 'FLOKI/TRY', 'SUI/TRY'
]

def analyze_market():
    print("Binance piyasa taramasi baslatildi...", flush=True)
    while True:
        try:
            print("Piyasa verileri çekiliyor...", flush=True)
            signals = []
            
            for symbol in TRY_PAIRS:
                try:
                    ticker = exchange.fetch_ticker(symbol)
                    price = ticker['last']
                    change = ticker['percentage']
                    
                    signals.append({
                        'symbol': symbol.replace('/', '_'),
                        'price': price,
                        'change': change,
                        'timestamp': int(time.time())
                    })
                except Exception as ex:
                    print(f"{symbol} çekilemedi:", ex, flush=True)

            print("Firebase'e veriler yazılıyor...", flush=True)
            ref = db.reference('signals')
            ref.set({sig['symbol']: sig for sig in signals})
            print(f"[{time.strftime('%H:%M:%S')}] Firebase sinyalleri basariyla guncellendi!", flush=True)
            
        except Exception as e:
            print("Genel hata oluştu:", e, flush=True)
            
        time.sleep(60)

# --- UYGULAMA BAŞLANGICI ---
if __name__ == "__main__":
    bot_thread = threading.Thread(target=analyze_market, daemon=True)
    bot_thread.start()
    run_flask()
