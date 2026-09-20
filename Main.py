import time
import requests
from flask import Flask

app = Flask(__name__)

# Firebase Veritabanı URL'niz
FIREBASE_DB_URL = "https://yunusanaliz-fade1-default-rtdb.firebaseio.com/signals.json"

def get_all_try_symbols():
    """Binance üzerindeki tüm aktif TRY paritelerini dinamik olarak çeker"""
    try:
        url = "https://data-api.binance.vision/api/v3/exchangeInfo"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Sadece TRY ile biten ve işlemde olan pariteleri filtrele
        try_symbols = [
            item['symbol'] for item in data['symbols'] 
            if item['symbol'].endswith('TRY') and item['status'] == 'TRADING'
        ]
        return try_symbols
    except Exception as e:
        print(f"Semboller çekilirken hata oluştu: {e}")
        return ["BTC_TRY", "ETH_TRY", "AVAX_TRY"] # Hata durumunda yedek liste

def fetch_crypto_data():
    symbols = get_all_try_symbols()
    all_signals = {}

    print(f"Toplam {len(symbols)} adet TRY paritesi taranıyor...")

    for symbol in symbols:
        try:
            # Binance Public Data API üzerinden 24 saatlik değişim ve fiyat verisini al
            ticker_url = f"https://data-api.binance.vision/api/v3/ticker/24hr?symbol={symbol}"
            res = requests.get(ticker_url, timeout=5)
            
            if res.status_code == 200:
                item = res.json()
                price = float(item['lastPrice'])
                change = float(item['priceChangePercent'])
                
                # Basit bir skorlama ve sinyal mantığı (Geliştirilebilir)
                # Değişim oranına göre dinamik bir skor üretiyoruz
                score = 50
                if change > 5:
                    score = 75  # AL
                elif change > 0:
                    score = 60  # BEKLE / NÖTR
                else:
                    score = 30  # RİSK / UYGUN DEĞİL

                # Firebase için anahtar ismi (Örn: BTC_TRY)
                key = symbol.replace('/', '_')
                
                all_signals[key] = {
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "score": score,
                    "timestamp": int(time.time())
                }
        except Exception as e:
            print(f"{symbol} verisi çekilemedi: {e}")

    # Firebase Realtime Database'e PUT isteği ile tüm verileri gönder
    try:
        response = requests.put(FIREBASE_DB_URL, json=all_signals, timeout=10)
        if response.status_code == 200:
            print(f"[{time.strftime('%H:%M:%S']}] Firebase sinyalleri başarıyla güncellendi!")
        else:
            print(f"Firebase'e yazılamadı, Kod: {response.status_code}")
    except Exception as e:
        print(f"Firebase bağlantı hatası: {e}")

@app.route('/')
def home():
    # Manuel tetikleme veya sağlık kontrolü için
    fetch_crypto_data()
    return "Python Sinyal Botu Aktif ve Çalışıyor!"

if __name__ == '__main__':
    # Render üzerinde çalıştırma yapılandırması
    app.run(host='0.0.0.0', port=5000)
