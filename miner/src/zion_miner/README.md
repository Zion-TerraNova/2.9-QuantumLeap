# 🚀 ZION Miner v2.9

Modulární native miner pro ZION blockchain s podporou všech mining algoritmů.

## 📋 Vlastnosti

- **Modulární architektura**: Oddělené moduly pro algoritmy, síť a metriky
- **Multi-protokol**: XMRig i Stratum podpora
- **Lazy loading**: Algoritmy se načítají jen když jsou potřeba (rychlý start)
- **Real-time metriky**: Hashrate, accepted/rejected shares, efektivita
- **Native knihovny**: Optimalizované pro Cosmic Harmony, RandomX, Yescrypt
- **Async I/O**: Neblokující komunikace s poolem
- **Graceful shutdown**: Čisté ukončení při CTRL+C

## 🏗️ Architektura

```
zion_miner/
├── __init__.py              # Package exports
├── algorithms/              # Mining algoritmy
│   └── __init__.py         # AlgorithmEngine s lazy loading
├── network/                # Pool komunikace
│   └── __init__.py         # PoolClient (XMRig + Stratum)
├── metrics/                # Statistiky a monitoring
│   └── __init__.py         # MetricsCollector
└── zion_miner_v2_9.py      # Hlavní orchestrátor
```

### Komponenty

#### AlgorithmEngine (`algorithms/`)
- Lazy loading native knihoven (žádné 25s čekání při startu)
- Detekce dostupných algoritmů
- Jednotné rozhraní pro všechny algo (cosmic_harmony, randomx, yescrypt)
- Fallback handling pokud knihovna chybí

#### PoolClient (`network/`)
- Async TCP komunikace
- Podpora XMRig protokolu (JSON-RPC over TCP)
- Podpora Stratum protokolu (text-based)
- Auto-reconnect připraveno
- Keepalive mechanismus
- Job queue a message routing

#### MetricsCollector (`metrics/`)
- Rolling averages (1min, 5min, 15min hashrate)
- Share statistiky (accepted, rejected, stale)
- Efektivita výpočtu
- Prometheus export ready
- Hardware metriky ready (CPU/GPU temp, power)

#### ZionMiner (`zion_miner_v2_9.py`)
- Hlavní orchestrátor všech komponent
- Multi-threaded mining workers
- Signal handling (SIGINT, SIGTERM)
- Graceful shutdown všech tasků
- CLI entry point

## 🚀 Rychlý start

### 1. Jednoduché spuštění

```bash
python -m zion_miner example.com 3333 ZION_WALLET_ADDRESS worker1 randomx
```

### 2. Vlastní konfigurace

```python
from zion_miner import ZionMiner, MinerConfig

config = MinerConfig(
  pool_host="example.com",
    pool_port=3333,
  wallet_address="ZION_WALLET_ADDRESS",
    worker_name="my-worker",
    algorithm="cosmic_harmony",
    threads=4,
    protocol="xmrig",
    intensity=1,
    stats_enabled=True,
    stats_interval=10.0
)

miner = ZionMiner(config)
await miner.start()
```

### 3. CLI použití

```bash
# Základní
python -m zion_miner example.com 3333 ZION_WALLET_ADDRESS worker1 cosmic_harmony

# S parametry
python -m zion_miner \
  --host example.com \
  --port 3333 \
  --wallet ZION_WALLET_ADDRESS \
  --worker test-miner \
  --algorithm cosmic_harmony \
  --threads 4 \
  --protocol xmrig \
  --intensity 1
```

## 📊 Metriky

Miner zobrazuje real-time statistiky:

```
⛏️  MINING STATS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hashrate:     548.3 kH/s (1m: 547.1 | 5m: 546.8 | 15m: 545.2)
Shares:       Accepted: 42 (98.5%) | Rejected: 1 | Stale: 0
Efficiency:   98.5%
Uptime:       02:15:33
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Prometheus Export

Miner exportuje metriky pro Prometheus:

```python
# GET /metrics
zion_miner_hashrate_current 548300
zion_miner_hashrate_1m 547100
zion_miner_hashrate_5m 546800
zion_miner_hashrate_15m 545200
zion_miner_shares_accepted 42
zion_miner_shares_rejected 1
zion_miner_shares_stale 0
zion_miner_efficiency 98.5
```

## 🔧 Konfigurace

### MinerConfig parametry

| Parametr | Typ | Default | Popis |
|----------|-----|---------|-------|
| `pool_host` | str | - | IP/hostname poolu |
| `pool_port` | int | - | Port poolu (3333) |
| `wallet_address` | str | - | ZION peněženka |
| `worker_name` | str | "worker1" | Název workeru |
| `algorithm` | str | "cosmic_harmony" | Mining algoritmus |
| `threads` | int | CPU count | Počet vláken |
| `protocol` | str | "xmrig" | Protokol (xmrig/stratum) |
| `intensity` | int | 1 | Mining intensita |
| `stats_enabled` | bool | True | Zobrazit statistiky |
| `stats_interval` | float | 10.0 | Interval statistik (s) |

### Podporované algoritmy

- **cosmic_harmony**: ZION native (548 kH/s na Hetzner CPX51)
- **randomx**: Monero-compatible
- **yescrypt**: ~4.8 kH/s

## 🏊 Pool kompatibilita

### XMRig protokol (doporučeno)
- JSON-RPC over TCP
- Login flow: `{"id":1,"method":"login","params":{"login":"WALLET","pass":"WORKER"}}`
- Job notification: `{"jsonrpc":"2.0","method":"job","params":{...}}`
- Share submit: `{"id":2,"method":"submit","params":{...}}`

### Stratum protokol
- Text-based line protocol
- Subscribe: `{"id":1,"method":"mining.subscribe","params":[]}`
- Authorize: `{"id":2,"method":"mining.authorize","params":["WALLET.WORKER","x"]}`
- Submit: `{"id":3,"method":"mining.submit","params":[...]}`

## 🧪 Testování

### Unit testy
```bash
pytest -v
```

### Integration test
```bash
# Krátký test proti libovolnému poolu
python -m zion_miner \
  example.com 3333 \
  ZION_WALLET_ADDRESS \
  test-integration \
  randomx
```

### Benchmark
```bash
# Otestovat výkon algoritmu
python -c "
from zion_miner import AlgorithmEngine
engine = AlgorithmEngine()
engine.initialize('cosmic_harmony')
result = engine.benchmark()
print(f'Hashrate: {result} H/s')
"
```

## 📁 Poznámka k veřejné verzi

Tento public export záměrně neobsahuje blockchain core ani historické interní minery.

## 🔍 Debugging

### Verbose logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Pool connection test
```bash
# Ověř, že pool běží
nc -zv example.com 3333
```

### Algorithm test
```python
from zion_miner import AlgorithmEngine

engine = AlgorithmEngine()
print(f"Available: {engine.get_available_algorithms()}")

engine.initialize("cosmic_harmony")
hash_result = engine.compute_hash(b"test data", "000000...")
print(f"Hash: {hash_result}")
```

## 🛠️ Vývoj

### Přidat nový algoritmus

1. Přidej native knihovnu do `build_zion/`
2. Aktualizuj `ALGORITHM_MAP` v `algorithms/__init__.py`:
```python
ALGORITHM_MAP = {
    "cosmic_harmony": "libcosmic_harmony_zion.so",
    "my_algo": "libmy_algo.so",  # Nový
}
```

### Přidat hardware metriky

```python
# V metrics/__init__.py
def get_hardware_metrics(self) -> dict:
    """GPU temp, power atd."""
    return {
        "cpu_temp": self._get_cpu_temp(),
        "gpu_temp": self._get_gpu_temp(),
        "power": self._get_power_usage(),
    }
```

## 📊 Výkon

### Benchmark (Hetzner CPX51)

| Algoritmus | Hashrate | Threads | Poznámka |
|------------|----------|---------|----------|
| cosmic_harmony | 548.3 kH/s | 16 | Native optimized |
| randomx | ~2.1 kH/s | 16 | Monero-compatible |
| yescrypt | ~4.8 kH/s | 16 | CPU-bound |

### Optimalizace

- **Cosmic Harmony**: Využívá všechna CPU jádra efektivně
- **Lazy loading**: Start < 1s (vs 25s při eager loading všech algo)
- **Async I/O**: Žádné blokování na síťové komunikaci
- **Multi-threading**: Jeden worker per core pro max throughput

## 🐛 Známé problémy

1. **Connection timeout**: Pool může resetovat idle spojení - připraveno auto-reconnect
2. **Native library path**: Ujisti se že `LD_LIBRARY_PATH` obsahuje `build_zion/`
3. **Memory leak**: Dlouhodobé běhy sleduj RAM usage (zatím bez leaků)

## 📝 Changelog

### v2.9.0 (2024-01)
- ✅ Modulární architektura (algorithms, network, metrics)
- ✅ Lazy loading algoritmů
- ✅ XMRig + Stratum dual protokol
- ✅ Real-time metriky s rolling averages
- ✅ Prometheus export ready
- ✅ Graceful shutdown
- ✅ CLI interface
- 🔄 Hardware metriky (připraveno)
- 🔄 Auto-reconnect (připraveno)
- 🔄 Config soubor support (připraveno)

## 🤝 Contributing

1. Používej type hints (mypy compatible)
2. Async/await pro I/O operace
3. Graceful error handling
4. Unit testy pro nové features
5. Dokumentuj public API

## 📄 License

ZION Blockchain Project

## 🔗 Odkazy

- **Pool v2.9**: `src/pool/` - Modulární mining pool
- **Blockchain Core**: `src/core/new_zion_blockchain.py`
- **RPC Server**: `src/core/zion_rpc_server.py` (dual-port 8545+18081)
- **Native Libraries**: `build_zion/`

---

**Vytvořeno**: 2024-01  
**Status**: ✅ Production Ready  
**Architektura**: Modular v2.9  
**Konsoliduje**: ~68 legacy miner souborů
