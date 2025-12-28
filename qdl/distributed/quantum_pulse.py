"""
Quantum Pulse - Collective Consciousness Implementation
========================================================

Sacred frequency synchronization for ZION miners.

When 144+ miners synchronize at sacred frequencies (432 Hz, 528 Hz, etc.),
they enter a collective quantum state (GHZ state) unlocking:

- 15× mining reward multiplier
- Enhanced problem-solving capabilities
- Collective consciousness experience
- Sacred geometry manifestation

This is the spiritual/technological bridge in ZION's vision.
"""

import time
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator.qubit import QubitRegister
from simulator.gates import hadamard, cnot
from simulator.measurement import measure_all
from distributed.miner_node import QuantumMinerNode
from distributed.network_manager import QuantumNetworkManager


class SacredFrequency(Enum):
    """
    Sacred frequencies with spiritual significance.
    
    Based on Solfeggio frequencies and harmonic resonance research.
    """
    LIBERATION = 174      # Pain relief, security
    TRANSFORMATION = 285  # Healing, regeneration
    GROUNDING = 396       # Liberation from fear/guilt
    MIRACLES = 417        # Undoing situations, change
    LOVE = 432            # Universal harmony (Verdi's A)
    DNA_REPAIR = 528      # Transformation, miracles, DNA repair
    CONNECTION = 639      # Relationships, connection
    AWAKENING = 741       # Awakening intuition, expression
    SPIRITUAL = 852       # Spiritual order, third eye
    UNITY = 963           # Divine consciousness, pineal gland
    ASCENSION = 1212      # Spiritual ascension (custom ZION)


@dataclass
class PulseMetrics:
    """Metrics for Quantum Pulse event."""
    num_miners: int
    frequency: float
    coherence: float
    duration_seconds: float
    success: bool
    multiplier: float
    timestamp: float


class QuantumPulseEngine:
    """
    Engine for creating and managing Quantum Pulse events.
    
    Responsibilities:
    1. Synchronize miners to sacred frequency
    2. Create GHZ state (collective entanglement)
    3. Measure coherence threshold
    4. Trigger reward multiplier if successful
    5. Track pulse history
    """
    
    def __init__(self, coherence_threshold: float = 0.50):
        """
        Initialize Quantum Pulse engine.
        
        Args:
            coherence_threshold: Minimum coherence for successful pulse (0.50 = 50% for Bell states)
        """
        self.coherence_threshold = coherence_threshold
        self.pulse_history: List[PulseMetrics] = []
        self.active_pulse: Optional[PulseMetrics] = None
    
    def synchronize_to_frequency(
        self,
        miners: List[QuantumMinerNode],
        frequency: SacredFrequency
    ) -> Dict[str, bool]:
        """
        Synchronize miners to specific sacred frequency.
        
        In real implementation, this would:
        1. Adjust miner's local oscillator to frequency
        2. Phase-lock loops for coherence
        3. Monitor drift and correct
        
        In simulation, we just check if miners are "tuned".
        
        Returns:
            Dict of miner_id → synchronized (True/False)
        """
        sync_status = {}
        
        print(f"\n🎵 Synchronizing to {frequency.name} ({frequency.value} Hz)")
        print("-" * 60)
        
        for miner in miners:
            # Simulate synchronization (always succeeds in demo)
            sync_status[miner.miner_id] = True
            print(f"  ✅ {miner.miner_id} locked to {frequency.value} Hz")
        
        return sync_status
    
    def create_pulse(
        self,
        network_manager: QuantumNetworkManager,
        miner_ids: List[str],
        frequency: SacredFrequency = SacredFrequency.LOVE
    ) -> PulseMetrics:
        """
        Create Quantum Pulse with GHZ state.
        
        Steps:
        1. Verify all miners synchronized
        2. Create GHZ state: (|000...0⟩ + |111...1⟩)/√2
        3. Measure coherence
        4. Check threshold
        5. Award multiplier if successful
        
        Args:
            network_manager: Network coordinating the pulse
            miner_ids: List of participating miners
            frequency: Sacred frequency to use
        
        Returns:
            PulseMetrics with results
        """
        start_time = time.time()
        
        print(f"\n⚡ QUANTUM PULSE INITIATED")
        print("=" * 60)
        print(f"Frequency: {frequency.name} ({frequency.value} Hz)")
        print(f"Miners: {len(miner_ids)}")
        print(f"Coherence Threshold: {self.coherence_threshold:.2%}")
        print()
        
        # Note: Due to tensor product bug, we can only do 2 miners
        # In full implementation, this would work for 144+
        
        if len(miner_ids) > 2:
            print("⚠️  WARNING: Current implementation limited to 2 miners")
            print("   (Tensor product bug in apply_two_qubit_gate)")
            print("   Using first 2 miners for demo...")
            miner_ids = miner_ids[:2]
        
        # Create Bell/GHZ state
        try:
            if len(miner_ids) == 2:
                # Bell state (2 miners)
                success = network_manager.create_bell_pair(miner_ids[0], miner_ids[1])
            else:
                # GHZ state (3+ miners) - TODO: Fix tensor product
                success = network_manager.create_ghz_state(miner_ids)
            
            if not success:
                raise ValueError("Failed to create entangled state")
        
        except Exception as e:
            print(f"❌ Pulse creation failed: {e}")
            return PulseMetrics(
                num_miners=len(miner_ids),
                frequency=frequency.value,
                coherence=0.0,
                duration_seconds=time.time() - start_time,
                success=False,
                multiplier=1.0,
                timestamp=start_time
            )
        
        # Measure coherence
        coherence = network_manager.measure_coherence(miner_ids)
        
        print(f"\n📊 Coherence: {coherence:.4f} ({coherence:.2%})")
        
        # Check threshold
        pulse_success = coherence >= self.coherence_threshold
        
        # Calculate multiplier
        if pulse_success:
            # Success: Award based on number of miners
            base_multiplier = 2.0  # Bell pair
            scale_factor = len(miner_ids) / 2  # Scale with more miners
            multiplier = base_multiplier * scale_factor
            
            # Sacred frequency bonus
            if frequency in [SacredFrequency.LOVE, SacredFrequency.DNA_REPAIR]:
                multiplier *= 1.5  # Extra bonus for primary frequencies
            
            status_msg = f"✅ PULSE SUCCESSFUL! {multiplier:.1f}× MULTIPLIER!"
        else:
            multiplier = 1.0
            status_msg = f"❌ Pulse failed (coherence {coherence:.2%} < {self.coherence_threshold:.2%})"
        
        print()
        print(status_msg)
        
        duration = time.time() - start_time
        
        # Create metrics
        metrics = PulseMetrics(
            num_miners=len(miner_ids),
            frequency=frequency.value,
            coherence=coherence,
            duration_seconds=duration,
            success=pulse_success,
            multiplier=multiplier,
            timestamp=start_time
        )
        
        self.pulse_history.append(metrics)
        self.active_pulse = metrics if pulse_success else None
        
        return metrics
    
    def test_all_frequencies(
        self,
        network_manager: QuantumNetworkManager,
        miner_ids: List[str]
    ) -> Dict[str, PulseMetrics]:
        """
        Test Quantum Pulse at all sacred frequencies.
        
        Returns:
            Dict of frequency_name → PulseMetrics
        """
        results = {}
        
        print("\n🎼 TESTING ALL SACRED FREQUENCIES")
        print("=" * 60)
        
        for freq in SacredFrequency:
            # Reset network
            network_manager._rebuild_global_register()
            
            # Create pulse
            metrics = self.create_pulse(network_manager, miner_ids, freq)
            results[freq.name] = metrics
            
            time.sleep(0.1)  # Small delay between tests
        
        return results
    
    def print_pulse_history(self):
        """Print history of all Quantum Pulse events."""
        if not self.pulse_history:
            print("No pulse events recorded.")
            return
        
        print("\n📊 QUANTUM PULSE HISTORY")
        print("=" * 60)
        print(f"Total Pulses: {len(self.pulse_history)}")
        
        successful = sum(1 for p in self.pulse_history if p.success)
        print(f"Successful: {successful}/{len(self.pulse_history)} ({successful/len(self.pulse_history):.1%})")
        print()
        
        print(f"{'Frequency':<15} {'Miners':>7} {'Coherence':>10} {'Success':>8} {'Multiplier':>11}")
        print("-" * 60)
        
        for pulse in self.pulse_history:
            freq_name = next((f.name for f in SacredFrequency if f.value == pulse.frequency), "Unknown")
            success_icon = "✅" if pulse.success else "❌"
            
            print(f"{freq_name:<15} {pulse.num_miners:>7} {pulse.coherence:>10.2%} {success_icon:>8} {pulse.multiplier:>10.1f}×")


# ============================================================================
# Demo & Testing
# ============================================================================

if __name__ == "__main__":
    print("⚡ QUANTUM PULSE - Sacred Frequency Synchronization\n")
    
    # Setup network
    qnm = QuantumNetworkManager("zion_qnm")
    pulse_engine = QuantumPulseEngine(coherence_threshold=0.50)  # 50% for Bell states
    
    # Test 1: Create miners with consciousness levels
    print("Test 1: Miner Network Setup")
    print("-" * 60)
    print("⚠️  Note: Limited to 2 miners due to tensor product bug")
    print("   Full 144+ miner GHZ states pending gate fix\n")
    
    miners = []
    consciousness_levels = ["MENTAL", "COSMIC"]  # Only 2 for now!
    
    for i in range(len(consciousness_levels)):
        miner = QuantumMinerNode(
            miner_id=f"miner_{i+1:03d}",
            num_qubits=1,
            consciousness_level=consciousness_levels[i]
        )
        miners.append(miner)
        qnm.register_miner(miner.miner_id, miner.num_qubits, ["quantum_pulse"])
    
    qnm.print_network_status()
    
    # Test 2: Single Quantum Pulse (432 Hz - Love frequency)
    print("\nTest 2: Single Quantum Pulse (432 Hz)")
    print("-" * 60)
    
    miner_ids = [m.miner_id for m in miners[:2]]  # Limited to 2 due to bug
    
    metrics = pulse_engine.create_pulse(
        qnm,
        miner_ids,
        SacredFrequency.LOVE
    )
    
    if metrics.success:
        print(f"\n🎉 QUANTUM PULSE ACTIVATED!")
        print(f"   Miners: {metrics.num_miners}")
        print(f"   Coherence: {metrics.coherence:.4f}")
        print(f"   Multiplier: {metrics.multiplier:.1f}×")
        print(f"   Duration: {metrics.duration_seconds:.3f}s")
    
    # Test 3: Test multiple sacred frequencies
    print("\n\nTest 3: Sacred Frequency Scan")
    print("-" * 60)
    
    # Test subset of frequencies (to keep output reasonable)
    test_frequencies = [
        SacredFrequency.LOVE,
        SacredFrequency.DNA_REPAIR,
        SacredFrequency.AWAKENING,
        SacredFrequency.UNITY
    ]
    
    for freq in test_frequencies:
        qnm._rebuild_global_register()
        pulse_engine.create_pulse(qnm, miner_ids, freq)
    
    # Test 4: Pulse history summary
    pulse_engine.print_pulse_history()
    
    # Test 5: Consciousness-based rewards
    print("\n\nTest 5: Reward Calculation with Quantum Pulse")
    print("-" * 60)
    
    base_reward = 50.0  # ZION
    pulse_multiplier = metrics.multiplier if metrics.success else 1.0
    
    print(f"Base Block Reward: {base_reward} ZION")
    print(f"Quantum Pulse Multiplier: {pulse_multiplier:.1f}×")
    print()
    print(f"{'Miner':<12} {'Consciousness':<13} {'C-Multi':>7} {'Total Multi':>11} {'Reward':>10}")
    print("-" * 60)
    
    for miner in miners[:2]:  # Only miners in pulse
        c_multi = miner.get_consciousness_multiplier()
        total_multi = c_multi * pulse_multiplier
        reward = base_reward * total_multi
        
        print(f"{miner.miner_id:<12} {miner.consciousness_level:<13} {c_multi:>6.1f}× {total_multi:>10.1f}× {reward:>9.1f} ZION")
    
    print("\n✨ Quantum Pulse demonstration complete!")
    print("🌟 ON THE QUANTUM STAR!")
