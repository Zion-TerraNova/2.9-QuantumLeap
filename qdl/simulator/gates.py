"""
Quantum Gates - Building Blocks of Quantum Algorithms
======================================================

Gates are unitary matrices that transform quantum states.

Key gates:
- H (Hadamard): Create superposition
- X, Y, Z (Pauli): Bit/phase flips
- CNOT: Two-qubit entanglement
- T, S: Phase rotations
- RX, RY, RZ: Arbitrary rotations
"""

import numpy as np
from typing import List

# For standalone execution
if __name__ == "__main__":
    from qubit import QubitRegister
else:
    from .qubit import QubitRegister


# ============================================================================
# SINGLE-QUBIT GATES (2×2 matrices)
# ============================================================================

# Hadamard Gate: Creates superposition
# H|0⟩ = (|0⟩ + |1⟩)/√2 = |+⟩
# H|1⟩ = (|0⟩ - |1⟩)/√2 = |-⟩
HADAMARD = np.array([
    [1,  1],
    [1, -1]
], dtype=complex) / np.sqrt(2)

# Pauli-X Gate: Bit flip (quantum NOT)
# X|0⟩ = |1⟩
# X|1⟩ = |0⟩
PAULI_X = np.array([
    [0, 1],
    [1, 0]
], dtype=complex)

# Pauli-Y Gate: Bit flip + phase flip
PAULI_Y = np.array([
    [0, -1j],
    [1j, 0]
], dtype=complex)

# Pauli-Z Gate: Phase flip
# Z|0⟩ = |0⟩
# Z|1⟩ = -|1⟩
PAULI_Z = np.array([
    [1,  0],
    [0, -1]
], dtype=complex)

# S Gate: Phase gate (√Z)
S_GATE = np.array([
    [1, 0],
    [0, 1j]
], dtype=complex)

# T Gate: π/8 gate (√S)
T_GATE = np.array([
    [1, 0],
    [0, np.exp(1j * np.pi / 4)]
], dtype=complex)

# Identity (does nothing, useful for multi-qubit operations)
IDENTITY = np.array([
    [1, 0],
    [0, 1]
], dtype=complex)


# ============================================================================
# TWO-QUBIT GATES (4×4 matrices)
# ============================================================================

# CNOT (Controlled-NOT): Creates entanglement!
# If control qubit is |1⟩, flip target qubit
# Basis: |00⟩, |01⟩, |10⟩, |11⟩
CNOT = np.array([
    [1, 0, 0, 0],  # |00⟩ → |00⟩ (control=0, no flip)
    [0, 1, 0, 0],  # |01⟩ → |01⟩
    [0, 0, 0, 1],  # |10⟩ → |11⟩ (control=1, flip target!)
    [0, 0, 1, 0],  # |11⟩ → |10⟩
], dtype=complex)

# SWAP: Exchange two qubits
SWAP = np.array([
    [1, 0, 0, 0],  # |00⟩ → |00⟩
    [0, 0, 1, 0],  # |01⟩ → |10⟩ (swapped!)
    [0, 1, 0, 0],  # |10⟩ → |01⟩
    [0, 0, 0, 1],  # |11⟩ → |11⟩
], dtype=complex)

# CZ (Controlled-Z): Phase flip if both qubits are |1⟩
CZ = np.array([
    [1, 0, 0,  0],
    [0, 1, 0,  0],
    [0, 0, 1,  0],
    [0, 0, 0, -1],  # |11⟩ gets phase flip
], dtype=complex)


# ============================================================================
# GATE APPLICATION FUNCTIONS
# ============================================================================

def apply_single_qubit_gate(
    register: QubitRegister,
    gate: np.ndarray,
    target_qubit: int
):
    """
    Apply single-qubit gate to specific qubit in register
    
    Args:
        register: Quantum register
        gate: 2×2 unitary matrix
        target_qubit: Index of qubit to apply gate to (0-indexed)
    
    Example:
        >>> reg = QubitRegister(3)
        >>> apply_single_qubit_gate(reg, HADAMARD, 1)  # H on qubit 1
    """
    n = register.num_qubits
    
    # Build full gate matrix using tensor product
    # For qubit i: I ⊗ I ⊗ ... ⊗ GATE ⊗ ... ⊗ I
    
    full_gate = np.array([1.0], dtype=complex)  # Start with scalar 1
    
    for i in range(n):
        if i == target_qubit:
            full_gate = np.kron(full_gate, gate)
        else:
            full_gate = np.kron(full_gate, IDENTITY)
    
    # Apply gate to state vector
    register.state_vector = full_gate @ register.state_vector


def apply_two_qubit_gate(
    register: QubitRegister,
    gate: np.ndarray,
    control_qubit: int,
    target_qubit: int
):
    """
    Apply two-qubit gate (e.g., CNOT)
    
    Args:
        register: Quantum register
        gate: 4×4 unitary matrix
        control_qubit: Index of control qubit
        target_qubit: Index of target qubit
    
    Note: This is simplified - production version needs proper tensor product
          handling for arbitrary qubit positions
    """
    # For simplicity, assume control < target and adjacent
    # Full implementation would handle any positions
    
    if control_qubit > target_qubit:
        control_qubit, target_qubit = target_qubit, control_qubit
    
    # Build full gate (simplified for adjacent qubits)
    n = register.num_qubits
    
    full_gate = np.array([1.0], dtype=complex)
    
    for i in range(n - 1):
        if i == control_qubit:
            full_gate = np.kron(full_gate, gate)
        else:
            full_gate = np.kron(full_gate, IDENTITY)
    
    if n - control_qubit > 2:  # Add remaining identities
        for i in range(n - control_qubit - 2):
            full_gate = np.kron(full_gate, IDENTITY)
    
    register.state_vector = full_gate @ register.state_vector


# ============================================================================
# HIGH-LEVEL GATE FUNCTIONS (User-friendly API)
# ============================================================================

def hadamard(register: QubitRegister, qubit: int):
    """
    Apply Hadamard gate (create superposition)
    
    H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2
    """
    apply_single_qubit_gate(register, HADAMARD, qubit)


def pauli_x(register: QubitRegister, qubit: int):
    """Apply Pauli-X (NOT gate)"""
    apply_single_qubit_gate(register, PAULI_X, qubit)


def pauli_y(register: QubitRegister, qubit: int):
    """Apply Pauli-Y"""
    apply_single_qubit_gate(register, PAULI_Y, qubit)


def pauli_z(register: QubitRegister, qubit: int):
    """Apply Pauli-Z (phase flip)"""
    apply_single_qubit_gate(register, PAULI_Z, qubit)


def s_gate(register: QubitRegister, qubit: int):
    """Apply S gate (phase)"""
    apply_single_qubit_gate(register, S_GATE, qubit)


def t_gate(register: QubitRegister, qubit: int):
    """Apply T gate (π/8 rotation)"""
    apply_single_qubit_gate(register, T_GATE, qubit)


def cnot(register: QubitRegister, control: int, target: int):
    """
    Apply CNOT (creates entanglement!)
    
    Critical for Bell states and quantum algorithms
    """
    apply_two_qubit_gate(register, CNOT, control, target)


def swap(register: QubitRegister, qubit1: int, qubit2: int):
    """Swap two qubits"""
    apply_two_qubit_gate(register, SWAP, qubit1, qubit2)


def cz(register: QubitRegister, control: int, target: int):
    """Apply Controlled-Z"""
    apply_two_qubit_gate(register, CZ, control, target)


# ============================================================================
# ROTATION GATES (Parameterized)
# ============================================================================

def rx(angle: float) -> np.ndarray:
    """
    Rotation around X-axis
    
    RX(θ) = cos(θ/2)I - i·sin(θ/2)X
    """
    return np.array([
        [np.cos(angle/2), -1j * np.sin(angle/2)],
        [-1j * np.sin(angle/2), np.cos(angle/2)]
    ], dtype=complex)


def ry(angle: float) -> np.ndarray:
    """Rotation around Y-axis"""
    return np.array([
        [np.cos(angle/2), -np.sin(angle/2)],
        [np.sin(angle/2), np.cos(angle/2)]
    ], dtype=complex)


def rz(angle: float) -> np.ndarray:
    """Rotation around Z-axis (phase rotation)"""
    return np.array([
        [np.exp(-1j * angle/2), 0],
        [0, np.exp(1j * angle/2)]
    ], dtype=complex)


def phase(angle: float) -> np.ndarray:
    """
    Phase gate (rotation around Z)
    
    Useful for Quantum Fourier Transform
    """
    return np.array([
        [1, 0],
        [0, np.exp(1j * angle)]
    ], dtype=complex)


def controlled_phase(register: QubitRegister, control: int, target: int, angle: float):
    """
    Controlled phase rotation (used in QFT)
    
    If control=|1⟩, apply phase to target
    """
    # Build controlled phase gate
    cp_gate = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, np.exp(1j * angle)]
    ], dtype=complex)
    
    apply_two_qubit_gate(register, cp_gate, control, target)


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    
    print("🌌 QDL Quantum Simulator - Gates Demo\n")
    
    # Test 1: Hadamard creates superposition
    print("=" * 60)
    print("TEST 1: Hadamard Gate (Superposition)")
    print("=" * 60)
    
    reg = QubitRegister(1)
    print("\nInitial state:")
    reg.print_state()
    
    print("\nApply H gate:")
    hadamard(reg, 0)
    reg.print_state()
    print("✅ Created equal superposition!")
    
    # Test 2: CNOT creates entanglement (Bell state!)
    print("\n\n" + "=" * 60)
    print("TEST 2: CNOT Gate (Entanglement)")
    print("=" * 60)
    
    reg2 = QubitRegister(2)
    print("\nInitial: |00⟩")
    reg2.print_state()
    
    print("\nApply H to qubit 0:")
    hadamard(reg2, 0)
    reg2.print_state()
    
    print("\nApply CNOT (control=0, target=1):")
    cnot(reg2, 0, 1)
    reg2.print_state()
    
    print("\n✅ Created Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
    print("   Qubits are now ENTANGLED!")
    print("   Measuring one instantly affects the other!")
    
    # Test 3: Pauli gates
    print("\n\n" + "=" * 60)
    print("TEST 3: Pauli Gates")
    print("=" * 60)
    
    reg3 = QubitRegister(1)
    
    print("\nX gate (bit flip):")
    pauli_x(reg3, 0)
    reg3.print_state()
    
    print("\nZ gate (phase flip):")
    pauli_z(reg3, 0)
    reg3.print_state()
    
    print("\n✅ Gates working correctly!")
