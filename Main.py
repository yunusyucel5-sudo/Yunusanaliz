import requests
import time
import json
from datetime import datetime

# Binance API URL
BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50
    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change >= 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def run_bot():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Bot arka planda aktif, Binance taranıyor...")
    try:
        response = requests.get(BINANCE_URL, timeout=10)
        data = response.json()
        try_coins = [c for c in data if c['symbol'].endswith('TRY')]
        
        print(f"Toplam {len(try_coins)} TL çifti bulundu. Analiz ediliyor...")
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    while True:
        run_bot()
        time.sleep(30) # 30 saniyede bir tara
