import time
from binance.client import Client

# Binance API anahtarlarınızı buraya girin
api_key = 'Binance_API_Key'
api_secret = 'Binance_API_Secret'

# Binance bağlantısını oluşturun
client = Client(api_key, api_secret)

# Bollinger Bantları stratejisi için gerekli parametreler
symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1DAY
period = 20
upper_threshold = 1.01  # Üst banda dokunduğunda satış yapmak için threshold değeri
lower_threshold = 0.99  # Alt banda dokunduğunda alım yapmak için threshold değeri
quantity = 0.001  # Ticaret miktarı

# Kripto verilerini almak için fonksiyon
def get_crypto_data(symbol, interval, limit):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    return klines

# Bollinger Bantları hesaplama fonksiyonu
def calculate_bollinger_bands(data, period):
    close_prices = [float(entry[4]) for entry in data]
    sma = sum(close_prices[-period:]) / period
    std_dev = (sum((price - sma) ** 2 for price in close_prices[-period:]) / period) ** 0.5
    upper_band = sma + (2 * std_dev)
    lower_band = sma - (2 * std_dev)
    return upper_band, sma, lower_band

# Alım emri yerleştirme fonksiyonu
def place_buy_order(symbol, quantity):
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity
    )
    return order

# Satım emri yerleştirme fonksiyonu
def place_sell_order(symbol, quantity):
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity
    )
    return order

# Ana işlem fonksiyonu
def main():
    while True:
        # Kripto verilerini al
        crypto_data = get_crypto_data(symbol, interval, period)

        # Bollinger Bantlarını hesapla
        upper_band, sma, lower_band = calculate_bollinger_bands(crypto_data, period)

        # Son fiyatı al
        last_price = float(crypto_data[-1][4])

        # Alım satım kararını ver
        if last_price >= upper_band * upper_threshold:
            # Üst banda dokunuldu, satış yap
            print("Üst banda dokunuldu, satış yapılıyor...")
            place_sell_order(symbol, quantity)
        elif last_price <= lower_band * lower_threshold:
            # Alt banda dokunuldu, alım yap
            print("Alt banda dokunuldu, alım yapılıyor...")
            place_buy_order(symbol, quantity)
        else:
            print("Alım veya satım yapılmadı.")

        # Belirli bir aralıkta döngüyü beklet
        time.sleep(60)  # Örnekte her dakika çalıştırıldı, isteğinize göre değiştirebilirsiniz

# Ana işlem fonksiyonunu çağır
main()
