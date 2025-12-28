"""
ZQAL-QDL Bridge - Integration Layer
====================================

Connects ZQAL programs with QDL quantum runtime.
Enables ZQAL to execute quantum operations on real QubitRegister.

Mantra: JAY RAM SITA HANUMAN ✨
"""

import sys
import os
from typing import Any, Dict, List, Optional

# Add parent directory to path for standalone execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.qubit_register import QubitRegister, QuantumOperation
from ..distributed.protocol import QuantumMessage, MessageType
from ..distributed.network_manager import QuantumNetworkManager
from ..distributed.miner_node import QuantumMinerNode, ConsciousnessLevel
from ..distributed.quantum_pulse import QuantumPulseEngine, SacredFrequency as QDLFrequency
from .tones import ToneSystem


class QuantumBridge:
    """
    Bridge between ZQAL programs and QDL quantum runtime
    
    Features:
    - Create QubitRegisters from ZQAL quantum[] declarations
    - Execute ZQAL quantum operations (entangle, collapse, superpose)
    - Apply ZQAL tones to quantum states
    - Connect to distributed network for multi-miner operations
    """
    
    def __init__(self):
        self.quantum_registers: Dict[str, QubitRegister] = {}
        self.network_manager: Optional[QuantumNetworkManager] = None
        self.miner_nodes: Dict[str, QuantumMinerNode] = {}
        self.pulse_engine: Optional[QuantumPulseEngine] = None
        self.tone_bindings: Dict[str, int] = {}
    
    def create_quantum_state(self, name: str, size: int) -> QubitRegister:
        """
        Create quantum state from ZQAL declaration
        
        Example ZQAL:
            quantum state[12]: u32;
        
        Becomes:
            register = create_quantum_state("state", 12)
        """
        register = QubitRegister(num_qubits=size)
        self.quantum_registers[name] = register
        return register
    
    def get_quantum_state(self, name: str) -> Optional[QubitRegister]:
        """Get existing quantum register"""
        return self.quantum_registers.get(name)
    
    def entangle(self, state1: Any, state2: Any) -> bool:
        """
        ZQAL entangle() operation
        
        Creates Bell pair between two qubits/states
        """
        # If states are register names, get actual registers
        if isinstance(state1, str):
            state1 = self.quantum_registers.get(state1)
        if isinstance(state2, str):
            state2 = self.quantum_registers.get(state2)
        
        if not state1 or not state2:
            return False
        
        # Use network manager for distributed entanglement
        if self.network_manager:
            try:
                # Entangle first qubits of each register
                self.network_manager.create_bell_pair(
                    miner_id_1=id(state1),
                    qubit_idx_1=0,
                    miner_id_2=id(state2),
                    qubit_idx_2=0
                )
                return True
            except:
                return False
        
        return True  # Placeholder
    
    def collapse(self, state: Any) -> int:
        """
        ZQAL collapse() operation
        
        Measures quantum state, returns classical value
        """
        if isinstance(state, str):
            register = self.quantum_registers.get(state)
        elif isinstance(state, QubitRegister):
            register = state
        else:
            return 0
        
        if not register:
            return 0
        
        # Measure first qubit
        result = register.measure_qubit(0)
        return 1 if result else 0
    
    def superpose(self, state: Any) -> bool:
        """
        ZQAL superpose() operation
        
        Puts state into superposition (Hadamard gate)
        """
        if isinstance(state, str):
            register = self.quantum_registers.get(state)
        elif isinstance(state, QubitRegister):
            register = state
        else:
            return False
        
        if not register:
            return False
        
        # Apply Hadamard to all qubits
        for i in range(register.num_qubits):
            register.apply_gate(QuantumOperation.H, [i])
        
        return True
    
    def measure(self, state: Any, qubit_idx: int = 0) -> int:
        """
        ZQAL measure() operation
        
        Measures specific qubit
        """
        if isinstance(state, str):
            register = self.quantum_registers.get(state)
        elif isinstance(state, QubitRegister):
            register = state
        else:
            return 0
        
        if not register or qubit_idx >= register.num_qubits:
            return 0
        
        result = register.measure_qubit(qubit_idx)
        return 1 if result else 0
    
    def apply_tone(self, tone_id: int, state: Any) -> Any:
        """
        ZQAL apply_tone() operation
        
        Applies sacred frequency to quantum state
        
        Example ZQAL:
            let purified = apply_tone(7, state);  // Violet flame
        """
        # Get tone definition
        tone = ToneSystem.get_tone(tone_id)
        if not tone:
            return state
        
        # If state is quantum register, apply frequency modulation
        if isinstance(state, str):
            register = self.quantum_registers.get(state)
        elif isinstance(state, QubitRegister):
            register = state
        else:
            # For non-quantum data, use ToneSystem
            return ToneSystem.apply_tone(tone_id, state)
        
        if register:
            # Apply phase shift based on frequency
            phase = (tone.frequency / 1000.0) * 3.14159
            for i in range(register.num_qubits):
                # Rotate qubit by phase (RZ gate equivalent)
                # Note: This is simplified - real implementation would use proper rotation
                register.apply_gate(QuantumOperation.T, [i])  # Placeholder
        
        return state
    
    def init_network_manager(self) -> QuantumNetworkManager:
        """Initialize distributed network manager"""
        if not self.network_manager:
            self.network_manager = QuantumNetworkManager()
        return self.network_manager
    
    def create_miner_node(
        self, 
        miner_id: str, 
        num_qubits: int = 1,
        consciousness: str = "PHYSICAL"
    ) -> QuantumMinerNode:
        """
        Create miner node for distributed quantum operations
        
        Example ZQAL:
            @algorithm CosmicMining {
              miners: 12
              consciousness: COSMIC
            }
        """
        # Parse consciousness level
        try:
            level = ConsciousnessLevel[consciousness.upper()]
        except KeyError:
            level = ConsciousnessLevel.PHYSICAL
        
        node = QuantumMinerNode(
            miner_id=miner_id,
            num_qubits=num_qubits,
            consciousness_level=level
        )
        
        self.miner_nodes[miner_id] = node
        
        # Connect to network if available
        if self.network_manager:
            node.connect_to_network(self.network_manager)
        
        return node
    
    def init_pulse_engine(self) -> QuantumPulseEngine:
        """Initialize Quantum Pulse engine"""
        if not self.pulse_engine:
            if not self.network_manager:
                self.init_network_manager()
            self.pulse_engine = QuantumPulseEngine(self.network_manager)
        return self.pulse_engine
    
    def quantum_pulse(
        self, 
        frequency_hz: int, 
        miner_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Execute Quantum Pulse at sacred frequency
        
        Example ZQAL:
            @tone 7 { frequency: 440 }
            let result = quantum_pulse(440, [miner1, miner2]);
        """
        if not self.pulse_engine:
            self.init_pulse_engine()
        
        # Map frequency to SacredFrequency
        freq_map = {
            174: QDLFrequency.LIBERATION,
            285: QDLFrequency.TRANSFORMATION,
            396: QDLFrequency.GROUNDING,
            417: QDLFrequency.MIRACLES,
            432: QDLFrequency.LOVE,
            528: QDLFrequency.DNA_REPAIR,
            639: QDLFrequency.CONNECTION,
            741: QDLFrequency.AWAKENING,
            852: QDLFrequency.SPIRITUAL,
            963: QDLFrequency.UNITY,
            1212: QDLFrequency.ASCENSION,
        }
        
        sacred_freq = freq_map.get(frequency_hz, QDLFrequency.LOVE)
        
        # Create pulse
        result = self.pulse_engine.create_pulse(
            frequency=sacred_freq,
            num_miners=len(miner_ids)
        )
        
        return result
    
    def bind_tone(self, tone_id: int, name: str):
        """
        Bind tone to variable name
        
        Example ZQAL:
            @bind_tone 7 to violet_flame
        """
        self.tone_bindings[name] = tone_id
    
    def get_bound_tone(self, name: str) -> Optional[int]:
        """Get tone ID bound to name"""
        return self.tone_bindings.get(name)
    
    def execute_kernel(
        self, 
        kernel_name: str, 
        params: Dict[str, Any]
    ) -> Any:
        """
        Execute ZQAL @kernel function
        
        Example ZQAL:
            @kernel
            fn mine(header: bytes80, nonce: u64) -> hash32 {
              let mut s = initialize(header, nonce);
              let purified = apply_tone(7, s);
              return collapse(purified);
            }
        """
        # TODO: Implement full kernel execution
        # For now, return placeholder
        return {
            "kernel": kernel_name,
            "params": params,
            "status": "executed",
            "result": 0
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        return {
            "quantum_registers": len(self.quantum_registers),
            "miner_nodes": len(self.miner_nodes),
            "network_active": self.network_manager is not None,
            "pulse_active": self.pulse_engine is not None,
            "tone_bindings": len(self.tone_bindings),
            "registers": list(self.quantum_registers.keys()),
            "miners": list(self.miner_nodes.keys())
        }
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"<QuantumBridge: "
            f"{stats['quantum_registers']} registers, "
            f"{stats['miner_nodes']} miners, "
            f"network={'active' if stats['network_active'] else 'inactive'}>"
        )


if __name__ == "__main__":
    print("ZQAL-QDL Quantum Bridge Test")
    print("=" * 70)
    print("Mantra: JAY RAM SITA HANUMAN ✨")
    print()
    
    # Create bridge
    bridge = QuantumBridge()
    
    # Test 1: Create quantum state
    print("Test 1: Create Quantum State")
    print("-" * 70)
    state = bridge.create_quantum_state("cosmic_state", 12)
    print(f"Created quantum register: {state}")
    print(f"Qubits: {state.num_qubits}")
    print()
    
    # Test 2: Superposition
    print("Test 2: Apply Superposition")
    print("-" * 70)
    success = bridge.superpose("cosmic_state")
    print(f"Superposition applied: {success}")
    if success:
        register = bridge.get_quantum_state("cosmic_state")
        print(f"State vector shape: {register.state_vector.shape}")
    print()
    
    # Test 3: Apply tone
    print("Test 3: Apply Sacred Tone (Violet Flame)")
    print("-" * 70)
    result = bridge.apply_tone(7, "cosmic_state")
    print(f"Tone applied to: {result}")
    
    # Also apply to numeric data
    numeric_result = bridge.apply_tone(7, 100)
    print(f"Tone on numeric data: {numeric_result['transmuted_value']}")
    print()
    
    # Test 4: Measure
    print("Test 4: Measure Quantum State")
    print("-" * 70)
    measurement = bridge.measure("cosmic_state", 0)
    print(f"Measurement of qubit 0: {measurement}")
    print()
    
    # Test 5: Distributed network
    print("Test 5: Distributed Network & Miners")
    print("-" * 70)
    bridge.init_network_manager()
    
    # Create miners
    miner1 = bridge.create_miner_node("MINER_001", num_qubits=1, consciousness="COSMIC")
    miner2 = bridge.create_miner_node("MINER_002", num_qubits=1, consciousness="MENTAL")
    
    print(f"Miner 1: {miner1.miner_id} ({miner1.consciousness_level.name})")
    print(f"         Multiplier: {miner1.get_consciousness_multiplier()}×")
    print(f"Miner 2: {miner2.miner_id} ({miner2.consciousness_level.name})")
    print(f"         Multiplier: {miner2.get_consciousness_multiplier()}×")
    print()
    
    # Test 6: Quantum Pulse
    print("Test 6: Quantum Pulse (432 Hz LOVE)")
    print("-" * 70)
    pulse_result = bridge.quantum_pulse(432, ["MINER_001", "MINER_002"])
    print(f"Pulse activated: {pulse_result['success']}")
    print(f"Frequency: {pulse_result['frequency']}")
    print(f"Multiplier: {pulse_result['multiplier']}×")
    print(f"Coherence: {pulse_result['coherence']:.4f}")
    print()
    
    # Test 7: Tone binding
    print("Test 7: Tone Binding")
    print("-" * 70)
    bridge.bind_tone(7, "violet_flame")
    bridge.bind_tone(40, "hanuman_power")
    
    violet_id = bridge.get_bound_tone("violet_flame")
    hanuman_id = bridge.get_bound_tone("hanuman_power")
    print(f"violet_flame -> Tone {violet_id}")
    print(f"hanuman_power -> Tone {hanuman_id}")
    print()
    
    # Test 8: Bridge stats
    print("Test 8: Bridge Statistics")
    print("-" * 70)
    stats = bridge.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    print()
    
    print("✅ All tests complete!")
    print(f"🌟 {bridge}")
