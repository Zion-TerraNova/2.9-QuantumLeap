from __future__ import annotations

import argparse
import asyncio
import logging
import socket
import time
from typing import Optional

from .message import NetworkMessage
from .peer_store import PeerStore

logger = logging.getLogger(__name__)


class Node:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8333,
        node_id: Optional[str] = None,
        max_peers: int = 50,
    ):
        self.host = host
        self.port = port
        self.node_id = node_id or socket.gethostname()
        self.peers = PeerStore(max_peers=max_peers)
        self._server: Optional[asyncio.base_events.Server] = None
        self._running = False

    async def start(self) -> None:
        self._running = True
        self._server = await asyncio.start_server(self._handle_conn, self.host, self.port)
        addrs = ", ".join(str(s.getsockname()) for s in self._server.sockets or [])
        logger.info("node_listening", extra={"addrs": addrs, "node_id": self.node_id})

    async def stop(self) -> None:
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def connect(self, host: str, port: int) -> None:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            self.peers.upsert(host, port)

            # send handshake
            msg = NetworkMessage(
                type="handshake",
                data={"node_id": self.node_id, "version": "2.9.0", "timestamp": int(time.time()), "port": self.port},
                sender=self.node_id,
            )
            writer.write((msg.to_json() + "\n").encode())
            await writer.drain()

            asyncio.create_task(self._listen(reader, writer, peer=f"{host}:{port}"))
        except Exception as e:
            logger.warning("connect_failed", extra={"peer": f"{host}:{port}", "error": str(e)})

    async def _handle_conn(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        peername = writer.get_extra_info("peername")
        peer = f"{peername[0]}:{peername[1]}" if peername else "unknown"
        logger.info("peer_connected", extra={"peer": peer})
        asyncio.create_task(self._listen(reader, writer, peer=peer))

    async def _listen(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, peer: str) -> None:
        try:
            while self._running:
                line = await reader.readline()
                if not line:
                    break
                raw = line.decode(errors="replace").strip()
                if not raw:
                    continue
                msg = NetworkMessage.from_json(raw)
                await self._dispatch(msg, peer, writer)
        except Exception as e:
            logger.debug("listen_error", extra={"peer": peer, "error": str(e)})
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            logger.info("peer_disconnected", extra={"peer": peer})

    async def _dispatch(self, msg: NetworkMessage, peer: str, writer: asyncio.StreamWriter) -> None:
        if msg.type == "handshake":
            await self._on_handshake(msg, peer, writer)
        elif msg.type == "ping":
            await self._send(writer, NetworkMessage(type="pong", data={"timestamp": msg.timestamp}, sender=self.node_id))
        elif msg.type == "get_peers":
            await self._send(writer, NetworkMessage(type="peers", data={"peers": self.peers.as_dicts()}, sender=self.node_id))
        elif msg.type == "peers":
            self.peers.merge(msg.data.get("peers", []))
        # unknown types are ignored in the skeleton

    async def _on_handshake(self, msg: NetworkMessage, peer: str, writer: asyncio.StreamWriter) -> None:
        try:
            port = int(msg.data.get("port", 0))
            host = peer.split(":")[0]
            if port > 0:
                self.peers.upsert(host, port)
        except Exception:
            pass

        # reply basic handshake
        reply = NetworkMessage(
            type="handshake",
            data={"node_id": self.node_id, "version": "2.9.0", "timestamp": int(time.time()), "port": self.port},
            sender=self.node_id,
        )
        await self._send(writer, reply)

    async def _send(self, writer: asyncio.StreamWriter, msg: NetworkMessage) -> None:
        writer.write((msg.to_json() + "\n").encode())
        await writer.drain()


def _parse_seed(seed: str) -> tuple[str, int]:
    host, port_s = seed.rsplit(":", 1)
    return host, int(port_s)


def main() -> None:
    parser = argparse.ArgumentParser(description="ZION Node Skeleton")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8333)
    parser.add_argument("--seed", action="append", default=[], help="Seed peer host:port (repeatable)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    async def runner() -> None:
        node = Node(host=args.host, port=args.port)
        await node.start()
        for s in args.seed:
            host, port = _parse_seed(s)
            await node.connect(host, port)
        # keep running
        while True:
            await asyncio.sleep(1)

    asyncio.run(runner())


if __name__ == "__main__":
    main()
