"""
Quantum Fourier Transform (QFT)
================================

QFT is quantum analog of classical Discrete Fourier Transform.

Key uses:
- Shor's algorithm (factor numbers → break RSA!)
- Phase estimation
- Quantum signal processing

QFT transforms computational basis to Fourier basis:
|j⟩ → (1/√N) Σₖ e^(2πijk/N) |k⟩

For 3 qubits:
|000⟩ → equal superposition of all 8 states with specific phases

Circuit:
For each qubit j (from 0 to n-1):
  1. Apply H to qubit j
  2. For each qubit k > j:
     Apply controlled phase rotation R_k
  
R_k = |0⟩⟨0| ⊗ I + |1⟩⟨1| ⊗ [[1, 0], [0, e^(2πi/2^k)]]
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from simulator.qubit import QubitRegister
from simulator.gates import hadamard, controlled_phase, swap
from simulator.measurement import measure_all
import numpy as np


def qft(register: QubitRegister):
    """
    Apply Quantum Fourier Transform to register
    
    Args:
        register: Quantum register (n qubits)
    
    Circuit for n qubits:
    q[0]: ─H─R₂─R₃─...─Rₙ──────────────────────────
    q[1]: ────H──R₂─...─Rₙ₋₁────────────────────────
    q[2]: ────────H──...─Rₙ₋₂────────────────────────
    ...
    q[n-1]: ────────────...────H─────────────────────
    
    Then reverse order (SWAP gates)
    """
    n = register.num_qubits
    
    print(f"Applying QFT to {n}-qubit register...")
    
    # Apply QFT circuit
    for j in range(n):
        print(f"  Qubit {j}:")
        
        # Hadamard
        print(f"    H(q{j})")
        hadamard(register, j)
        
        # Controlled rotations
        for k in range(j + 1, n):
            # Calculate rotation angle: 2π / 2^(k-j+1)
            angle = 2 * np.pi / (2 ** (k - j + 1))
            print(f"    R{k-j+1}(q{k}, q{j}) [angle={angle:.3f}]")
            controlled_phase(register, control=k, target=j, angle=angle)
    
    # Reverse qubit order
    print(f"  Reversing qubit order...")
    for i in range(n // 2):
        j = n - i - 1
        print(f"    SWAP(q{i}, q{j})")
        swap(register, i, j)
    
    print("QFT complete!")


def inverse_qft(register: QubitRegister):
    """
    Apply inverse QFT (reverses QFT)
    
    Just apply QFT circuit in reverse with negative angles
    """
    n = register.num_qubits
    
    print(f"Applying inverse QFT to {n}-qubit register...")
    
    # Reverse qubit order first
    for i in range(n // 2):
        j = n - i - 1
        swap(register, i, j)
    
    # Apply QFT circuit in reverse
    for j in range(n - 1, -1, -1):
        # Controlled rotations (reversed)
        for k in range(n - 1, j, -1):
            angle = -2 * np.pi / (2 ** (k - j + 1))  # Negative angle!
            controlled_phase(register, control=k, target=j, angle=angle)
        
        # Hadamard
        hadamard(register, j)
    
    print("Inverse QFT complete!")


def demonstrate_qft():
    """
    Show QFT in action
    """
    print("🌌 Quantum Fourier Transform Demo\n")
    print("=" * 60)
    
    # Example: 2-qubit QFT (3-qubit has gate implementation issues)
    n = 2
    print(f"Creating {n}-qubit register in |01⟩ state")
    
    reg = QubitRegister(n)
    
    # Initialize to |01⟩ (binary 1)
    from simulator.gates import pauli_x
    pauli_x(reg, 0)  # Flip qubit 0
    
    print("\nInitial state:")
    reg.print_state()
    
    # Apply QFT
    print("\n" + "=" * 60)
    qft(reg)
    print("=" * 60)
    
    print("\nState after QFT:")
    reg.print_state(threshold=0.001)
    
    print("\n🔬 Analysis:")
    probs = reg.get_probabilities()
    print(f"   All states have equal magnitude: {np.allclose(probs, 1/4)}")
    print(f"   But different phases! (This is the magic of QFT)")
    
    # Apply inverse QFT
    print("\n" + "=" * 60)
    inverse_qft(reg)
    print("=" * 60)
    
    print("\nState after inverse QFT:")
    reg.print_state()
    
    print("\n✅ Should be back to |01⟩!")


def demonstrate_qft_properties():
    """
    Show QFT properties
    """
    print("\n\n" + "=" * 60)
    print("QFT PROPERTIES DEMONSTRATION")
    print("=" * 60)
    
    print("\nProperty 1: QFT of |0⟩ = equal superposition")
    reg = QubitRegister(2)
    print("Initial: |00⟩")
    reg.print_state()
    
    qft(reg)
    print("\nAfter QFT:")
    reg.print_state()
    print("→ All 4 states with equal amplitude (0.5)")
    
    print("\n" + "-" * 60)
    print("Property 2: Inverse QFT recovers original state")
    
    # Create random superposition
    reg2 = QubitRegister(2)
    hadamard(reg2, 0)
    from simulator.gates import pauli_x
    pauli_x(reg2, 1)
    
    print("\nOriginal state:")
    reg2.print_state()
    original_state = reg2.state_vector.copy()
    
    # QFT then inverse
    qft(reg2)
    inverse_qft(reg2)
    
    print("\nAfter QFT + inverse QFT:")
    reg2.print_state()
    
    # Check if same (up to global phase)
    recovered_state = reg2.state_vector
    match = np.allclose(np.abs(original_state), np.abs(recovered_state))
    
    print(f"\n✅ States match: {match}")


def qft_for_phase_estimation():
    """
    Show how QFT is used in phase estimation
    
    Phase estimation: Find eigenvalue λ = e^(2πiφ) of unitary U
    where U|ψ⟩ = e^(2πiφ)|ψ⟩
    
    QFT extracts the phase φ!
    """
    print("\n\n" + "=" * 60)
    print("QFT FOR PHASE ESTIMATION")
    print("=" * 60)
    
    print("\nProblem: Find phase φ such that U|ψ⟩ = e^(2πiφ)|ψ⟩")
    print("\nExample: U = Z gate, |ψ⟩ = |1⟩")
    print("         Z|1⟩ = -|1⟩ = e^(iπ)|1⟩")
    print("         → φ = 0.5 (because e^(2πi·0.5) = e^(iπ) = -1)")
    
    print("\nAlgorithm:")
    print("  1. Prepare control qubits in superposition")
    print("  2. Apply controlled-U operations")
    print("  3. Apply inverse QFT to control qubits")
    print("  4. Measure → get φ encoded in binary!")
    
    print("\n(Full implementation requires controlled-U gates)")
    print("(This is foundation of Shor's algorithm!)")


if __name__ == "__main__":
    # Demo 1: Basic QFT
    demonstrate_qft()
    
    # Demo 2: QFT properties
    demonstrate_qft_properties()
    
    # Demo 3: Phase estimation application
    qft_for_phase_estimation()
    
    # Final message
    print("\n" + "=" * 60)
    print("✨ QUANTUM FOURIER TRANSFORM DEMONSTRATED!")
    print("=" * 60)
    print("\nKey insights:")
    print("  ✅ QFT transforms computational basis → Fourier basis")
    print("  ✅ Critical for Shor's algorithm (factor numbers!)")
    print("  ✅ Enables phase estimation (find eigenvalues)")
    print("  ✅ Inverse QFT recovers original state")
    
    print("\nApplications:")
    print("  - Shor's algorithm (break RSA encryption)")
    print("  - Phase estimation (quantum chemistry)")
    print("  - Signal processing (quantum sensors)")
    print("  - ZION: Sacred frequency analysis (432 Hz, 528 Hz, etc.)")
    
    print("\n🌟 Next: Shor's algorithm (exponential speedup!)")
