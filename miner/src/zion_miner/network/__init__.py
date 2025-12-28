"""
📡 Pool Client - Stratum & XMRig Protocol Support
================================================

Async pool communication with job management.
"""

import asyncio
import json
import logging
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MiningJob:
    """Mining job from pool"""
    job_id: str
    algorithm: str
    blob: Optional[bytes] = None  # XMRig format
    target: str = "ffffffff"
    height: int = 0
    seed_hash: Optional[str] = None
    difficulty: int = 1
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class PoolClient:
    """
    Async pool client supporting XMRig and Stratum protocols
    
    Features:
    - Auto-reconnect
    - Keepalive
    - Job queue
    - Share submission
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        wallet: str,
        worker: str = "zion-miner",
        algorithm: str = "cosmic_harmony",
        protocol: str = "xmrig"  # or "stratum"
    ):
        self.host = host
        self.port = port
        self.wallet = wallet
        self.worker = worker
        self.algorithm = algorithm
        self.protocol = protocol
        
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connected = False
        self.authenticated = False
        
        self.current_job: Optional[MiningJob] = None
        self.miner_id: Optional[str] = None
        
        # Callbacks
        self.on_job_callback: Optional[Callable] = None
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None
        
        # Stats
        self.shares_submitted = 0
        self.shares_accepted = 0
        self.shares_rejected = 0
        self.last_share_time = 0.0
        
        self._tasks = []
        self._running = False
    
    async def connect(self) -> bool:
        """Connect to pool"""
        try:
            logger.info(f"🔗 Connecting to {self.host}:{self.port}...")
            
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            
            self.connected = True
            logger.info(f"✅ Connected to pool")
            
            if self.on_connect_callback:
                await self.on_connect_callback()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.connected = False
            return False
    
    async def login(self) -> bool:
        """Authenticate with pool"""
        if not self.connected:
            return False
        
        try:
            if self.protocol == "xmrig":
                return await self._login_xmrig()
            elif self.protocol == "stratum":
                return await self._login_stratum()
            else:
                logger.error(f"Unknown protocol: {self.protocol}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
    
    async def _login_xmrig(self) -> bool:
        """XMRig protocol login"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "login",
            "params": {
                "login": self.wallet,
                "pass": self.worker,
                "agent": "ZIONMiner/2.9.0",
                "algo": self.algorithm
            }
        }
        
        await self._send_json(request)
        response = await self._recv_json()
        
        if not response:
            return False
        
        result = response.get("result")
        if not result:
            error = response.get("error", {})
            logger.error(f"Login failed: {error.get('message', 'Unknown error')}")
            return False
        
        self.miner_id = result.get("id")
        self.authenticated = True
        
        # Extract job if present
        job_data = result.get("job")
        if job_data:
            self._handle_job(job_data)
        
        logger.info(f"✅ Authenticated: {self.miner_id}")
        return True
    
    async def _login_stratum(self) -> bool:
        """Stratum protocol login (subscribe + authorize)"""
        # Subscribe
        subscribe_req = {
            "id": 1,
            "method": "mining.subscribe",
            "params": ["ZIONMiner/2.9.0"]
        }
        await self._send_json(subscribe_req)
        subscribe_resp = await self._recv_json()
        
        if not subscribe_resp or not subscribe_resp.get("result"):
            return False
        
        # Authorize
        auth_req = {
            "id": 2,
            "method": "mining.authorize",
            "params": [f"{self.wallet}.{self.worker}", "x"]
        }
        await self._send_json(auth_req)
        auth_resp = await self._recv_json()
        
        if auth_resp and auth_resp.get("result"):
            self.authenticated = True
            logger.info("✅ Authenticated (Stratum)")
            return True
        
        return False
    
    async def submit_share(self, job_id: str, nonce: str, result: str) -> bool:
        """Submit mining share"""
        if not self.authenticated:
            logger.warning("⚠️  Not authenticated, cannot submit share")
            return False
        
        try:
            if self.protocol == "xmrig":
                request = {
                    "jsonrpc": "2.0",
                    "id": self.shares_submitted + 10,
                    "method": "submit",
                    "params": {
                        "id": self.miner_id,
                        "job_id": job_id,
                        "nonce": nonce,
                        "result": result
                    }
                }
            else:  # stratum
                request = {
                    "id": self.shares_submitted + 10,
                    "method": "mining.submit",
                    "params": [
                        f"{self.wallet}.{self.worker}",
                        job_id,
                        nonce,
                        result
                    ]
                }
            
            await self._send_json(request)
            self.shares_submitted += 1
            self.last_share_time = time.time()
            
            logger.info(f"📤 Share submitted: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Share submission failed: {e}")
            return False
    
    def _handle_job(self, job_data: Dict):
        """Handle new job from pool"""
        try:
            job = MiningJob(
                job_id=job_data.get("job_id", ""),
                algorithm=job_data.get("algo", self.algorithm),
                blob=bytes.fromhex(job_data.get("blob", "")) if job_data.get("blob") else None,
                target=job_data.get("target", "ffffffff"),
                height=job_data.get("height", 0),
                seed_hash=job_data.get("seed_hash"),
                difficulty=int(job_data.get("difficulty", 1))
            )
            
            self.current_job = job
            
            logger.info(f"📦 New job: {job.job_id} | height={job.height} | diff={job.difficulty}")
            
            if self.on_job_callback:
                asyncio.create_task(self.on_job_callback(job))
                
        except Exception as e:
            logger.error(f"❌ Failed to parse job: {e}")
    
    async def _send_json(self, data: Dict):
        """Send JSON message"""
        if not self.writer:
            raise RuntimeError("Not connected")
        
        msg = json.dumps(data) + "\n"
        self.writer.write(msg.encode())
        await self.writer.drain()
    
    async def _recv_json(self) -> Optional[Dict]:
        """Receive JSON message"""
        if not self.reader:
            return None
        
        try:
            line = await asyncio.wait_for(self.reader.readline(), timeout=30.0)
            if not line:
                return None
            
            return json.loads(line.decode().strip())
            
        except asyncio.TimeoutError:
            logger.debug("⏱️  Receive timeout (no message)")
            return None
        except Exception as e:
            logger.error(f"❌ Receive error: {e}")
            return None
    
    async def _message_loop(self):
        """Background message handler"""
        timeout_count = 0
        max_consecutive_timeouts = 20
        
        while self._running and self.connected:
            try:
                msg = await self._recv_json()
                if msg is None:
                    timeout_count += 1
                    if timeout_count >= max_consecutive_timeouts:
                        logger.warning("❌ Too many timeouts, connection lost")
                        self.connected = False
                        break
                    continue
                
                # Reset timeout counter on successful receive
                timeout_count = 0
                
                # Handle different message types
                method = msg.get("method")
                
                if method == "job":
                    # New job notification
                    params = msg.get("params", {})
                    self._handle_job(params)
                    
                elif "result" in msg:
                    # Response to submit
                    result = msg.get("result")
                    if result and result.get("status") == "OK":
                        self.shares_accepted += 1
                        logger.info(f"✅ Share accepted ({self.shares_accepted}/{self.shares_submitted})")
                    else:
                        self.shares_rejected += 1
                        logger.warning(f"❌ Share rejected ({self.shares_rejected}/{self.shares_submitted})")
                        
            except Exception as e:
                logger.error(f"❌ Message loop error: {e}")
                await asyncio.sleep(1)
        
        if self.on_disconnect_callback:
            await self.on_disconnect_callback()
    
    async def start(self):
        """Start pool client"""
        self._running = True
        
        if not await self.connect():
            return False
        
        if not await self.login():
            return False
        
        # Start message loop
        task = asyncio.create_task(self._message_loop())
        self._tasks.append(task)
        
        return True
    
    async def stop(self):
        """Stop pool client"""
        self._running = False
        
        # Cancel tasks
        for task in self._tasks:
            task.cancel()
        
        # Close connection
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except:
                pass
        
        self.connected = False
        self.authenticated = False
        
        logger.info("🛑 Pool client stopped")
