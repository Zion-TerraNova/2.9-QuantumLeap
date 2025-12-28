# Getting Started with ZION TerraNova v2.9

Průvodce prvními kroky s ZION — od peněženky po těžbu.

---

## 🎯 Co potřebuješ

| Požadavek | Minimum | Doporučeno |
|-----------|---------|------------|
| **OS** | Windows 10 / macOS 10.15 / Ubuntu 20.04 | Nejnovější verze |
| **CPU** | 4 jádra | 8+ jader (AMD Ryzen) |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 10 GB SSD | 50 GB SSD |
| **Internet** | Stabilní připojení | 10+ Mbps |
| **Python** | 3.10+ | 3.11+ |

---

## 1️⃣ Vytvoř si peněženku

### Generování adresy

```bash
# Stáhni wallet generator
git clone https://github.com/Zion-TerraNova/2.9-QuantumLeap.git
cd 2.9-QuantumLeap

# Vygeneruj novou adresu
python -c "
import secrets
import hashlib

# Vygeneruj privátní klíč
private_key = secrets.token_hex(32)

# Odvoz veřejnou adresu (zjednodušeno)
public_hash = hashlib.sha256(bytes.fromhex(private_key)).hexdigest()[:40]
address = f'ZION_{public_hash}'

print(f'🔐 Private Key: {private_key}')
print(f'📬 Address: {address}')
print()
print('⚠️  ULOŽ PRIVÁTNÍ KLÍČ NA BEZPEČNÉ MÍSTO!')
"
```

### Formát adresy

```
ZION_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
└──┬─┘└─────────────────────┬─────────────────────┘
 Prefix              40-char hex hash
```

---

## 2️⃣ Připoj se k síti

### Network Ports

| Služba | Port | Popis |
|--------|------|-------|
| P2P | 18080 | Node synchronizace |
| RPC | 18081 | API komunikace |
| Stratum | 3333 | Mining pool |

### TestNet vs MainNet

| Síť | Status | Použití |
|-----|--------|---------|
| **TestNet** | ✅ Aktivní | Testování, vývoj |
| **MainNet** | ⏳ Prosinec 2026 | Produkce |

```bash
# TestNet endpoint
POOL_URL="stratum+tcp://pool.zionterranova.com:3333"
```

---

## 3️⃣ Spusť mining

### Instalace mineru

```bash
# Naklonuj repo
git clone https://github.com/Zion-TerraNova/2.9-QuantumLeap.git
cd 2.9-QuantumLeap/miner

# Instaluj závislosti
pip install -e .

# Ověř instalaci
python -m zion_miner --version
```

### Spuštění

```bash
# Základní mining (CPU)
python -m zion_miner \
  --pool stratum+tcp://pool.zionterranova.com:3333 \
  --wallet ZION_tvoje_adresa \
  --worker muj-pocitac \
  --threads 4

# S GPU podporou
python -m zion_miner \
  --pool stratum+tcp://pool.zionterranova.com:3333 \
  --wallet ZION_tvoje_adresa \
  --worker muj-pocitac \
  --gpu

# Vyber algoritmus
python -m zion_miner \
  --pool stratum+tcp://pool.zionterranova.com:3333 \
  --wallet ZION_tvoje_adresa \
  --algorithm randomx
```

### Dostupné algoritmy

| Algoritmus | Flag | Typ | Popis |
|------------|------|-----|-------|
| Cosmic Harmony | `--algorithm cosmic_harmony` | CPU/GPU | Primární (default) |
| RandomX | `--algorithm randomx` | CPU | Monero-kompatibilní |
| Yescrypt | `--algorithm yescrypt` | CPU | Low power |
| Autolykos v2 | `--algorithm autolykos` | GPU | Ergo-kompatibilní |

---

## 4️⃣ Sleduj své statistiky

### Pool Dashboard

Navštiv `https://pool.zionterranova.com` a zadej svou adresu.

### API dotazy

```bash
# Zkontroluj balance
curl "https://api.zionterranova.com/v1/account/balance/ZION_tvoje_adresa"

# Mining statistiky
curl "https://api.zionterranova.com/v1/pool/miner/ZION_tvoje_adresa"

# Network stats
curl "https://api.zionterranova.com/v1/network/stats"
```

### Očekávaný výkon

| Hardware | Hashrate | ~Daily ZION |
|----------|----------|-------------|
| Intel i5 (4 jádra) | ~1,000 H/s | ~15 ZION |
| Intel i7 (8 jader) | ~2,000 H/s | ~30 ZION |
| AMD Ryzen 5 | ~4,000 H/s | ~60 ZION |
| AMD Ryzen 9 | ~8,000 H/s | ~120 ZION |
| GPU (RTX 3070) | ~15,000 H/s | ~225 ZION |

*Odhady při network hashrate 1 MH/s*

---

## 5️⃣ Consciousness Mining

### XP systém

Každá aktivita ti dává XP body:

| Aktivita | XP |
|----------|-----|
| Share submission | +10 XP |
| Block found | +1,000 XP |
| AI Challenge | +100-1,000 XP |
| Community help | Variable |

### Úrovně vědomí

| Level | Název | XP | Bonus |
|-------|-------|-----|-------|
| 1 | PHYSICAL | 0 | 1.0x |
| 2 | EMOTIONAL | 1,000 | 1.5x |
| 3 | MENTAL | 5,000 | 2.0x |
| 4 | SACRED | 15,000 | 3.0x |
| 5 | QUANTUM | 50,000 | 4.0x |
| 6 | COSMIC | 150,000 | 5.0x |
| 7 | ENLIGHTENED | 500,000 | 7.5x |
| 8 | TRANSCENDENT | 1,500,000 | 10.0x |
| 9 | ON THE STAR | 5,000,000 | 15.0x |

Vyšší úroveň = vyšší bonus k block reward!

---

## 6️⃣ SDK Integrace

### JavaScript

```bash
npm install @zion-terranova/sdk
```

```javascript
import { ZionSDK } from '@zion-terranova/sdk';

const zion = new ZionSDK({
  network: 'testnet',
  apiKey: 'tvuj-api-klic'
});

// Zkontroluj balance
const balance = await zion.getBalance('ZION_tvoje_adresa');
console.log('Balance:', balance);

// Pošli transakci
const tx = await zion.sendTransaction({
  to: 'ZION_prijemce',
  amount: '100.0',
  memo: 'Test payment'
});
console.log('TX:', tx.hash);
```

### Python

```bash
pip install zion-sdk
```

```python
from zion_sdk import ZionClient

client = ZionClient(
    network='testnet',
    api_key='tvuj-api-klic'
)

# Zkontroluj balance
balance = client.get_balance('ZION_tvoje_adresa')
print(f'Balance: {balance}')
```

---

## 7️⃣ Troubleshooting

### Časté problémy

**"Connection refused" při připojení k poolu:**
```bash
# Zkontroluj firewall
sudo ufw allow 3333/tcp

# Ověř dostupnost
telnet pool.zionterranova.com 3333
```

**"Invalid share" zprávy:**
```bash
# Zkontroluj algoritmus
python -m zion_miner --algorithm cosmic_harmony ...

# Snižš difficulty (pokud pool podporuje)
python -m zion_miner --difficulty 10000 ...
```

**Nízký hashrate:**
```bash
# Zkontroluj počet vláken
python -m zion_miner --threads $(nproc) ...

# Pro RandomX potřebuješ 2+ GB RAM
free -h
```

---

## 📚 Další kroky

1. **[Whitepaper Lite](./whitepaper-lite.md)** — Pochop projekt
2. **[Economic Model](./economic-model.md)** — Tokenomics
3. **[Consciousness Levels](./consciousness-levels.md)** — XP systém
4. **[API Reference](./api-reference.md)** — Pro vývojáře
5. **[FAQ](./faq.md)** — Časté otázky

---

## 🌐 Komunita

- **Website**: [zionterranova.com](https://zionterranova.com)
- **GitHub**: [github.com/Zion-TerraNova](https://github.com/Zion-TerraNova)
- **Discord**: [discord.gg/zion](https://discord.gg/zion)
- **Telegram**: [t.me/zionterranova](https://t.me/zionterranova)

---

*Jsi připraven těžit vědomí! 🚀*

**ZION TerraNova v2.9 — Where Technology Meets Spirit** 🌟
