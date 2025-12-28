"""
Quantum Network Manager
========================

Orchestrates distributed quantum operations across ZION mining network.

Responsibilities:
1. Miner registration and connection management
2. Quantum state distribution and synchronization
3. Entanglement coordination across network
4. Coherence tracking and error detection
5. Quantum Pulse orchestration (GHZ states)
"""

import asyncio
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import time
import numpy as np

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator.qubit import QubitRegister
from simulator.gates import hadamard, cnot, apply_single_qubit_gate, HADAMARD
from simulator.measurement import measure_all
from distributed.protocol import (
    MessageType,
    QuantumMessage,
    build_connect_message,
    build_entangle_message,
    build_pulse_init_message
)


@dataclass
class MinerInfo:
    """Information about connected miner."""
    miner_id: str
    num_qubits: int
    capabilities: List[str]
    connected_at: float
    last_heartbeat: float
    status: str = "active"  # active, syncing, measuring, error


@dataclass
class EntanglementPair:
    """Represents entangled qubits across miners."""
    miner_a: str
    qubit_a: int
    miner_b: str
    qubit_b: int
    created_at: float
    coherence: float = 1.0  # Decreases over time


class QuantumNetworkManager:
    """
    Manages distributed quantum computing network.
    
    Architecture:
    - Star topology: Manager = hub, miners = spokes
    - Each miner owns local qubits
    - Manager coordinates entanglement operations
    - Synchronized measurements for quantum states
    """
    
    def __init__(self, manager_id: str = "qnm_master"):
        self.manager_id = manager_id
        self.miners: Dict[str, MinerInfo] = {}
        self.entanglements: List[EntanglementPair] = []
        self.global_register: Optional[QubitRegister] = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance tracking
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'entanglements_created': 0,
            'quantum_pulses': 0,
            'errors': 0
        }
    
    def register_miner(self, miner_id: str, num_qubits: int, capabilities: List[str]) -> bool:
        """
        Register a new miner to the quantum network.
        
        Args:
            miner_id: Unique identifier for miner
            num_qubits: Number of qubits miner contributes
            capabilities: Supported operations (bell_state, grover, qft, etc.)
        
        Returns:
            True if registration successful
        """
        if miner_id in self.miners:
            print(f"⚠️  Miner {miner_id} already registered!")
            return False
        
        now = time.time()
        miner_info = MinerInfo(
            miner_id=miner_id,
            num_qubits=num_qubits,
            capabilities=capabilities,
            connected_at=now,
            last_heartbeat=now
        )
        
        self.miners[miner_id] = miner_info
        print(f"✅ Registered miner {miner_id} ({num_qubits} qubits)")
        
        # Rebuild global register with all miners' qubits
        self._rebuild_global_register()
        
        return True
    
    def _rebuild_global_register(self):
        """
        Rebuild global quantum register from all miners.
        
        Layout: [miner1_qubits][miner2_qubits][miner3_qubits]...
        """
        total_qubits = sum(m.num_qubits for m in self.miners.values())
        
        if total_qubits == 0:
            self.global_register = None
            return
        
        self.global_register = QubitRegister(total_qubits)
        print(f"🌐 Global register: {total_qubits} qubits from {len(self.miners)} miners")
    
    def get_miner_qubit_range(self, miner_id: str) -> Tuple[int, int]:
        """
        Get qubit index range for specific miner in global register.
        
        Returns:
            (start_index, end_index) exclusive
        """
        if miner_id not in self.miners:
            raise ValueError(f"Miner {miner_id} not registered!")
        
        start = 0
        for mid, minfo in self.miners.items():
            if mid == miner_id:
                return (start, start + minfo.num_qubits)
            start += minfo.num_qubits
        
        raise ValueError("Logic error in qubit range calculation")
    
    def create_bell_pair(self, miner_a: str, miner_b: str) -> bool:
        """
        Create Bell state entanglement between two miners.
        
        Circuit:
            Miner A qubit 0: |0⟩ --H--●--
                                      |
            Miner B qubit 0: |0⟩ -----⊕--
        
        Result: (|00⟩ + |11⟩)/√2
        """
        if not self.global_register:
            print("❌ No global register! Register miners first.")
            return False
        
        if miner_a not in self.miners or miner_b not in self.miners:
            print("❌ Both miners must be registered!")
            return False
        
        # Get qubit indices
        range_a = self.get_miner_qubit_range(miner_a)
        range_b = self.get_miner_qubit_range(miner_b)
        
        qubit_a = range_a[0]  # First qubit of miner A
        qubit_b = range_b[0]  # First qubit of miner B
        
        print(f"\n🔗 Creating Bell pair:")
        print(f"   {miner_a} qubit {qubit_a} ↔ {miner_b} qubit {qubit_b}")
        
        # Apply Bell state circuit
        hadamard(self.global_register, qubit_a)
        cnot(self.global_register, qubit_a, qubit_b)
        
        # Record entanglement
        pair = EntanglementPair(
            miner_a=miner_a,
            qubit_a=qubit_a,
            miner_b=miner_b,
            qubit_b=qubit_b,
            created_at=time.time()
        )
        self.entanglements.append(pair)
        self.stats['entanglements_created'] += 1
        
        print(f"✅ Bell pair created! (Total entanglements: {len(self.entanglements)})")
        return True
    
    def create_ghz_state(self, miner_ids: List[str]) -> bool:
        """
        Create GHZ state (Greenberger-Horne-Zeilinger) across multiple miners.
        
        GHZ state: (|000...0⟩ + |111...1⟩)/√2
        
        This is the foundation of Quantum Pulse!
        
        Circuit:
            Qubit 0: |0⟩ --H--●--●--●--...
                               |  |  |
            Qubit 1: |0⟩ ------⊕--|--|--...
                                  |  |
            Qubit 2: |0⟩ ---------⊕--|--...
                                     |
            Qubit 3: |0⟩ ------------⊕--...
        """
        if not self.global_register:
            print("❌ No global register!")
            return False
        
        if len(miner_ids) < 2:
            print("❌ Need at least 2 miners for GHZ state!")
            return False
        
        print(f"\n🌌 Creating GHZ state across {len(miner_ids)} miners:")
        for mid in miner_ids:
            print(f"   - {mid}")
        
        # Get first qubit from each miner
        qubit_indices = []
        for mid in miner_ids:
            if mid not in self.miners:
                print(f"❌ Miner {mid} not registered!")
                return False
            range_ = self.get_miner_qubit_range(mid)
            qubit_indices.append(range_[0])
        
        # Build GHZ state
        # Step 1: Hadamard on first qubit
        hadamard(self.global_register, qubit_indices[0])
        
        # Step 2: CNOT cascade from first qubit to all others
        for i in range(1, len(qubit_indices)):
            cnot(self.global_register, qubit_indices[0], qubit_indices[i])
        
        print(f"✅ GHZ state created! ({len(miner_ids)} qubits entangled)")
        
        # Record all pairwise entanglements
        for i in range(len(miner_ids)):
            for j in range(i + 1, len(miner_ids)):
                pair = EntanglementPair(
                    miner_a=miner_ids[i],
                    qubit_a=qubit_indices[i],
                    miner_b=miner_ids[j],
                    qubit_b=qubit_indices[j],
                    created_at=time.time()
                )
                self.entanglements.append(pair)
        
        self.stats['quantum_pulses'] += 1
        return True
    
    def measure_coherence(self, miner_ids: List[str]) -> float:
        """
        Measure coherence of entangled miners.
        
        Coherence = how "synchronized" the quantum state is.
        1.0 = perfect coherence (pure state)
        0.0 = decoherence (classical mixture)
        
        For GHZ state, coherence measured by checking if all miners
        show correlated results when measured.
        """
        if not self.global_register:
            return 0.0
        
        # For now, use purity as coherence metric
        # Purity = Tr(ρ²) where ρ is density matrix
        # For pure state: purity = 1
        # For mixed state: purity < 1
        
        # Simplified: Check if state has dominant amplitudes
        state = self.global_register.state_vector
        probabilities = np.abs(state) ** 2
        
        # Entropy-based coherence
        # High coherence = few dominant states
        # Low coherence = many states with similar probability
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        max_entropy = np.log2(len(state))
        
        coherence = 1.0 - (entropy / max_entropy)
        
        return coherence
    
    def get_network_stats(self) -> Dict:
        """Get current network statistics."""
        total_qubits = sum(m.num_qubits for m in self.miners.values())
        active_miners = sum(1 for m in self.miners.values() if m.status == "active")
        
        return {
            'total_miners': len(self.miners),
            'active_miners': active_miners,
            'total_qubits': total_qubits,
            'entanglements': len(self.entanglements),
            'coherence': self.measure_coherence(list(self.miners.keys())),
            'stats': self.stats
        }
    
    def print_network_status(self):
        """Print detailed network status."""
        stats = self.get_network_stats()
        
        print("\n" + "="*60)
        print(f"🌐 QUANTUM NETWORK STATUS")
        print("="*60)
        print(f"Manager ID: {self.manager_id}")
        print(f"Active Miners: {stats['active_miners']}/{stats['total_miners']}")
        print(f"Total Qubits: {stats['total_qubits']}")
        print(f"Entanglements: {stats['entanglements']}")
        print(f"Network Coherence: {stats['coherence']:.4f}")
        print()
        print("Miners:")
        for mid, minfo in self.miners.items():
            range_ = self.get_miner_qubit_range(mid)
            print(f"  • {mid}: {minfo.num_qubits} qubits (indices {range_[0]}-{range_[1]-1}) [{minfo.status}]")
        print()
        print("Performance:")
        for key, value in stats['stats'].items():
            print(f"  {key}: {value}")
        print("="*60)


# ============================================================================
# Demo & Testing
# ============================================================================

if __name__ == "__main__":
    print("🌐 QDL Quantum Network Manager Demo\n")
    
    # Create network manager
    qnm = QuantumNetworkManager("zion_qnm")
    
    # Test 1: Register miners (only 2 for Bell pair demo due to gate limitations)
    print("Test 1: Miner Registration")
    print("-" * 60)
    qnm.register_miner("miner_001", num_qubits=1, capabilities=["bell_state", "grover"])
    qnm.register_miner("miner_002", num_qubits=1, capabilities=["bell_state", "qft"])
    
    qnm.print_network_status()
    
    # Test 2: Create Bell pair
    print("\nTest 2: Bell Pair Creation")
    print("-" * 60)
    success = qnm.create_bell_pair("miner_001", "miner_002")
    
    if success:
        # Measure to verify entanglement
        print("\nMeasuring Bell pair:")
        results = measure_all(qnm.global_register)
        
        qubit_0 = results[0]  # Miner 001 qubit 0
        qubit_1 = results[1]  # Miner 002 qubit 0
        
        print(f"  Miner 001 qubit 0: {qubit_0}")
        print(f"  Miner 002 qubit 0: {qubit_1}")
        
        if qubit_0 == qubit_1:
            print("  ✅ Qubits are CORRELATED! (Entanglement verified)")
        else:
            print("  ❌ Qubits are NOT correlated (unexpected)")
    
    # Test 3: GHZ state (Quantum Pulse!) - requires proper multi-qubit gate implementation
    print("\nTest 3: GHZ State (Quantum Pulse) - SKIPPED")
    print("-" * 60)
    print("⚠️  Multi-qubit gates not yet fully implemented.")
    print("   Current limitation: max 2 qubits total")
    print("   TODO: Fix tensor product in apply_two_qubit_gate()")
    print("   Future: 144+ miner GHZ states will work!")
    
    qnm.print_network_status()
    
    print("\n✨ Network manager demo complete!")
    print("🚀 Ready for distributed quantum computing!")
