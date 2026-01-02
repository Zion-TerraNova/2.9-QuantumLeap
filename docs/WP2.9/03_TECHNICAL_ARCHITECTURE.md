# Chapter 3: Technical Architecture

> **"Built to Last: Enterprise-Grade Blockchain for the Next Decade"**

---

## 🏗️ Architecture Overview

ZION TerraNova v2.9 represents a mature, production-ready blockchain stack built with modern DevOps practices. The architecture follows a modular design allowing independent scaling and maintenance of each component.

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ZION TerraNova v2.9 Stack                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                              INTERNET                                   │
│                                  │                                      │
│              ┌───────────────────┴───────────────────┐                 │
│              │                                       │                 │
│         Port 80/443                           Port 3333                │
│              │                                       │                 │
│              ▼                                       ▼                 │
│    ┌─────────────────┐                    ┌──────────────────┐        │
│    │     NGINX       │                    │   STRATUM POOL   │        │
│    │  Reverse Proxy  │                    │   (Mining Pool)  │        │
│    │   + SSL/TLS     │                    │                  │        │
│    └────────┬────────┘                    └────────┬─────────┘        │
│             │                                      │                   │
│    ┌────────┴────────────────────────────────────┬┘                   │
│    │                                              │                    │
│    ▼                                              ▼                    │
│ ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐        │
│ │   Website    │  │   FastAPI    │  │   Blockchain Core     │        │
│ │  (Next.js)   │  │  (API GW)    │  │  (Python + SQLite)    │        │
│ │   Port 3001  │  │  Port 8001   │  │   Ports 18080/18081   │        │
│ └──────────────┘  └──────────────┘  └───────────────────────┘        │
│                           │                       │                    │
│                           │          ┌────────────┴────────────┐       │
│                           │          │                         │       │
│                           ▼          ▼                         ▼       │
│                    ┌──────────┐  ┌────────┐  ┌──────────────────┐     │
│                    │  Redis   │  │ SQLite │  │   Prometheus +   │     │
│                    │ (Cache)  │  │  (DB)  │  │   Grafana        │     │
│                    │Port 6379 │  │        │  │  Ports 9090/3000 │     │
│                    └──────────┘  └────────┘  └──────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Core Components

### 1. Blockchain Core (`src/core/`)

The heart of ZION — a custom Proof-of-Work blockchain implementing:

| Component | File | Purpose |
|-----------|------|---------|
| **Main Engine** | `new_zion_blockchain.py` | Block creation, validation, chain management |
| **P2P Network** | `zion_p2p_network.py` | Peer discovery, block propagation |
| **RPC Server** | `zion_rpc_server.py` | JSON-RPC API (Monero-compatible) |
| **Crypto Utils** | `crypto_utils.py` | Ed25519 signatures, Bech32 addresses |
| **Premine Logic** | `premine.py` | Genesis block distribution |
| **Consciousness** | `consciousness_mining_game.py` | XP system, level progression |

**Key Specifications:**

```yaml
Blockchain Parameters:
  Total Supply: 144,000,000,000 ZION
  Block Time: 60 seconds
  Block Reward: 50 ZION (TestNet) / 5,400.067 ZION (MainNet)
  Difficulty Adjustment: Per-block (VarDiff algorithm)
  Max Block Size: 1 MB
  Database: SQLite with WAL mode
  Network: P2P gossip protocol
```

### 2. Mining Pool (`src/pool/`)

A modular mining pool implementation with enterprise-grade features:

```
src/pool/
├── auth/               # Miner authentication
│   ├── login_handler.py       # Stratum login processing
│   ├── address_validator.py   # ZION address validation
│   └── session_manager.py     # Miner session tracking
│
├── mining/             # Core mining logic
│   ├── algorithm_detector.py  # Multi-algo support
│   ├── job_manager.py         # Job creation & distribution
│   ├── share_validator.py     # Share verification
│   └── difficulty_manager.py  # VarDiff algorithm
│
├── blockchain/         # Chain integration
│   ├── zion_rpc_client.py     # RPC communication
│   ├── block_template_mgr.py  # Template fetching
│   ├── reward_calculator.py   # Payout math
│   └── consciousness_game.py  # XP integration
│
├── network/            # Server infrastructure
│   ├── stratum_server.py      # Stratum protocol
│   ├── protocol_handler.py    # Message handling
│   └── metrics_server.py      # Pool statistics
│
├── payout/             # Payment system
│   └── payout_manager.py      # PPLNS distribution
│
└── database/           # Persistence
    └── pool_database.py       # SQLite stats & history
```

**Supported Algorithms:**

| Port | Algorithm | Hardware | Use Case |
|------|-----------|----------|----------|
| 3333 | Cosmic Harmony | CPU | Recommended, native |
| 3335 | RandomX | CPU | Monero-compatible |
| 3336 | Yescrypt | CPU/ARM | Memory-hard, SBC friendly |
| 3337 | Autolykos v2 | GPU | 6GB+ VRAM required |

### 3. API Gateway (`src/api/`)

FastAPI-based REST and WebSocket API providing:

- **Public Endpoints**: Pool stats, blockchain info, miner stats
- **Protected Endpoints**: Wallet operations, agent control
- **WebSocket**: Real-time updates, mining events

```python
# Example API endpoints
GET  /health              # Service health check
GET  /api/stats           # Pool statistics
GET  /api/blocks          # Recent blocks
GET  /api/miner/{address} # Individual miner stats
POST /api/agents/pair     # Agent pairing
WS   /ws/events           # Real-time event stream
```

### 4. Website (`website-v2.9/`)

Next.js static export for the public-facing interface:

- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Output**: Static export (`out/` directory)
- **Deployment**: NGINX static hosting

**Key Pages:**
- `/` — Landing page
- `/mining` — Mining guide & downloads
- `/roadmap` — Project timeline
- `/dashboard` — Live statistics
- `/presale` — Token purchase (coming Q1 2026)

---

## ⛏️ Mining Algorithm: RandomX + Cosmic Harmony

### RandomX (Primary)

ZION uses **RandomX** — the same ASIC-resistant algorithm as Monero:

| Feature | Value |
|---------|-------|
| **Type** | CPU-optimized PoW |
| **Memory** | 2 GB scratchpad |
| **ASIC Resistance** | High (random code execution) |
| **GPU Efficiency** | ~50% of CPU |
| **Verification** | Fast (~0.1 ms) |

**Why RandomX?**

1. **Fair Mining**: Anyone with a CPU can participate
2. **Proven Security**: Audited, used by Monero since 2019
3. **Energy Efficient**: Lower power than SHA-256
4. **Decentralization**: No ASIC manufacturer advantage

### Cosmic Harmony (Native)

ZION's custom algorithm building on RandomX with consciousness elements:

```python
def cosmic_harmony_hash(block_header, nonce):
    """
    Cosmic Harmony = RandomX + Sacred Geometry Layer
    
    1. Standard RandomX hash
    2. Apply golden ratio transformation (φ = 1.618)
    3. Sacred frequency modulation (44.44 Hz pattern)
    4. Final hash output
    """
    base_hash = randomx_hash(block_header, nonce)
    transformed = apply_golden_ratio(base_hash)
    modulated = sacred_frequency_mod(transformed, 44.44)
    return modulated
```

---

## 🔐 Privacy: CryptoNote Protocol

ZION implements the **CryptoNote** privacy protocol (same as Monero):

### Ring Signatures

Every transaction is signed with a "ring" of possible signers, making it impossible to identify the true sender:

```
Transaction Signature Ring:
┌─────────────────────────────────────────────────┐
│  Possible Signers (decoys + real)               │
├─────────────────────────────────────────────────┤
│  ● Alice's key (decoy)                          │
│  ● Bob's key (REAL SIGNER)                      │
│  ● Carol's key (decoy)                          │
│  ● Dave's key (decoy)                           │
│  ● Eve's key (decoy)                            │
└─────────────────────────────────────────────────┘
Verifier can confirm ONE signed, but not WHICH one.
```

### Stealth Addresses

Each transaction generates a one-time address:

```
Sender: Alice → Bob
Bob's public address: zion1qyfe883hey23jwfj498djawe98rfu0w0j23p7f

Transaction:
1. Alice derives one-time stealth address
2. Funds sent to: zion1[random_unique_address]
3. Only Bob can derive private key
4. No link between transactions
```

### RingCT (Confidential Transactions)

Transaction amounts are cryptographically hidden:

```
Before RingCT:
"Alice sends 100 ZION to Bob" → Visible on chain

With RingCT:
"Alice sends [encrypted] ZION to Bob"
├─ Validators can verify: Input ≥ Output + Fee
├─ Cannot see actual amounts
└─ Pedersen commitments ensure math is correct
```

---

## 🌐 Network Architecture

### P2P Protocol

ZION uses a gossip-based P2P network:

```yaml
P2P Specifications:
  Protocol: Custom ZION P2P (Monero-inspired)
  Port: 18080 (P2P), 18081 (RPC)
  Discovery: Seed nodes + peer exchange
  Block Propagation: Flooding with deduplication
  Connection Limit: 100 peers default
  Sync Strategy: Chain download + incremental updates
```

### Seed Nodes (TestNet)

```
Primary Seeds:
  - 91.98.122.165:18080 (Europe - Prague)
  - (Additional nodes coming Q1 2026)

Backup Seeds:
  - Hardcoded in source
  - DNS-based discovery (future)
```

---

## 🐳 Docker Infrastructure

### Production Stack (`docker-compose-v2.9-production.yml`)

```yaml
services:
  blockchain:
    image: zion/blockchain:2.9.0
    ports:
      - "8545:8545"   # ETH-style RPC
      - "18081:18081" # Monero-style RPC
    volumes:
      - blockchain_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:18081/json_rpc"]
      interval: 30s
      
  pool:
    image: zion/pool:2.9.0
    ports:
      - "3333:3333"   # Stratum
      - "8080:8080"   # Stats API
    depends_on:
      - blockchain
      - redis
      
  api:
    image: zion/api:2.9.0
    ports:
      - "127.0.0.1:8001:8001"  # Internal only
    depends_on:
      - blockchain
      
  redis:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
      
  prometheus:
    image: prom/prometheus
    ports:
      - "127.0.0.1:9090:9090"
      
  grafana:
    image: grafana/grafana
    ports:
      - "127.0.0.1:3000:3000"
```

### Resource Requirements

| Service | CPU | RAM | Disk |
|---------|-----|-----|------|
| Blockchain | 1 core | 512 MB | 10 GB |
| Pool | 2 cores | 256 MB | 1 GB |
| API | 0.5 core | 128 MB | 100 MB |
| Redis | 0.5 core | 128 MB | 500 MB |
| Prometheus | 0.5 core | 256 MB | 5 GB |
| Grafana | 0.5 core | 256 MB | 1 GB |
| **TOTAL** | 5 cores | 1.5 GB | ~18 GB |

---

## 🔒 Security Architecture

### Current Security Measures

| Layer | Protection |
|-------|------------|
| **Network** | TLS 1.3 encryption, rate limiting |
| **Authentication** | Ed25519 signatures, BIP39 mnemonics |
| **Database** | SQLite WAL mode, file permissions |
| **API** | CORS policies, input validation |
| **Docker** | Resource limits, network isolation |

### Planned Security Upgrades (v2.9.2+)

- **Migration**: `ecdsa` → `cryptography` library (timing attack fix)
- **Hardware Wallets**: Ledger/Trezor support
- **Multi-Sig**: N-of-M wallet signing
- **Audit**: External security review (Q2 2026)

---

## 📊 Performance Metrics

### Current TestNet Performance

| Metric | Value |
|--------|-------|
| Block Time | 60 seconds (target) |
| TPS Capacity | ~100 tx/block |
| API Latency (p95) | <100 ms |
| Pool Share Rate | 5%+ acceptance |
| Database Query | <50 ms (indexed) |
| Memory Usage | 4.6 GB total stack |

### Scalability Roadmap

| Phase | Target |
|-------|--------|
| TestNet (Now) | 100 miners, 10 TPS |
| MainNet Launch | 1,000 miners, 50 TPS |
| Year 1 | 10,000 miners, 100 TPS |
| Year 3 | 100,000 miners, 500 TPS |

---

## 🛠️ Developer Resources

### Quick Start (Local Development)

```bash
# Clone repository
git clone https://github.com/Yose144/Zion-2.9.git
cd Zion-2.9

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start blockchain node
python src/core/new_zion_blockchain.py --network testnet

# Start mining pool (separate terminal)
python src/pool/zion_pool_v2_9.py

# Start miner (separate terminal)
python zion_native_miner_v2_9.py \
  --pool localhost:3333 \
  --wallet YOUR_ZION_ADDRESS
```

### API Documentation

Full API reference available at:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI JSON**: `http://localhost:8001/openapi.json`

---

**Peace and One Love** ☮️❤️

---

[← Back to Chapter 2](02_LIBERATION_MANIFESTO.md) | [→ Chapter 4: WARP Multi-Chain Bridge](04_WARP_MULTICHAIN_BRIDGE.md)
