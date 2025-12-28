"""
Quantum Miner Node
==================

Independent miner node that can:
1. Own local qubits
2. Connect to quantum network
3. Participate in distributed quantum operations
4. Measure local qubits and report results

This is the "edge device" in ZION's distributed quantum computing network.
Each ZION miner runs one of these nodes.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import uuid

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator.qubit import Qubit, QubitRegister
from simulator.gates import hadamard, pauli_x, apply_single_qubit_gate, HADAMARD
from simulator.measurement import measure
from distributed.protocol import (
    MessageType,
    QuantumMessage,
    build_connect_message,
    QuantumStateSerializer
)


@dataclass
class MinerStats:
    """Performance statistics for miner node."""
    qubits_owned: int = 0
    entanglements_participated: int = 0
    measurements_performed: int = 0
    quantum_pulses_joined: int = 0
    uptime_seconds: float = 0.0
    coherence_avg: float = 1.0


class QuantumMinerNode:
    """
    Independent quantum miner node.
    
    Each ZION miner runs this to participate in distributed quantum computing.
    
    Capabilities:
    - Own 1-10 local qubits
    - Join quantum network (connect to manager)
    - Participate in Bell pairs, GHZ states
    - Measure qubits and share results
    - Track consciousness level (PHYSICAL → ON_THE_STAR)
    """
    
    def __init__(
        self,
        miner_id: Optional[str] = None,
        num_qubits: int = 1,
        consciousness_level: str = "PHYSICAL"
    ):
        """
        Initialize miner node.
        
        Args:
            miner_id: Unique identifier (auto-generated if None)
            num_qubits: Number of local qubits owned by this miner
            consciousness_level: PHYSICAL, MENTAL, COSMIC, ON_THE_STAR
        """
        self.miner_id = miner_id or f"miner_{uuid.uuid4().hex[:8]}"
        self.num_qubits = num_qubits
        self.consciousness_level = consciousness_level
        
        # Local quantum register (owned by this miner)
        self.local_register = QubitRegister(num_qubits)
        
        # Network state
        self.connected = False
        self.network_manager_id: Optional[str] = None
        self.peer_miners: List[str] = []
        
        # Statistics
        self.stats = MinerStats(qubits_owned=num_qubits)
        self.start_time = time.time()
        
        # Consciousness multiplier (for rewards)
        self.consciousness_multipliers = {
            "PHYSICAL": 1.0,
            "MENTAL": 1.1,
            "COSMIC": 2.0,
            "ON_THE_STAR": 15.0
        }
    
    def get_consciousness_multiplier(self) -> float:
        """Get reward multiplier based on consciousness level."""
        return self.consciousness_multipliers.get(self.consciousness_level, 1.0)
    
    def connect_to_network(self, manager_id: str) -> QuantumMessage:
        """
        Connect to quantum network manager.
        
        Returns:
            CONNECT message to send to manager
        """
        self.network_manager_id = manager_id
        self.connected = True
        
        msg = build_connect_message(self.miner_id, self.num_qubits)
        print(f"📡 {self.miner_id} connecting to network...")
        
        return msg
    
    def prepare_superposition(self, qubit_index: int = 0):
        """
        Put local qubit into superposition (H gate).
        
        This is the first step in creating entanglement.
        """
        if qubit_index >= self.num_qubits:
            raise ValueError(f"Qubit {qubit_index} out of range (have {self.num_qubits})")
        
        hadamard(self.local_register, qubit_index)
        print(f"✨ {self.miner_id}: Qubit {qubit_index} in superposition")
    
    def apply_pauli_x(self, qubit_index: int = 0):
        """Apply X gate (bit flip) to local qubit."""
        if qubit_index >= self.num_qubits:
            raise ValueError(f"Qubit {qubit_index} out of range")
        
        pauli_x(self.local_register, qubit_index)
        print(f"🔄 {self.miner_id}: Applied X to qubit {qubit_index}")
    
    def measure_local_qubit(self, qubit_index: int = 0) -> int:
        """
        Measure local qubit.
        
        Returns:
            0 or 1 (measurement result)
        """
        if qubit_index >= self.num_qubits:
            raise ValueError(f"Qubit {qubit_index} out of range")
        
        result = measure(self.local_register, qubit_index)
        self.stats.measurements_performed += 1
        
        print(f"📊 {self.miner_id}: Measured qubit {qubit_index} → {result}")
        return result
    
    def get_local_state(self) -> List[complex]:
        """Get current quantum state of local register."""
        return list(self.local_register.state_vector)
    
    def sync_state_with_network(self) -> QuantumMessage:
        """
        Create SYNC_STATE message with local quantum state.
        
        Used when network manager needs to know this miner's state.
        """
        state = self.get_local_state()
        
        msg = QuantumMessage(
            msg_type=MessageType.SYNC_STATE,
            sender_id=self.miner_id,
            payload={
                'state_data': QuantumStateSerializer.serialize_state(state).hex(),
                'num_qubits': self.num_qubits,
                'consciousness_level': self.consciousness_level,
                'multiplier': self.get_consciousness_multiplier()
            }
        )
        
        return msg
    
    def update_stats(self):
        """Update runtime statistics."""
        self.stats.uptime_seconds = time.time() - self.start_time
    
    def print_status(self):
        """Print current miner status."""
        self.update_stats()
        
        print("\n" + "="*60)
        print(f"⚡ QUANTUM MINER NODE: {self.miner_id}")
        print("="*60)
        print(f"Qubits Owned: {self.stats.qubits_owned}")
        print(f"Consciousness Level: {self.consciousness_level}")
        print(f"Reward Multiplier: {self.get_consciousness_multiplier()}×")
        print(f"Network Connected: {'✅ Yes' if self.connected else '❌ No'}")
        if self.connected:
            print(f"Manager: {self.network_manager_id}")
            print(f"Peers: {len(self.peer_miners)}")
        print()
        print("Statistics:")
        print(f"  Entanglements: {self.stats.entanglements_participated}")
        print(f"  Measurements: {self.stats.measurements_performed}")
        print(f"  Quantum Pulses: {self.stats.quantum_pulses_joined}")
        print(f"  Uptime: {self.stats.uptime_seconds:.1f}s")
        print("="*60)
    
    def __repr__(self) -> str:
        return f"QuantumMinerNode(id={self.miner_id}, qubits={self.num_qubits}, level={self.consciousness_level})"


# ============================================================================
# Demo & Testing
# ============================================================================

if __name__ == "__main__":
    print("⚡ QDL Quantum Miner Node Demo\n")
    
    # Test 1: Create miners with different consciousness levels
    print("Test 1: Miner Creation")
    print("-" * 60)
    
    alice = QuantumMinerNode(
        miner_id="alice_777",
        num_qubits=1,
        consciousness_level="MENTAL"
    )
    
    bob = QuantumMinerNode(
        miner_id="bob_888",
        num_qubits=1,
        consciousness_level="COSMIC"
    )
    
    master = QuantumMinerNode(
        miner_id="master_999",
        num_qubits=1,
        consciousness_level="ON_THE_STAR"
    )
    
    print(f"✅ Created: {alice}")
    print(f"✅ Created: {bob}")
    print(f"✅ Created: {master}")
    print()
    
    # Test 2: Connect to network
    print("Test 2: Network Connection")
    print("-" * 60)
    
    alice_msg = alice.connect_to_network("qnm_master")
    bob_msg = bob.connect_to_network("qnm_master")
    
    print(f"✅ Alice connected: {alice_msg.msg_type.value}")
    print(f"✅ Bob connected: {bob_msg.msg_type.value}")
    print()
    
    # Test 3: Quantum operations
    print("Test 3: Local Quantum Operations")
    print("-" * 60)
    
    # Alice prepares superposition
    alice.prepare_superposition(0)
    
    # Bob flips his qubit
    bob.apply_pauli_x(0)
    
    # Both measure
    alice_result = alice.measure_local_qubit(0)
    bob_result = bob.measure_local_qubit(0)
    
    print()
    
    # Test 4: State synchronization
    print("Test 4: State Synchronization")
    print("-" * 60)
    
    alice_sync = alice.sync_state_with_network()
    print(f"📤 Alice synced state: {len(alice_sync.payload['state_data'])} hex chars")
    print(f"   Consciousness: {alice_sync.payload['consciousness_level']}")
    print(f"   Multiplier: {alice_sync.payload['multiplier']}×")
    print()
    
    # Test 5: Consciousness levels comparison
    print("Test 5: Consciousness Levels & Rewards")
    print("-" * 60)
    
    base_reward = 50.0  # ZION per block
    
    miners = [alice, bob, master]
    for miner in miners:
        multiplier = miner.get_consciousness_multiplier()
        total_reward = base_reward * multiplier
        print(f"{miner.miner_id:12} | {miner.consciousness_level:13} | {multiplier:4.1f}× | {total_reward:6.1f} ZION")
    
    print()
    
    # Test 6: Full status
    print("Test 6: Miner Status Reports")
    print("-" * 60)
    
    alice.stats.entanglements_participated = 5
    alice.stats.quantum_pulses_joined = 2
    alice.print_status()
    
    bob.stats.entanglements_participated = 3
    bob.stats.quantum_pulses_joined = 1
    bob.print_status()
    
    master.stats.entanglements_participated = 10
    master.stats.quantum_pulses_joined = 5
    master.print_status()
    
    print("\n✨ Miner node demo complete!")
    print("🚀 Ready for distributed quantum mining!")
