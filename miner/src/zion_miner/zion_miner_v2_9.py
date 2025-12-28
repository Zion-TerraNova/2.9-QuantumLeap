"""
⛏️ ZION Miner v2.9 - Main Orchestrator
======================================

Modulární mining client s nativními algoritmy.
"""

import asyncio
import logging
import signal
import time
from typing import Optional
from dataclasses import dataclass

from .algorithms import AlgorithmEngine
from .network import PoolClient, MiningJob
from .metrics import MetricsCollector

logger = logging.getLogger(__name__)


@dataclass
class MinerConfig:
    """Miner configuration"""
    # Required
    wallet_address: str
    
    # Optional with defaults
    pool_host: str = "localhost"
    pool_port: int = 3333
    worker_name: str = "zion-miner"
    algorithm: str = "randomx"
    threads: int = 1
    protocol: str = "xmrig"  # or "stratum"
    
    # Performance
    intensity: int = 1  # Concurrent nonce searches per thread
    update_interval: float = 2.0  # Stats update interval
    
    # Display
    stats_enabled: bool = True
    stats_interval: float = 10.0  # Print stats every N seconds


class ZionMiner:
    """
    ZION Universal Miner v2.9
    
    Features:
    - Native algorithm support (Cosmic Harmony, RandomX, Yescrypt)
    - Async pool communication
    - Real-time metrics
    - Auto-reconnect
    - Graceful shutdown
    """
    
    VERSION = "2.9.0"
    
    def __init__(self, config: MinerConfig):
        self.config = config
        
        # Components
        self.algo_engine = AlgorithmEngine()
        self.pool_client: Optional[PoolClient] = None
        self.metrics = MetricsCollector(
            algorithm=config.algorithm,
            threads=config.threads
        )
        
        # State
        self.running = False
        self.current_job: Optional[MiningJob] = None
        self.total_hashes = 0
        
        # Tasks
        self._tasks = []
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        logger.info("🛑 Received shutdown signal")
        self.running = False
    
    async def initialize(self):
        """Initialize miner components"""
        logger.info(f"🚀 Initializing ZION Miner v{self.VERSION}")
        logger.info(f"   Algorithm: {self.config.algorithm}")
        logger.info(f"   Threads: {self.config.threads}")
        logger.info(f"   Pool: {self.config.pool_host}:{self.config.pool_port}")
        
        # Initialize algorithm engine
        self.algo_engine.initialize([self.config.algorithm])
        
        if not self.algo_engine.is_available(self.config.algorithm):
            raise RuntimeError(f"Algorithm {self.config.algorithm} not available")
        
        # Create pool client
        self.pool_client = PoolClient(
            host=self.config.pool_host,
            port=self.config.pool_port,
            wallet=self.config.wallet_address,
            worker=self.config.worker_name,
            algorithm=self.config.algorithm,
            protocol=self.config.protocol
        )
        
        # Setup callbacks
        self.pool_client.on_job_callback = self._on_new_job
        self.pool_client.on_connect_callback = self._on_connect
        self.pool_client.on_disconnect_callback = self._on_disconnect
        
        logger.info("✅ Miner initialized")
    
    async def _on_connect(self):
        """Called when connected to pool"""
        logger.info(f"✅ Connected to {self.config.pool_host}:{self.config.pool_port}")
    
    async def _on_disconnect(self):
        """Called when disconnected from pool"""
        logger.warning("❌ Disconnected from pool")
        # TODO: Implement auto-reconnect
    
    async def _on_new_job(self, job: MiningJob):
        """Called when new job received"""
        self.current_job = job
        logger.info(f"📦 New job: {job.job_id} | height={job.height} | diff={job.difficulty}")
    
    async def _mining_worker(self, worker_id: int):
        """
        Mining worker thread
        
        Args:
            worker_id: Worker thread ID
        """
        logger.info(f"⚙️  Worker {worker_id} started")
        
        nonce = worker_id  # Start nonce
        nonce_step = self.config.threads * self.config.intensity
        
        while self.running:
            job = self.current_job
            
            if not job or not job.blob:
                await asyncio.sleep(0.1)
                continue
            
            # Mine multiple nonces per iteration (intensity)
            for _ in range(self.config.intensity):
                if not self.running or job != self.current_job:
                    break
                
                try:
                    # Apply nonce to blob for hashing (XMRig style for RandomX)
                    blob_for_hash = self._apply_nonce_to_blob(job.blob, f"{nonce:08x}")
                    
                    # Compute hash
                    hash_result = self.algo_engine.hash(
                        self.config.algorithm,
                        bytes.fromhex(blob_for_hash),
                        0  # Nonce already applied to blob
                    )
                    
                    self.total_hashes += 1
                    
                    # Check if hash meets target
                    if self._check_target(hash_result, job.target):
                        logger.info(f"💎 Found share! Nonce: {nonce:08x}")
                        
                        # Submit share
                        await self.pool_client.submit_share(
                            job_id=job.job_id,
                            nonce=f"{nonce:08x}",
                            result=hash_result
                        )
                        
                        # Record in metrics
                        self.metrics.record_share(
                            accepted=True,  # Will be updated when pool responds
                            difficulty=job.difficulty
                        )
                    
                    # Increment nonce
                    nonce += nonce_step
                    
                except Exception as e:
                    logger.error(f"❌ Mining error: {e}")
                    await asyncio.sleep(1)
            
            # Yield control periodically
            await asyncio.sleep(0)
        
        logger.info(f"⚙️  Worker {worker_id} stopped")
    
    def _apply_nonce_to_blob(self, blob: str, nonce: str) -> str:
        """
        Apply nonce to block blob (XMRig style)
        
        Args:
            blob: Block blob hex
            nonce: Nonce hex (8 chars)
            
        Returns:
            Blob with nonce applied
        """
        if len(nonce) != 8:
            raise ValueError(f"Nonce must be 8 hex chars, got {len(nonce)}")
        
        if len(blob) < 84:  # Need at least 42 bytes
            raise ValueError(f"Blob too short: {len(blob)} chars")
        
        # Nonce position: byte 39 = hex char 78
        nonce_pos = 78
        
        # Replace nonce in blob
        blob_with_nonce = (
            blob[:nonce_pos] +
            nonce +
            blob[nonce_pos + 8:]
        )
        
        return blob_with_nonce
    
    def _check_target(self, hash_hex: str, target_hex: str) -> bool:
        """
        Check if hash meets target difficulty
        
        Args:
            hash_hex: Hash hex string
            target_hex: Target hex string
            
        Returns:
            True if hash <= target
        """
        try:
            hash_int = int(hash_hex, 16)
            target_int = int(target_hex, 16)
            return hash_int <= target_int
        except ValueError:
            return False
    
    async def _metrics_loop(self):
        """Background metrics update loop"""
        last_print = time.time()
        
        while self.running:
            # Update hashrate
            self.metrics.update_hashrate(self.total_hashes)
            
            # Update share stats from pool
            if self.pool_client:
                self.metrics.stats.shares_total = self.pool_client.shares_submitted
                self.metrics.stats.shares_accepted = self.pool_client.shares_accepted
                self.metrics.stats.shares_rejected = self.pool_client.shares_rejected
            
            # Print stats periodically
            if self.config.stats_enabled:
                now = time.time()
                if now - last_print >= self.config.stats_interval:
                    self.metrics.print_stats()
                    last_print = now
            
            await asyncio.sleep(self.config.update_interval)
    
    async def start(self):
        """Start mining"""
        await self.initialize()
        
        # Connect to pool
        if not await self.pool_client.start():
            raise RuntimeError("Failed to connect to pool")
        
        self.running = True
        
        # Start mining workers
        for i in range(self.config.threads):
            task = asyncio.create_task(self._mining_worker(i))
            self._tasks.append(task)
        
        # Start metrics loop
        metrics_task = asyncio.create_task(self._metrics_loop())
        self._tasks.append(metrics_task)
        
        logger.info(f"⛏️  Mining started with {self.config.threads} threads")
        
        # Wait for shutdown
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop mining"""
        logger.info("🛑 Stopping miner...")
        
        self.running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to finish
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        # Stop pool client
        if self.pool_client:
            await self.pool_client.stop()
        
        # Print final stats
        if self.config.stats_enabled:
            print("\n" + "=" * 60)
            print("📊 Final Statistics:")
            print("=" * 60)
            self.metrics.print_stats()
        
        logger.info("✅ Miner stopped")


# CLI entry point
async def main():
    """Main entry point for CLI"""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python -m zion_miner <pool_host> <pool_port> <wallet_address> [worker_name] [algorithm]")
        print("\nExample:")
        print("  python -m zion_miner example.com 3333 zion1abc... worker1 cosmic_harmony")
        sys.exit(1)
    
    config = MinerConfig(
        pool_host=sys.argv[1],
        pool_port=int(sys.argv[2]),
        wallet_address=sys.argv[3],
        worker_name=sys.argv[4] if len(sys.argv) > 4 else "zion-miner",
        algorithm=sys.argv[5] if len(sys.argv) > 5 else "cosmic_harmony",
        threads=2,
        stats_enabled=True,
        stats_interval=10.0
    )
    
    miner = ZionMiner(config)
    await miner.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    asyncio.run(main())
