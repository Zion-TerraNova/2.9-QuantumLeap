"""
🔧 Algorithm Engine - Native ZION Mining Algorithms
==================================================

Lazy-loading wrapper pro native mining libraries s fallback na Python.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Global cache for loaded algorithms
_loaded_algorithms: Dict[str, Any] = {}
_algorithm_module = None


@dataclass
class AlgorithmInfo:
    """Algorithm metadata"""
    name: str
    hashrate: float  # Expected H/s
    available: bool
    native: bool  # True if using native library
    threads: int
    error: Optional[str] = None


def _lazy_load_algorithms():
    """Lazy load algorithm module to avoid startup delay"""
    global _algorithm_module
    if _algorithm_module is None:
        logger.info("🔧 Loading native algorithm libraries...")
        try:
            from .. import algorithms_registry
            _algorithm_module = algorithms_registry
            logger.info("✅ Algorithm module loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load algorithms: {e}")
            raise
    return _algorithm_module


class AlgorithmEngine:
    """
    Algorithm engine with lazy loading and fallback support
    
    Features:
    - Lazy initialization (don't load until needed)
    - Native library support (C++/Cython)
    - Python fallbacks
    - Performance metrics
    """
    
    def __init__(self):
        self.available_algorithms: Dict[str, AlgorithmInfo] = {}
        self._initialized = False
    
    def initialize(self, algorithms: list = None):
        """
        Initialize requested algorithms
        
        Args:
            algorithms: List of algorithm names to load (None = all)
        """
        if self._initialized:
            return
        
        logger.info("🚀 Initializing algorithm engine...")
        
        # Default algorithms
        if algorithms is None:
            algorithms = ["cosmic_harmony", "randomx", "yescrypt"]
        
        # Lazy load module
        algo_module = _lazy_load_algorithms()
        
        # Detect available algorithms
        for algo_name in algorithms:
            try:
                is_avail = algo_module.is_available(algo_name)
                
                if is_avail:
                    # Get algorithm info
                    info = AlgorithmInfo(
                        name=algo_name,
                        hashrate=0.0,  # Will be benchmarked
                        available=True,
                        native=True,  # Assume native if available
                        threads=1
                    )
                    self.available_algorithms[algo_name] = info
                    logger.info(f"✅ {algo_name}: available")
                else:
                    # Algorithm not available - still track it
                    info = AlgorithmInfo(
                        name=algo_name,
                        hashrate=0.0,
                        available=False,
                        native=False,
                        threads=0
                    )
                    self.available_algorithms[algo_name] = info
                    logger.warning(f"⚠️  {algo_name}: not available")
                    
            except Exception as e:
                logger.error(f"❌ {algo_name}: failed to load - {e}")
                self.available_algorithms[algo_name] = AlgorithmInfo(
                    name=algo_name,
                    hashrate=0.0,
                    available=False,
                    native=False,
                    threads=0,
                    error=str(e)
                )
        
        self._initialized = True
        logger.info(f"✅ Algorithm engine initialized ({len(self.available_algorithms)} algorithms)")
    
    def hash(self, algorithm: str, data: bytes, nonce: int) -> str:
        """
        Compute hash using specified algorithm
        
        Args:
            algorithm: Algorithm name
            data: Input data
            nonce: Nonce value
            
        Returns:
            Hash hex string
        """
        if not self._initialized:
            self.initialize([algorithm])
        
        algo_module = _lazy_load_algorithms()
        return algo_module.get_hash(algorithm, data, nonce)
    
    def is_available(self, algorithm: str) -> bool:
        """Check if algorithm is available"""
        if not self._initialized:
            self.initialize([algorithm])
        
        return self.available_algorithms.get(algorithm, AlgorithmInfo(
            name=algorithm,
            hashrate=0,
            available=False,
            native=False,
            threads=0
        )).available
    
    def get_info(self, algorithm: str) -> Optional[AlgorithmInfo]:
        """Get algorithm info"""
        return self.available_algorithms.get(algorithm)
    
    def list_available(self) -> list:
        """List all available algorithms"""
        return [name for name, info in self.available_algorithms.items() if info.available]
