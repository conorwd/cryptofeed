# Crypto Price WebSocket Server

A real-time cryptocurrency price streaming server that aggregates data from multiple exchanges and broadcasts it to connected clients via WebSocket.

## Features

- Real-time price updates from Coinbase, Binance, and Kraken
- WebSocket server for client connections
- Initial price snapshot on connection
- Health check endpoint for monitoring
- Railway-ready deployment configuration

## Supported Exchanges

- Coinbase
- Binance
- Kraken

## Message Types

### Price Update
```json
{
  "type": "price_update",
  "symbol": "BTC-USD",
  "exchange": "coinbase",
  "price": "50000.00",
  "timestamp": 1234567890.123
}
```

### Initial Snapshot
```json
{
  "type": "snapshot",
  "data": {
    "BTC-USD": {
      "coinbase": {"price": "50000.00", "timestamp": 1234567890.123},
      "binance": {"price": "50001.00", "timestamp": 1234567890.123}
    }
  }
}
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python crypto_price_server.py
```

## Railway Deployment

This server is configured for deployment on Railway.app:

1. Create a new project on Railway
2. Connect your repository
3. Railway will automatically detect the Procfile and deploy the service
4. The WebSocket server will be available at `wss://your-app-name.railway.app`

## Frontend Connection Example

```javascript
const wsUrl = 'wss://your-app-name.railway.app';
const ws = new WebSocket(wsUrl);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'snapshot') {
        console.log('Current prices:', data.data);
    } else if (data.type === 'price_update') {
        console.log(`New price for ${data.symbol} on ${data.exchange}: ${data.price}`);
    }
};

ws.onopen = function() {
    console.log('Connected to price feed');
};

ws.onclose = function() {
    console.log('Disconnected from price feed');
};
```

## Environment Variables

- `PORT`: The port number for the HTTP server (WebSocket server runs on PORT + 1)
- Default port is 8765 if not specified

## Health Check

The server provides a health check endpoint at `/health` that returns a 200 OK response.
