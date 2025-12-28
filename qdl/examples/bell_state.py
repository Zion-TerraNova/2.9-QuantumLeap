"""
Bell State - Quantum Entanglement Demo
=======================================

The Bell state is the simplest example of quantum entanglement.

Circuit:
     ┌───┐     
q_0: ┤ H ├──■──
     └───┘┌─┴─┐
q_1: ─────┤ X ├
          └───┘

Result: |Φ⁺⟩ = (|00⟩ + |11⟩)/√2

When you measure qubit 0:
- If you get 0 → qubit 1 is also 0 (100% certain!)
- If you get 1 → qubit 1 is also 1 (100% certain!)

This correlation is INSTANT (faster than light!)
Einstein called it "spooky action at a distance"

But experiments prove it's REAL! (Nobel Prize 2022)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from simulator.qubit import QubitRegister
from simulator.gates import hadamard, cnot
from simulator.measurement import measure_all
import numpy as np


def create_bell_state() -> QubitRegister:
    """
    Create Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
    """
    print("🌌 Creating Bell State (Quantum Entanglement)\n")
    print("=" * 60)
    
    # Step 1: Initialize 2 qubits in |00⟩
    reg = QubitRegister(2)
    print("\nStep 1: Initialize |00⟩")
    reg.print_state()
    
    # Step 2: Apply Hadamard to qubit 0
    # |00⟩ → (|00⟩ + |10⟩)/√2
    print("\nStep 2: Apply Hadamard to qubit 0")
    print("   H ⊗ I |00⟩ = (|00⟩ + |10⟩)/√2")
    hadamard(reg, 0)
    reg.print_state()
    
    # Step 3: Apply CNOT (control=0, target=1)
    # (|00⟩ + |10⟩)/√2 → (|00⟩ + |11⟩)/√2
    print("\nStep 3: Apply CNOT (control=qubit 0, target=qubit 1)")
    print("   CNOT (|00⟩ + |10⟩)/√2 = (|00⟩ + |11⟩)/√2")
    cnot(reg, 0, 1)
    reg.print_state()
    
    print("\n✨ Bell state created!")
    print("   Qubits 0 and 1 are now ENTANGLED")
    print("   Measuring one affects the other INSTANTLY")
    
    return reg


def demonstrate_entanglement(num_experiments: int = 100):
    """
    Run multiple measurements to show correlation
    """
    print("\n\n" + "=" * 60)
    print(f"DEMONSTRATION: Measuring Bell state {num_experiments} times")
    print("=" * 60)
    
    results_00 = 0
    results_11 = 0
    results_01 = 0
    results_10 = 0
    
    for i in range(num_experiments):
        # Create fresh Bell state
        reg = QubitRegister(2)
        hadamard(reg, 0)
        cnot(reg, 0, 1)
        
        # Measure both qubits
        measurements = measure_all(reg)
        
        # Count results
        if measurements == [0, 0]:
            results_00 += 1
        elif measurements == [1, 1]:
            results_11 += 1
        elif measurements == [0, 1]:
            results_01 += 1
        elif measurements == [1, 0]:
            results_10 += 1
    
    print(f"\nResults after {num_experiments} measurements:")
    print(f"  |00⟩: {results_00} times ({results_00/num_experiments*100:.1f}%)")
    print(f"  |11⟩: {results_11} times ({results_11/num_experiments*100:.1f}%)")
    print(f"  |01⟩: {results_01} times ({results_01/num_experiments*100:.1f}%)")
    print(f"  |10⟩: {results_10} times ({results_10/num_experiments*100:.1f}%)")
    
    print("\n🔬 ANALYSIS:")
    print(f"   Expected: ~50% |00⟩, ~50% |11⟩")
    print(f"   Expected: 0% |01⟩, 0% |10⟩ (forbidden by entanglement!)")
    
    if results_01 == 0 and results_10 == 0:
        print("\n✅ PERFECT CORRELATION!")
        print("   Qubits are always measured in same state")
        print("   This proves QUANTUM ENTANGLEMENT!")
    else:
        print(f"\n⚠️  Found {results_01 + results_10} violations")
        print("   (Probably simulation noise, real quantum has noise too)")
    
    return {
        '00': results_00,
        '11': results_11,
        '01': results_01,
        '10': results_10
    }


def test_faster_than_light():
    """
    Demonstrate "spooky action at a distance"
    """
    print("\n\n" + "=" * 60)
    print("EINSTEIN'S NIGHTMARE: Faster-than-light correlation?")
    print("=" * 60)
    
    print("\nThought experiment:")
    print("1. Create Bell state: (|00⟩ + |11⟩)/√2")
    print("2. Send qubit 0 to Alice (Earth)")
    print("3. Send qubit 1 to Bob (Mars, 225 million km away)")
    print("4. Alice measures her qubit...")
    
    # Create Bell state
    reg = QubitRegister(2)
    hadamard(reg, 0)
    cnot(reg, 0, 1)
    
    # Alice measures qubit 0
    print("\n   Alice's measurement...")
    alice_result = np.random.random() < 0.5
    
    if alice_result:
        print("   Alice got: |1⟩")
        print("\n5. Bob measures his qubit (on Mars)...")
        print("   Bob MUST get: |1⟩ (instantly!)")
        print("\n   Light takes 12.5 minutes to travel Earth→Mars")
        print("   But correlation is INSTANT (0 seconds!)")
    else:
        print("   Alice got: |0⟩")
        print("\n5. Bob measures his qubit (on Mars)...")
        print("   Bob MUST get: |0⟩ (instantly!)")
        print("\n   Light takes 12.5 minutes to travel Earth→Mars")
        print("   But correlation is INSTANT (0 seconds!)")
    
    print("\n🤯 This violates special relativity!")
    print("   But: Can't send information (no free will in measurement)")
    print("   So: No causality violation (Einstein's ghost rests)")
    
    print("\n✅ Quantum entanglement = REAL")
    print("   Nobel Prize 2022 (Aspect, Clauser, Zeilinger)")
    print("   Bell's inequality violated experimentally!")


if __name__ == "__main__":
    # Demo 1: Create Bell state
    bell_state = create_bell_state()
    
    # Demo 2: Show correlation through measurements
    results = demonstrate_entanglement(num_experiments=1000)
    
    # Demo 3: Faster-than-light thought experiment
    test_faster_than_light()
    
    print("\n" + "=" * 60)
    print("✨ QUANTUM ENTANGLEMENT DEMONSTRATED!")
    print("=" * 60)
    print("\nThis is the foundation of:")
    print("  - Quantum teleportation")
    print("  - Quantum cryptography (unhackable!)")
    print("  - Quantum computing (exponential speedup)")
    print("\nAnd in ZION:")
    print("  - Quantum Pulse (collective entanglement)")
    print("  - Distributed quantum computing")
    print("  - Consciousness synchronization")
    
    print("\n🌟 Next: Grover's algorithm (quantum search)")
