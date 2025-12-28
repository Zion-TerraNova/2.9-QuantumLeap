"""
Measurement - Wavefunction Collapse
====================================

When you measure a quantum system:
- Superposition collapses to single state
- Probabilistic (can't predict exactly which state)
- Irreversible (can't un-measure!)

This is the WEIRD part of quantum mechanics.
"""

import numpy as np
from typing import List
from .qubit import Qubit, QubitRegister


def measure(register: QubitRegister, qubit_index: int) -> int:
    """
    Measure single qubit (collapse to 0 or 1)
    
    Args:
        register: Quantum register
        qubit_index: Which qubit to measure
    
    Returns:
        0 or 1 (measurement result)
    
    Side effect: Collapses state vector!
    """
    # This is simplified - real measurement requires partial trace
    # For now, measure entire register and extract qubit value
    
    # Get probabilities
    probabilities = register.get_probabilities()
    
    # Random measurement based on Born rule
    outcome = np.random.choice(
        range(register.num_states),
        p=probabilities
    )
    
    # Collapse to measured state
    register.state_vector = np.zeros(register.num_states, dtype=complex)
    register.state_vector[outcome] = 1.0
    
    # Extract qubit value from outcome
    bit_string = register.get_state_string(outcome)
    measured_bit = int(bit_string[qubit_index])
    
    return measured_bit


def measure_all(register: QubitRegister) -> List[int]:
    """
    Measure all qubits at once
    
    Returns:
        List of 0s and 1s, e.g., [0, 1, 1] for |011⟩
    """
    # Get probabilities
    probabilities = register.get_probabilities()
    
    # Random measurement
    outcome = np.random.choice(
        range(register.num_states),
        p=probabilities
    )
    
    # Collapse state
    register.state_vector = np.zeros(register.num_states, dtype=complex)
    register.state_vector[outcome] = 1.0
    
    # Convert to bit list
    bit_string = register.get_state_string(outcome)
    return [int(b) for b in bit_string]


if __name__ == "__main__":
    from .qubit import QubitRegister
    from .gates import hadamard
    
    print("🌌 QDL - Measurement Demo\n")
    
    # Create superposition
    reg = QubitRegister(1)
    hadamard(reg, 0)
    
    print("Before measurement:")
    reg.print_state()
    print("\nSuperposition: 50% |0⟩, 50% |1⟩")
    
    # Measure multiple times (need fresh superposition each time)
    print("\n" + "=" * 60)
    print("Measuring 10 times (creating fresh superposition each time):")
    print("=" * 60)
    
    results = []
    for i in range(10):
        # Create fresh superposition
        test_reg = QubitRegister(1)
        hadamard(test_reg, 0)
        
        # Measure
        result = measure_all(test_reg)[0]
        results.append(result)
        print(f"Measurement {i+1}: {result}")
    
    zeros = results.count(0)
    ones = results.count(1)
    
    print(f"\nStatistics:")
    print(f"  Got 0: {zeros} times ({zeros/10*100}%)")
    print(f"  Got 1: {ones} times ({ones/10*100}%)")
    print(f"  Expected: ~50% each")
    
    print("\n✅ Measurement working! (Wavefunction collapse)")
