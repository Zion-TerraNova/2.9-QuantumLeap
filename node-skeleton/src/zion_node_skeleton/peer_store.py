from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Peer:
    host: str
    port: int
    last_seen: float = field(default_factory=time.time)

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


class PeerStore:
    def __init__(self, max_peers: int = 50):
        self.max_peers = max_peers
        self._peers: Dict[str, Peer] = {}

    def upsert(self, host: str, port: int) -> None:
        if len(self._peers) >= self.max_peers and f"{host}:{port}" not in self._peers:
            return
        self._peers[f"{host}:{port}"] = Peer(host=host, port=port)

    def list(self) -> List[Peer]:
        return list(self._peers.values())

    def as_dicts(self) -> List[dict]:
        return [{"host": p.host, "port": p.port} for p in self._peers.values()]

    def merge(self, peers: List[dict]) -> None:
        for p in peers:
            host = p.get("host")
            port = p.get("port")
            if host and port:
                self.upsert(str(host), int(port))
