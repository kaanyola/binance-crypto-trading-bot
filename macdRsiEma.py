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

# Göstergelerin ayarları
macd_fast_period = 12
macd_slow_period = 26
macd_signal_period = 9
rsi_period = 14
ema_period = 200

def calculate_indicators(data):
    close_prices = np.array([float(d['close']) for d in data])
    macd, macd_signal, _ = talib.MACD(close_prices, fastperiod=macd_fast_period, slowperiod=macd_slow_period, signalperiod=macd_signal_period)
    rsi = talib.RSI(close_prices, timeperiod=rsi_period)
    ema = talib.EMA(close_prices, timeperiod=ema_period)
    return macd[-1], macd_signal[-1], rsi[-1], ema[-1]

def run_bot():
    balance = starting_balance
    in_position = False

    while True:
        try:
            # Kripto para verilerini al
            klines = client.futures_klines(symbol=symbol, interval=interval, limit=1000)
            data = [{'time': int(k[0]), 'open': float(k[1]), 'high': float(k[2]), 'low': float(k[3]), 'close': float(k[4]), 'volume': float(k[5])} for k in klines]

            # Göstergeleri hesapla
            macd, macd_signal, rsi, ema = calculate_indicators(data)

            if not np.isnan(macd) and not np.isnan(macd_signal) and not np.isnan(rsi) and not np.isnan(ema):
                if macd > macd_signal and rsi > 50 and data[-1]['close'] > ema and not in_position:
                    # Alım işlemi
                    buy_price = data[-1]['close']
                    buy_quantity = (balance * (1 - fee_percentage)) / buy_price
                    balance = 0
                    print(f"Alım - MACD: {macd}, MACD Signal: {macd_signal}, RSI: {rsi}, EMA: {ema}, Fiyat: {buy_price}, Miktar: {buy_quantity}")
                    in_position = True

                elif macd < macd_signal and rsi < 50 and data[-1]['close'] < ema and in_position:
                    # Satış işlemi
                    sell_price = data[-1]['close']
                    balance = (sell_price * buy_quantity * (1 - fee_percentage))
                    print(f"Satış - MACD: {macd}, MACD Signal: {macd_signal}, RSI: {rsi}, EMA: {ema}, Fiyat: {sell_price}, Bakiye: {balance}")
                    in_position = False

            time.sleep(5)  # Her dakika kontrol etmek için bekleyin

        except Exception as e:
            print(f'Hata: {e}')
            time.sleep(5)

# Botu çalıştır
run_bot()