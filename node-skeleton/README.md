# ZION Node Skeleton (Public)

Minimal peer/node **skeleton** for experimentation with P2P messaging.

## What this is
- TCP-based peer connections
- JSON message envelope: `{type, data, timestamp, sender}`
- Message types: `handshake`, `ping`, `pong`, `get_peers`, `peers`

## What this is NOT
- No consensus, no block validation, no mempool, no mining rules.

## Run
```bash
python -m zion_node_skeleton --host 0.0.0.0 --port 8333 --seed example.com:8333
```
