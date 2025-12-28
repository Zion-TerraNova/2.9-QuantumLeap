from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class NetworkMessage:
    type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    sender: str = ""

    def to_json(self) -> str:
        return json.dumps(
            {"type": self.type, "data": self.data, "timestamp": self.timestamp, "sender": self.sender},
            separators=(",", ":"),
        )

    @classmethod
    def from_json(cls, raw: str) -> "NetworkMessage":
        payload = json.loads(raw)
        return cls(
            type=payload["type"],
            data=payload.get("data", {}),
            timestamp=payload.get("timestamp", time.time()),
            sender=payload.get("sender", ""),
        )
