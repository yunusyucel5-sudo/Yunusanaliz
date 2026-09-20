import os
import time
import threading
import ccxt
import pandas as pd
from flask import Flask
import firebase_admin
from firebase_admin import credentials, db

# --- FLASK WEB SERVER (Render Port Fix) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Binance Sinyal Botu ve Firebase Entegrasyonu Aktif!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- FIREBASE KURULUMU ---
FIREBASE_URL = "https://yunusanaliz-fade1-default-rtdb.firebaseio.com/"

if not firebase_admin._apps:
    firebase_admin.initialize_app(options={
        'databaseURL': FIREBASE_URL
    })

# --- BINANCE BOT ARAMA DÖNGÜSÜ ---
exchange = ccxt.binance()

def analyze_market():
    print("Binance piyasa taramasi baslatildi...")
    while True:
        try:
            markets = exchange.load_markets()
            try_pairs = [symbol for symbol in markets if symbol.endswith('/TRY')]
            
            signals = []
            for symbol in try_pairs[:15]:  # Ilk 15 çifti tara
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                change = ticker['percentage']
                
                # Sinyal verisini hazirla
                signals.append({
                    'symbol': symbol.replace('/', '_'),
                    'price': price,
                    'change': change,
                    'timestamp': int(time.time())
                })

            # Firebase Realtime Database'e gonder
            ref = db.reference('signals')
            ref.set({sig['symbol']: sig for sig in signals})
            print(f"[{time.strftime('%H:%M:%S')}] Firebase sinyalleri guncellendi.")
            
        except Exception as e:
            print("Hata oluştu:", e)
            
        time.sleep(60)  # Her 60 saniyede bir tara

if __name__ == "__main__":
    # Flask sunucusunu arka planda baslat
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Binance analiz döngüsünü baslat
    analyze_market()
