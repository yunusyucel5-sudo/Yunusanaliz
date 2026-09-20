import os
import time
import threading
import ccxt
import pandas as pd
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

def analyze_market():
    print("Binance piyasa taramasi baslatildi...")
    while True:
        try:
            print("Piyasa verileri çekiliyor...")
            markets = exchange.load_markets()
            try_pairs = [symbol for symbol in markets if symbol.endswith('/TRY')]
            
            signals = []
            for symbol in try_pairs[:15]:  # İlk 15 çifti tara
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                change = ticker['percentage']
                
                signals.append({
                    'symbol': symbol.replace('/', '_'),
                    'price': price,
                    'change': change,
                    'timestamp': int(time.time())
                })

            # Firebase Realtime Database'e gönder
            print("Firebase'e veriler yazılıyor...")
            ref = db.reference('signals')
            ref.set({sig['symbol']: sig for sig in signals})
            print(f"[{time.strftime('%H:%M:%S')}] Firebase sinyalleri basariyla guncellendi!")
            
        except Exception as e:
            print("Hata oluştu:", e)
            
        time.sleep(60)

# --- UYGULAMA BAŞLANGICI ---
if __name__ == "__main__":
    # Binance analiz döngüsünü ayrı bir arka plan iş parçacığında (thread) başlat
    bot_thread = threading.Thread(target=analyze_market, daemon=True)
    bot_thread.start()
    
    # Flask sunucusunu çalıştır
    run_flask()
