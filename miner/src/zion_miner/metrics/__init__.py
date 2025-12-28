"""
📊 Mining Metrics - Real-time Performance Tracking
=================================================

Comprehensive mining statistics and monitoring.
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class MiningStats:
    """Mining statistics snapshot"""
    hashrate_current: float = 0.0
    hashrate_avg_1min: float = 0.0
    hashrate_avg_5min: float = 0.0
    hashrate_avg_15min: float = 0.0
    
    shares_total: int = 0
    shares_accepted: int = 0
    shares_rejected: int = 0
    
    uptime: float = 0.0
    start_time: float = field(default_factory=time.time)
    
    pool_difficulty: int = 1
    pool_latency: float = 0.0
    
    algorithm: str = "unknown"
    threads: int = 0
    
    # Hardware metrics (optional)
    cpu_temp: float = 0.0
    cpu_usage: float = 0.0
    gpu_temp: float = 0.0
    gpu_fan: int = 0
    gpu_power: float = 0.0
    
    def acceptance_rate(self) -> float:
        """Calculate share acceptance rate"""
        if self.shares_total == 0:
            return 0.0
        return (self.shares_accepted / self.shares_total) * 100.0
    
    def uptime_str(self) -> str:
        """Format uptime as human-readable string"""
        seconds = int(self.uptime)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "hashrate": {
                "current": self.hashrate_current,
                "1min": self.hashrate_avg_1min,
                "5min": self.hashrate_avg_5min,
                "15min": self.hashrate_avg_15min,
            },
            "shares": {
                "total": self.shares_total,
                "accepted": self.shares_accepted,
                "rejected": self.shares_rejected,
                "acceptance_rate": self.acceptance_rate(),
            },
            "uptime": {
                "seconds": self.uptime,
                "formatted": self.uptime_str(),
            },
            "pool": {
                "difficulty": self.pool_difficulty,
                "latency": self.pool_latency,
            },
            "hardware": {
                "cpu_temp": self.cpu_temp,
                "cpu_usage": self.cpu_usage,
                "gpu_temp": self.gpu_temp,
                "gpu_fan": self.gpu_fan,
                "gpu_power": self.gpu_power,
            }
        }


class MetricsCollector:
    """
    Real-time metrics collector with rolling averages
    
    Features:
    - Rolling hashrate averages (1min, 5min, 15min)
    - Share tracking
    - Hardware monitoring
    - Prometheus export support
    """
    
    def __init__(self, algorithm: str = "unknown", threads: int = 1):
        self.stats = MiningStats(algorithm=algorithm, threads=threads)
        
        # Hashrate history (timestamp, hashrate) for averages
        self.hashrate_history: deque = deque(maxlen=900)  # 15 minutes @ 1Hz
        
        # Share history for detailed tracking
        self.share_history: List[Dict] = []
        
        self._last_hashes = 0
        self._last_time = time.time()
    
    def update_hashrate(self, total_hashes: int):
        """
        Update hashrate from total hash count
        
        Args:
            total_hashes: Total hashes computed since start
        """
        now = time.time()
        elapsed = now - self._last_time
        
        if elapsed > 0:
            # Calculate instantaneous hashrate
            delta_hashes = total_hashes - self._last_hashes
            hashrate = delta_hashes / elapsed
            
            # Update current
            self.stats.hashrate_current = hashrate
            
            # Add to history
            self.hashrate_history.append((now, hashrate))
            
            # Calculate averages
            self._calculate_averages()
            
            # Update for next iteration
            self._last_hashes = total_hashes
            self._last_time = now
    
    def _calculate_averages(self):
        """Calculate rolling hashrate averages"""
        if not self.hashrate_history:
            return
        
        now = time.time()
        
        # 1 minute average
        recent_1min = [h for t, h in self.hashrate_history if now - t <= 60]
        if recent_1min:
            self.stats.hashrate_avg_1min = sum(recent_1min) / len(recent_1min)
        
        # 5 minute average
        recent_5min = [h for t, h in self.hashrate_history if now - t <= 300]
        if recent_5min:
            self.stats.hashrate_avg_5min = sum(recent_5min) / len(recent_5min)
        
        # 15 minute average
        if self.hashrate_history:
            all_hashrates = [h for _, h in self.hashrate_history]
            self.stats.hashrate_avg_15min = sum(all_hashrates) / len(all_hashrates)
    
    def record_share(self, accepted: bool, difficulty: int = 1, latency: float = 0.0):
        """
        Record share submission result
        
        Args:
            accepted: Whether share was accepted
            difficulty: Share difficulty
            latency: Submission latency in ms
        """
        self.stats.shares_total += 1
        
        if accepted:
            self.stats.shares_accepted += 1
        else:
            self.stats.shares_rejected += 1
        
        # Update pool stats
        self.stats.pool_difficulty = difficulty
        if latency > 0:
            self.stats.pool_latency = latency
        
        # Record in history
        self.share_history.append({
            "timestamp": time.time(),
            "accepted": accepted,
            "difficulty": difficulty,
            "latency": latency
        })
        
        # Limit history size
        if len(self.share_history) > 1000:
            self.share_history = self.share_history[-1000:]
    
    def update_uptime(self):
        """Update uptime counter"""
        self.stats.uptime = time.time() - self.stats.start_time
    
    def update_hardware(self, cpu_temp=None, cpu_usage=None, gpu_temp=None, gpu_fan=None, gpu_power=None):
        """Update hardware metrics"""
        if cpu_temp is not None:
            self.stats.cpu_temp = cpu_temp
        if cpu_usage is not None:
            self.stats.cpu_usage = cpu_usage
        if gpu_temp is not None:
            self.stats.gpu_temp = gpu_temp
        if gpu_fan is not None:
            self.stats.gpu_fan = gpu_fan
        if gpu_power is not None:
            self.stats.gpu_power = gpu_power
    
    def get_stats(self) -> MiningStats:
        """Get current statistics snapshot"""
        self.update_uptime()
        return self.stats
    
    def print_stats(self):
        """Print formatted statistics to console"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print(f"⛏️  ZION Miner v2.9 - {stats.algorithm.upper()}")
        print("=" * 60)
        print(f"Hashrate:  {stats.hashrate_current:>10.2f} H/s (current)")
        print(f"           {stats.hashrate_avg_1min:>10.2f} H/s (1 min avg)")
        print(f"           {stats.hashrate_avg_5min:>10.2f} H/s (5 min avg)")
        print(f"           {stats.hashrate_avg_15min:>10.2f} H/s (15 min avg)")
        print("-" * 60)
        print(f"Shares:    {stats.shares_accepted}/{stats.shares_total} accepted ({stats.acceptance_rate():.1f}%)")
        print(f"           {stats.shares_rejected} rejected")
        print("-" * 60)
        print(f"Uptime:    {stats.uptime_str()}")
        print(f"Threads:   {stats.threads}")
        print(f"Diff:      {stats.pool_difficulty}")
        
        if stats.cpu_temp > 0:
            print("-" * 60)
            print(f"CPU:       {stats.cpu_temp:.1f}°C | {stats.cpu_usage:.1f}%")
        
        if stats.gpu_temp > 0:
            print(f"GPU:       {stats.gpu_temp:.1f}°C | {stats.gpu_fan}% fan | {stats.gpu_power:.1f}W")
        
        print("=" * 60 + "\n")
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        stats = self.get_stats()
        
        metrics = [
            f"# HELP zion_miner_hashrate_current Current hashrate in H/s",
            f"# TYPE zion_miner_hashrate_current gauge",
            f"zion_miner_hashrate_current {stats.hashrate_current}",
            "",
            f"# HELP zion_miner_hashrate_avg Average hashrate in H/s",
            f"# TYPE zion_miner_hashrate_avg gauge",
            f'zion_miner_hashrate_avg{{period="1min"}} {stats.hashrate_avg_1min}',
            f'zion_miner_hashrate_avg{{period="5min"}} {stats.hashrate_avg_5min}',
            f'zion_miner_hashrate_avg{{period="15min"}} {stats.hashrate_avg_15min}',
            "",
            f"# HELP zion_miner_shares_total Total shares submitted",
            f"# TYPE zion_miner_shares_total counter",
            f"zion_miner_shares_total {stats.shares_total}",
            "",
            f"# HELP zion_miner_shares_accepted Accepted shares",
            f"# TYPE zion_miner_shares_accepted counter",
            f"zion_miner_shares_accepted {stats.shares_accepted}",
            "",
            f"# HELP zion_miner_shares_rejected Rejected shares",
            f"# TYPE zion_miner_shares_rejected counter",
            f"zion_miner_shares_rejected {stats.shares_rejected}",
            "",
            f"# HELP zion_miner_uptime Miner uptime in seconds",
            f"# TYPE zion_miner_uptime counter",
            f"zion_miner_uptime {stats.uptime}",
        ]
        
        return "\n".join(metrics) + "\n"
