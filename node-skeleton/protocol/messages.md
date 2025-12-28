# ZION P2P Skeleton — Message Protocol (Public)

All messages are newline-delimited JSON objects.

## Envelope
```json
{
  "type": "handshake",
  "data": {},
  "timestamp": 1735410000,
  "sender": "node-123"
}
```

## Message types
- `handshake`: exchange basic node info
- `ping` / `pong`: keepalive
- `get_peers`: request known peers
- `peers`: response with list of peers

## Versioning
- `data.version` is a semantic string (e.g. `2.9.0`).
- Backwards compatibility is expected for the skeleton types.
