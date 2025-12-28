"""
⛏️ ZION Miner v2.9 - Modular Mining Client
==========================================

Modulární architektura:
- algorithms/ - Native mining algorithms (Cosmic, RandomX, Yescrypt)
- network/ - Pool communication (Stratum, XMRig protocol)
- metrics/ - Real-time performance monitoring
- config/ - Configuration management

Main components:
- ZionMiner - Main orchestrator
- AlgorithmEngine - Algorithm detection and execution
- PoolClient - Pool connection and job management
- MetricsCollector - Performance tracking
"""

from .zion_miner_v2_9 import MinerConfig, ZionMiner
from .algorithms import AlgorithmEngine

__version__ = "2.9.0"
__all__ = ["ZionMiner", "MinerConfig", "AlgorithmEngine"]
