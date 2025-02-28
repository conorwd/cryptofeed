'''
Copyright (C) 2024 Your Name

Please see the LICENSE file for the terms and conditions
associated with this software.
'''
import asyncio
import websockets
import json
import os
from decimal import Decimal
from collections import defaultdict
from typing import Set, Dict, DefaultDict
from datetime import datetime
from aiohttp import web

from cryptofeed import FeedHandler
from cryptofeed.callback import TradeCallback
from cryptofeed.defines import TRADES
from cryptofeed.exchanges import Binance, Coinbase, Kraken

# Store connected websocket clients
connected_clients: Set[websockets.WebSocketServerProtocol] = set()
# Store latest prices for each symbol
latest_prices: DefaultDict[str, Dict] = defaultdict(dict)

# Get port from environment variable or use default
PORT = int(os.getenv('PORT', '8765'))
HOST = '0.0.0.0'  # Required for Railway deployment

async def register(websocket):
    """Register a new client websocket"""
    connected_clients.add(websocket)
    # Send current prices to new client
    await websocket.send(json.dumps({
        'type': 'snapshot',
        'data': latest_prices
    }))

async def unregister(websocket):
    """Unregister a client websocket"""
    connected_clients.remove(websocket)

async def ws_handler(websocket, path):
    """Handle websocket connections"""
    await register(websocket)
    try:
        async for message in websocket:
            # Handle client messages if needed
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await unregister(websocket)

async def broadcast_price(symbol: str, price: Decimal, exchange: str, timestamp: float):
    """Broadcast price updates to all connected clients"""
    # Update latest price
    latest_prices[symbol][exchange] = {
        'price': str(price),
        'timestamp': timestamp
    }
    
    # Broadcast to all connected clients
    message = json.dumps({
        'type': 'price_update',
        'symbol': symbol,
        'exchange': exchange,
        'price': str(price),
        'timestamp': timestamp
    })
    
    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            pass

async def trade_callback(t, receipt_timestamp):
    """Callback for trade data"""
    await broadcast_price(t.symbol, t.price, t.exchange, t.timestamp)

# Health check endpoint
async def health_check(request):
    """Health check endpoint for Railway"""
    return web.Response(text='OK', status=200)

async def start_server():
    # Create aiohttp app for health check
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    
    # Start WebSocket server
    async with websockets.serve(ws_handler, HOST, PORT + 1):
        # Setup feed handler
        f = FeedHandler()
        
        # Add feeds for different exchanges
        # You can modify the symbol list based on what you want to track
        symbols = ['BTC-USD', 'ETH-USD']
        
        f.add_feed(Coinbase(symbols=symbols, channels=[TRADES], callbacks={TRADES: TradeCallback(trade_callback)}))
        f.add_feed(Binance(symbols=symbols, channels=[TRADES], callbacks={TRADES: TradeCallback(trade_callback)}))
        f.add_feed(Kraken(symbols=symbols, channels=[TRADES], callbacks={TRADES: TradeCallback(trade_callback)}))
        
        # Run feed handler
        await f.run(start_loop=False)
        
        # Keep the server running
        await asyncio.Future()  # run forever

def main():
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main() 