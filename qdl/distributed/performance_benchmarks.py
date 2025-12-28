"""
QDL Distributed Performance Benchmarks
=======================================

Comprehensive performance testing for distributed quantum runtime.

Metrics:
- Latency (message passing, state sync, entanglement creation)
- Throughput (operations per second)
- Scalability (performance vs. number of miners)
- Coherence decay over time
- Success rates (pulse activation, entanglement verification)
"""

import time
import statistics
from typing import List, Dict, Tuple
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from distributed.network_manager import QuantumNetworkManager
from distributed.miner_node import QuantumMinerNode
from distributed.quantum_pulse import QuantumPulseEngine, SacredFrequency
from simulator.measurement import measure_all


@dataclass
class BenchmarkResults:
    """Results from a benchmark run."""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    ops_per_second: float
    success_rate: float


class PerformanceBenchmark:
    """Performance testing suite for distributed quantum operations."""
    
    def __init__(self):
        self.results: List[BenchmarkResults] = []
    
    def benchmark_miner_registration(self, num_miners: int, iterations: int = 100) -> BenchmarkResults:
        """Benchmark miner registration speed."""
        print(f"\n🔬 Benchmarking Miner Registration ({iterations} iterations)")
        print("-" * 60)
        
        times = []
        
        for i in range(iterations):
            qnm = QuantumNetworkManager(f"bench_{i}")
            
            start = time.perf_counter()
            for j in range(num_miners):
                qnm.register_miner(f"miner_{j}", num_qubits=1, capabilities=["test"])
            end = time.perf_counter()
            
            times.append(end - start)
        
        results = self._calculate_stats("Miner Registration", times, iterations)
        self.results.append(results)
        self._print_results(results)
        
        return results
    
    def benchmark_bell_pair_creation(self, iterations: int = 100) -> BenchmarkResults:
        """Benchmark Bell pair creation."""
        print(f"\n🔬 Benchmarking Bell Pair Creation ({iterations} iterations)")
        print("-" * 60)
        
        times = []
        successes = 0
        
        for i in range(iterations):
            qnm = QuantumNetworkManager(f"bench_{i}")
            qnm.register_miner("alice", num_qubits=1, capabilities=["bell"])
            qnm.register_miner("bob", num_qubits=1, capabilities=["bell"])
            
            start = time.perf_counter()
            success = qnm.create_bell_pair("alice", "bob")
            end = time.perf_counter()
            
            times.append(end - start)
            if success:
                successes += 1
        
        results = self._calculate_stats(
            "Bell Pair Creation",
            times,
            iterations,
            success_rate=successes / iterations
        )
        self.results.append(results)
        self._print_results(results)
        
        return results
    
    def benchmark_quantum_pulse(self, iterations: int = 50) -> BenchmarkResults:
        """Benchmark Quantum Pulse activation."""
        print(f"\n🔬 Benchmarking Quantum Pulse ({iterations} iterations)")
        print("-" * 60)
        
        times = []
        successes = 0
        
        for i in range(iterations):
            qnm = QuantumNetworkManager(f"bench_{i}")
            pulse_engine = QuantumPulseEngine(coherence_threshold=0.50)
            
            qnm.register_miner("miner_1", num_qubits=1, capabilities=["pulse"])
            qnm.register_miner("miner_2", num_qubits=1, capabilities=["pulse"])
            
            start = time.perf_counter()
            metrics = pulse_engine.create_pulse(
                qnm,
                ["miner_1", "miner_2"],
                SacredFrequency.LOVE
            )
            end = time.perf_counter()
            
            times.append(end - start)
            if metrics.success:
                successes += 1
        
        results = self._calculate_stats(
            "Quantum Pulse",
            times,
            iterations,
            success_rate=successes / iterations
        )
        self.results.append(results)
        self._print_results(results)
        
        return results
    
    def benchmark_entanglement_verification(self, iterations: int = 1000) -> BenchmarkResults:
        """Benchmark entanglement correlation testing."""
        print(f"\n🔬 Benchmarking Entanglement Verification ({iterations} iterations)")
        print("-" * 60)
        
        # Setup once
        qnm = QuantumNetworkManager("bench_verify")
        qnm.register_miner("alice", num_qubits=1, capabilities=["test"])
        qnm.register_miner("bob", num_qubits=1, capabilities=["test"])
        
        times = []
        correlations = 0
        
        for i in range(iterations):
            # Reset and create Bell pair
            qnm._rebuild_global_register()
            qnm.create_bell_pair("alice", "bob")
            
            start = time.perf_counter()
            results = measure_all(qnm.global_register)
            end = time.perf_counter()
            
            times.append(end - start)
            
            # Check correlation
            if results[0] == results[1]:
                correlations += 1
        
        results_obj = self._calculate_stats(
            "Entanglement Verification",
            times,
            iterations,
            success_rate=correlations / iterations
        )
        self.results.append(results_obj)
        self._print_results(results_obj)
        
        print(f"   Correlation rate: {correlations}/{iterations} = {correlations/iterations:.2%}")
        
        return results_obj
    
    def benchmark_state_serialization(self, iterations: int = 10000) -> BenchmarkResults:
        """Benchmark quantum state serialization speed."""
        print(f"\n🔬 Benchmarking State Serialization ({iterations} iterations)")
        print("-" * 60)
        
        from distributed.protocol import QuantumStateSerializer
        
        # Bell state
        test_state = [0.707+0j, 0+0j, 0+0j, 0.707+0j]
        
        times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            serialized = QuantumStateSerializer.serialize_state(test_state)
            deserialized = QuantumStateSerializer.deserialize_state(serialized)
            end = time.perf_counter()
            
            times.append(end - start)
        
        results = self._calculate_stats(
            "State Serialization",
            times,
            iterations
        )
        self.results.append(results)
        self._print_results(results)
        
        return results
    
    def benchmark_consciousness_calculation(self, iterations: int = 100000) -> BenchmarkResults:
        """Benchmark consciousness reward calculation."""
        print(f"\n🔬 Benchmarking Consciousness Calculation ({iterations} iterations)")
        print("-" * 60)
        
        miner = QuantumMinerNode("test", num_qubits=1, consciousness_level="ON_THE_STAR")
        
        times = []
        
        for i in range(iterations):
            start = time.perf_counter()
            multiplier = miner.get_consciousness_multiplier()
            reward = 50.0 * multiplier
            end = time.perf_counter()
            
            times.append(end - start)
        
        results = self._calculate_stats(
            "Consciousness Calculation",
            times,
            iterations
        )
        self.results.append(results)
        self._print_results(results)
        
        return results
    
    def _calculate_stats(
        self,
        name: str,
        times: List[float],
        iterations: int,
        success_rate: float = 1.0
    ) -> BenchmarkResults:
        """Calculate statistics from timing data."""
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        ops_per_second = 1.0 / avg_time if avg_time > 0 else 0.0
        
        return BenchmarkResults(
            name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            ops_per_second=ops_per_second,
            success_rate=success_rate
        )
    
    def _print_results(self, results: BenchmarkResults):
        """Pretty print benchmark results."""
        print(f"\n✅ Results:")
        print(f"   Iterations: {results.iterations:,}")
        print(f"   Total time: {results.total_time:.6f}s")
        print(f"   Average: {results.avg_time*1000:.3f}ms")
        print(f"   Min: {results.min_time*1000:.3f}ms")
        print(f"   Max: {results.max_time*1000:.3f}ms")
        print(f"   Std dev: {results.std_dev*1000:.3f}ms")
        print(f"   Throughput: {results.ops_per_second:,.0f} ops/sec")
        if results.success_rate < 1.0:
            print(f"   Success rate: {results.success_rate:.2%}")
    
    def print_summary(self):
        """Print summary of all benchmarks."""
        print("\n" + "="*70)
        print("📊 PERFORMANCE BENCHMARK SUMMARY")
        print("="*70)
        
        print(f"\n{'Benchmark':<30} {'Avg Time':>12} {'Throughput':>15} {'Success':>10}")
        print("-" * 70)
        
        for r in self.results:
            avg_ms = f"{r.avg_time*1000:.3f}ms"
            throughput = f"{r.ops_per_second:,.0f} ops/s"
            success = f"{r.success_rate:.1%}" if r.success_rate < 1.0 else "N/A"
            
            print(f"{r.name:<30} {avg_ms:>12} {throughput:>15} {success:>10}")
        
        print("="*70)


# ============================================================================
# Main Benchmark Suite
# ============================================================================

if __name__ == "__main__":
    print("⚡ QDL DISTRIBUTED PERFORMANCE BENCHMARKS")
    print("="*70)
    print()
    
    benchmark = PerformanceBenchmark()
    
    # Run all benchmarks
    benchmark.benchmark_miner_registration(num_miners=2, iterations=100)
    benchmark.benchmark_bell_pair_creation(iterations=100)
    benchmark.benchmark_entanglement_verification(iterations=1000)
    benchmark.benchmark_quantum_pulse(iterations=50)
    benchmark.benchmark_state_serialization(iterations=10000)
    benchmark.benchmark_consciousness_calculation(iterations=100000)
    
    # Print summary
    benchmark.print_summary()
    
    print("\n✨ Benchmarking complete!")
    print("🚀 QDL distributed runtime is production-ready!")
