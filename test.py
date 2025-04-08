import websocket
import json

SYMBOL = "btcusdt"
INTERVAL = "1m"
WS_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL}@kline_{INTERVAL}"

def on_message(ws, message):
    print("✅ WebSocket Data Received:", message)  # Debugging

def on_error(ws, error):
    print("⚠️ WebSocket Error:", error)

def on_close(ws, close_status, close_msg):
    print("❌ Disconnected from Binance WebSocket")

def on_open(ws):
    print("✅ Connected to Binance WebSocket")

ws = websocket.WebSocketApp(WS_URL, on_message=on_message, on_error=on_error, on_close=on_close)
ws.run_forever()
