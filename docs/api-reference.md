# ZION API Reference v2.9

Dokumentace REST API, WebSocket a SDK pro integraci s ZION TerraNova.

---

## 🌐 Base URLs

| Environment | URL |
|-------------|-----|
| **MainNet** | `https://api.zionterranova.com/v1` |
| **TestNet** | `https://testnet-api.zionterranova.com/v1` |
| **Local Dev** | `http://localhost:18081/v1` |

---

## 🔐 Authentication

API používá Bearer token autentizaci pro chráněné endpointy.

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.zionterranova.com/v1/account/balance/YOUR_ADDRESS
```

### Rate Limits

| Tier | Limit | Popis |
|------|-------|-------|
| Public | 100 req/h | Bez API klíče |
| Basic | 1,000 req/h | Free API klíč |
| Pro | 10,000 req/h | Placený tier |
| Enterprise | Unlimited | Kontaktujte nás |

---

## 📡 REST API Endpoints

### Network

#### Get Network Stats
```http
GET /network/stats
```

**Response:**
```json
{
  "block_height": 123456,
  "hashrate": "500000000",
  "difficulty": "1234567890",
  "active_miners": 1234,
  "network_version": "2.9.0",
  "timestamp": "2025-12-28T12:00:00Z"
}
```

#### Get Block by Height
```http
GET /block/{height}
```

**Response:**
```json
{
  "height": 123456,
  "hash": "0x1a2b3c4d...",
  "previous_hash": "0x9f8e7d6c...",
  "timestamp": "2025-12-28T12:00:00Z",
  "transactions": 42,
  "miner": "ZION_abc123...",
  "reward": "1619.63",
  "difficulty": "1234567890"
}
```

#### Get Block by Hash
```http
GET /block/hash/{hash}
```

---

### Account

#### Get Balance
```http
GET /account/balance/{address}
```

**Response:**
```json
{
  "address": "ZION_abc123xyz...",
  "balance": "12345.678901",
  "pending": "100.000000",
  "consciousness_level": 5,
  "consciousness_xp": 75000,
  "last_updated": "2025-12-28T12:00:00Z"
}
```

#### Get Transaction History
```http
GET /account/transactions/{address}?limit=50&offset=0
```

**Query Parameters:**
| Param | Type | Default | Popis |
|-------|------|---------|-------|
| `limit` | int | 50 | Max 100 |
| `offset` | int | 0 | Pagination offset |
| `type` | string | all | `incoming`, `outgoing`, `all` |

**Response:**
```json
{
  "address": "ZION_abc123...",
  "transactions": [
    {
      "hash": "0x...",
      "type": "incoming",
      "amount": "100.000000",
      "from": "ZION_sender...",
      "to": "ZION_abc123...",
      "fee": "0.001000",
      "confirmations": 12,
      "timestamp": "2025-12-28T11:55:00Z"
    }
  ],
  "total": 1234,
  "limit": 50,
  "offset": 0
}
```

---

### Transactions

#### Send Transaction
```http
POST /transaction/send
```

**Request:**
```json
{
  "from": "ZION_sender...",
  "to": "ZION_recipient...",
  "amount": "100.000000",
  "fee": "0.001000",
  "memo": "Optional message",
  "signature": "hex-encoded-signature"
}
```

**Response:**
```json
{
  "success": true,
  "hash": "0x1a2b3c4d...",
  "status": "pending",
  "estimated_confirmation": "60s"
}
```

#### Get Transaction Details
```http
GET /transaction/{hash}
```

**Response:**
```json
{
  "hash": "0x1a2b3c4d...",
  "status": "confirmed",
  "block_height": 123456,
  "from": "ZION_sender...",
  "to": "ZION_recipient...",
  "amount": "100.000000",
  "fee": "0.001000",
  "confirmations": 12,
  "timestamp": "2025-12-28T12:00:00Z"
}
```

---

### Mining

#### Get Pool Stats
```http
GET /pool/stats
```

**Response:**
```json
{
  "pool_hashrate": "1500000",
  "active_miners": 234,
  "blocks_found_24h": 18,
  "last_block": 123456,
  "fee_percent": 1.0,
  "min_payout": "10.000000",
  "algorithm": "cosmic_harmony"
}
```

#### Get Miner Stats
```http
GET /pool/miner/{address}
```

**Response:**
```json
{
  "address": "ZION_miner...",
  "hashrate": "5000",
  "shares_24h": 12345,
  "blocks_found": 3,
  "pending_balance": "456.789000",
  "total_paid": "12345.678900",
  "consciousness_level": 4,
  "consciousness_xp": 35000,
  "workers": [
    {
      "name": "rig1",
      "hashrate": "3000",
      "last_share": "2025-12-28T11:59:00Z"
    },
    {
      "name": "rig2",
      "hashrate": "2000",
      "last_share": "2025-12-28T11:58:30Z"
    }
  ]
}
```

---

### Consciousness

#### Get Consciousness Info
```http
GET /consciousness/{address}
```

**Response:**
```json
{
  "address": "ZION_abc123...",
  "level": 5,
  "level_name": "QUANTUM",
  "xp": 75000,
  "xp_to_next_level": 75000,
  "multiplier": 4.0,
  "rank": 1234,
  "challenges_completed": 42,
  "achievements": [
    "first_block",
    "1000_shares",
    "level_5"
  ]
}
```

#### Get Leaderboard
```http
GET /consciousness/leaderboard?limit=100
```

**Response:**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "address": "ZION_top...",
      "level": 9,
      "xp": 5500000,
      "blocks_found": 500
    }
  ],
  "total_miners": 5000,
  "updated_at": "2025-12-28T12:00:00Z"
}
```

---

## 🔌 WebSocket API

### Connection

```javascript
const ws = new WebSocket('wss://api.zionterranova.com/v1/ws');

ws.onopen = () => {
  console.log('Connected to ZION WebSocket');
  
  // Subscribe to events
  ws.send(JSON.stringify({
    action: 'subscribe',
    channels: ['blocks', 'transactions', 'pool']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
};
```

### Event Types

#### New Block
```json
{
  "type": "block",
  "data": {
    "height": 123457,
    "hash": "0x...",
    "miner": "ZION_abc...",
    "reward": "1619.63",
    "timestamp": "2025-12-28T12:01:00Z"
  }
}
```

#### New Transaction
```json
{
  "type": "transaction",
  "data": {
    "hash": "0x...",
    "from": "ZION_sender...",
    "to": "ZION_recipient...",
    "amount": "100.000000"
  }
}
```

#### Pool Share
```json
{
  "type": "share",
  "data": {
    "miner": "ZION_abc...",
    "difficulty": 50000,
    "valid": true
  }
}
```

---

## 📦 SDK Integration

### JavaScript/TypeScript

```bash
npm install @zion-terranova/sdk
```

```typescript
import { ZionSDK } from '@zion-terranova/sdk';

const zion = new ZionSDK({
  network: 'testnet',
  apiKey: 'your-api-key'
});

// Get balance
const balance = await zion.getBalance('ZION_your_address');
console.log('Balance:', balance);

// Send transaction
const tx = await zion.sendTransaction({
  to: 'ZION_recipient',
  amount: '100.0',
  memo: 'Test payment'
});
console.log('TX Hash:', tx.hash);

// Subscribe to blocks
zion.on('block', (block) => {
  console.log('New block:', block.height);
});
```

### Python

```bash
pip install zion-sdk
```

```python
from zion_sdk import ZionClient

client = ZionClient(
    network='testnet',
    api_key='your-api-key'
)

# Get balance
balance = client.get_balance('ZION_your_address')
print(f'Balance: {balance}')

# Get network stats
stats = client.get_network_stats()
print(f'Block height: {stats.block_height}')
print(f'Hashrate: {stats.hashrate}')
```

---

## ⚠️ Error Codes

| Code | Message | Popis |
|------|---------|-------|
| 400 | Bad Request | Neplatný request |
| 401 | Unauthorized | Chybí/neplatný API klíč |
| 404 | Not Found | Resource neexistuje |
| 429 | Rate Limited | Překročen rate limit |
| 500 | Internal Error | Server error |

**Error Response Format:**
```json
{
  "error": true,
  "code": 400,
  "message": "Invalid address format",
  "details": "Address must start with 'ZION_'"
}
```

---

## 📚 Další dokumenty

- [Whitepaper Lite](./whitepaper-lite.md) — Přehled projektu
- [Economic Model](./economic-model.md) — Tokenomics
- [Getting Started](./getting-started.md) — Quick start guide

---

*ZION TerraNova API v2.9* 🌟
