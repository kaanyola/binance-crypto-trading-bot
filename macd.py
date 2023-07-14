from binance.client import Client
import talib
import numpy as np
import time
import sys
import config

# Binance API anahtarlarını buraya girin
API_KEY = config.API_KEY
API_SECRET = config.API_SECRET

# Binance API istemcisini oluşturun
client = Client(API_KEY, API_SECRET)

#

# Kripto para birimi çifti ve zaman dilimi
symbol = sys.argv[1]
interval = sys.argv[2]
# Başlangıç parametresi (dolar cinsinden)
starting_balance = 1000

# Alım ve satım işlemlerinde uygulanacak işlem ücreti yüzdesi
fee_percentage = 0.001  # %0.1

def calculate_macd(data):
    close_prices = np.array([float(d['close']) for d in data])
    macd, signal, _ = talib.MACD(close_prices)
    return macd[-1], signal[-1]

def run_bot():
    balance = starting_balance
    in_position = False
    totalPosition = 0
    while True:
        try:
            # Kripto para verilerini al
            klines = client.futures_klines(symbol=symbol, interval=interval, limit=100)
            data = [{'time': int(k[0]), 'open': float(k[1]), 'high': float(k[2]), 'low': float(k[3]), 'close': float(k[4]), 'volume': float(k[5])} for k in klines]

            # MACD ve sinyal değerlerini hesapla
            macd, signal = calculate_macd(data)
            if macd is not None and signal is not None:
                if macd > signal and not in_position:
                    # Alım işlemi
                    buy_price = data[-1]['close']
                    buy_quantity = (balance * (1 - fee_percentage)) / buy_price
                    balance = 0
                    print(f"Alım - MACD: {macd}, Sinyal: {signal}, Fiyat: {buy_price}, Miktar: {buy_quantity}")
                    in_position = True

                elif macd < signal and in_position:
                    # Satış işlemi
                    sell_price = data[-1]['close']
                    balance = (sell_price * buy_quantity * (1 - fee_percentage))
                    totalPosition += 1
                    print(f"Satış - MACD: {macd}, Sinyal: {signal}, Fiyat: {sell_price}, Bakiye: {balance}", "Trade Sayısı: ", totalPosition)
                    in_position = False

            time.sleep(10)  # Her dakika kontrol etmek için bekleyin

        except Exception as e:
            print(f'Hata: {e}')
            time.sleep(5)

# Botu çalıştır
run_bot()