import websocket
import json
import requests
import pandas as pd
import numpy as np

# Binance WebSocket URL
WS_URL = "wss://stream.binance.com:9443/ws/trumpusdt@kline_3m"

# Binance API for historical data
HISTORICAL_URL = "https://api.binance.com/api/v3/klines"

# Store closing prices
closing_prices = []

# Get historical data to initialize indicators
def fetch_historical_data(symbol="TRUMPUSDT", interval="3m", limit=30):
    response = requests.get(HISTORICAL_URL, params={"symbol": symbol, "interval": interval, "limit": limit})
    data = response.json()
    
    if isinstance(data, list):
        return [float(candle[4]) for candle in data]  # Extract closing prices
    else:
        print("⚠️ Failed to fetch historical data.")
        return []

# RSI Calculation
def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return None
    
    delta = np.diff(prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    
    avg_gain = np.mean(gain[-period:])
    avg_loss = np.mean(loss[-period:])
    
    if avg_loss == 0:
        return 100  # Prevent division by zero
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# MACD Calculation
def calculate_macd(prices, short_period=12, long_period=26, signal_period=9):
    if len(prices) < long_period:
        return None, None
    
    short_ema = pd.Series(prices).ewm(span=short_period, adjust=False).mean()
    long_ema = pd.Series(prices).ewm(span=long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    
    return macd.iloc[-1], signal.iloc[-1]

# Process WebSocket messages
def on_message(ws, message):
    global closing_prices
    msg = json.loads(message)
    kline = msg["k"]

    if not kline["x"]:  # Ignore unfinished candles
        return
    
    timestamp = kline["t"]
    open_price = float(kline["o"])
    high_price = float(kline["h"])
    low_price = float(kline["l"])
    close_price = float(kline["c"])
    volume = float(kline["v"])

    # Store closing price
    closing_prices.append(close_price)
    if len(closing_prices) > 100:
        closing_prices.pop(0)

    # Calculate indicators
    rsi = calculate_rsi(closing_prices) if len(closing_prices) >= 14 else None
    macd, signal = calculate_macd(closing_prices) if len(closing_prices) >= 26 else (None, None)

    # Generate Trading Signal
    signal_msg = "🔍 Neutral"
    if rsi is not None and macd is not None:
        if rsi < 30 and macd > signal:
            signal_msg = "✅ BUY Signal 📈"
        elif rsi > 70 and macd < signal:
            signal_msg = "❌ SELL Signal 📉"

    # Print to terminal
    print(f"\n🕒 Time: {timestamp}")
    print(f"📈 Open: {open_price}  📊 High: {high_price}  📉 Low: {low_price}  🔽 Close: {close_price}")
    print(f"📊 Volume: {volume}")
    
    if rsi is not None and macd is not None:
        print(f"📊 RSI: {rsi:.2f}  |  MACD: {macd:.5f}  |  Signal Line: {signal:.5f}")
        print(f"📢 Trade Signal: {signal_msg}")
    else:
        print("⏳ Waiting for more data to calculate indicators...")
    print("-" * 50)

# WebSocket Handlers
def on_error(ws, error):
    print(f"⚠️ WebSocket Error: {error}")

def on_close(ws, close_status, close_msg):
    print("❌ Disconnected from Binance WebSocket.")

def on_open(ws):
    print("✅ Connected to Binance WebSocket")

# Preload historical data
closing_prices = fetch_historical_data()

# Start WebSocket
ws = websocket.WebSocketApp(WS_URL, 
                            on_message=on_message, 
                            on_error=on_error, 
                            on_close=on_close)

ws.run_forever()
