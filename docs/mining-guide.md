# Mining Guide — ZION v2.9

Kompletní průvodce těžbou ZION TerraNova.

## Algoritmy

| Algoritmus | Typ | Výkon (referenční) |
| --- | --- | --- |
| Cosmic Harmony | CPU/GPU | ~600 kH/s CPU, ~1.6 MH/s GPU |
| RandomX | CPU | ~640 H/s |
| Yescrypt | CPU | ~176 H/s |
| Autolykos v2 | GPU | závisí na GPU |

## Solo vs Pool

- **Solo**: doporučeno při výkonu > 50 kH/s.
- **Pool**: doporučený endpoint `pool.zionterranova.com:3333`.

```bash
# Pomocí ZION Native Miner v2.9
python -m zion_miner pool.zionterranova.com 3333 ZION_WALLET_ADDRESS worker1 cosmic_harmony

# Nebo pomocí Desktop Mining Agent
# Stáhni z releases a spusť GUI aplikaci
```

## Optimalizace

1. Povolit hugepages: `vm.nr_hugepages=128`.
2. NUMA pinning dle socketu.
3. TDP limit okolo 80 % pro stabilitu.

## Monitoring výkonu

- Grafana dashboard `deployment/monitoring`.
- Alert: propad hashrate o 30 % během 10 minut.
