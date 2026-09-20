import os
import time
import threading
import requests
from flask import Flask

# --- FLASK WEB SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Binance Sinyal Botu ve Firebase Entegrasyonu Aktif!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# --- FIREBASE REST API ADRESİ ---
FIREBASE_URL = "https://yunusanaliz-fade1-default-rtdb.firebaseio.com/signals.json"

# --- HEDEF PARİTELER ---
TARGET_SYMBOLS = [
    'BTCTRY', 'ETHTRY', 'USDTRY', 'SOLTRY', 'AVAXTRY',
    'XRPTRY', 'DOGETRY', 'PEPETRY', 'SHIBTRY', 'ADATRY',
    'NEARTRY', 'MATICTRY', 'ARTRY', 'FLOKITRY', 'SUITRY'
]

def fetch_binance_data():
    """Binance Public Data API üzerinden verileri çeker (Render/ABD engelini aşar)."""
    urls = [
        "https://data-api.binance.vision/api/v3/ticker/24hr",
        "https://api.binance.me/api/v3/ticker/24hr",
        "https://api.binance.com/api/v3/ticker/24hr"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"URL denenirken hata ({url}):", e, flush=True)
    return None

def analyze_market():
    print("Binance piyasa taramasi baslatildi...", flush=True)
    while True:
        try:
            print("Piyasa verileri çekiliyor...", flush=True)
            raw_data = fetch_binance_data()
            
            if raw_data:
                signals = {}
                for item in raw_data:
                    symbol = item.get('symbol', '')
                    if symbol in TARGET_SYMBOLS:
                        formatted_key = symbol.replace('TRY', '_TRY')
                        signals[formatted_key] = {
                            'symbol': symbol,
                            'price': float(item.get('lastPrice', 0)),
                            'change': float(item.get('priceChangePercent', 0)),
                            'timestamp': int(time.time())
                        }
                
                # Firebase'e Dosyasız/Anahtarsız REST API ile Veri Yazma
                print("Firebase'e veriler yazılıyor...", flush=True)
                fb_res = requests.put(FIREBASE_URL, json=signals, timeout=10)
                
                if fb_res.status_code == 200:
                    print(f"[{time.strftime('%H:%M:%S')}] Firebase sinyalleri basariyla guncellendi!", flush=True)
                else:
                    print(f"Firebase hatası ({fb_res.status_code}):", fb_res.text, flush=True)
            else:
                print("Binance'den veri alınamadı!", flush=True)
                
        except Exception as e:
            print("Genel hata oluştu:", e, flush=True)
            
        time.sleep(60)

# --- UYGULAMA BAŞLANGICI ---
if __name__ == "__main__":
    bot_thread = threading.Thread(target=analyze_market, daemon=True)
    bot_thread.start()
    run_flask()
