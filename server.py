import asyncio
import websockets
import json
import random
import time

# Simulate market data
async def send_market_data(websocket, path):  # Use 'path' instead of '_'
    while True:
        market_data = {
            "time": int(time.time() * 1000),
            "open": round(random.uniform(1000, 1200), 2),
            "high": round(random.uniform(1000, 1200), 2),
            "low": round(random.uniform(1000, 1200), 2),
            "close": round(random.uniform(1000, 1200), 2),
            "volume": round(random.uniform(10, 100), 4),
            "rsi": round(random.uniform(30, 70), 2),
            "macd": round(random.uniform(-5, 5), 5),
            "signal_line": round(random.uniform(-5, 5), 5),
            "trade_signal": "Buy" if random.random() > 0.5 else "Sell"
        }
        
        await websocket.send(json.dumps(market_data))
        await asyncio.sleep(1)

# Start WebSocket server
async def main():
    async with websockets.serve(send_market_data, "localhost", 8765):
        print("✅ WebSocket Server Running on ws://localhost:8765")
        await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(main())
