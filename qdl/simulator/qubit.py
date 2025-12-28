"""
Qubit - Quantum Bit Implementation
===================================

A qubit exists in superposition: α|0⟩ + β|1⟩
where |α|² + |β|² = 1 (normalization)

Classical bit: 0 OR 1
Quantum bit: 0 AND 1 (simultaneously!)
"""

import numpy as np
from typing import Tuple, List
import matplotlib.pyplot as plt


class Qubit:
    """
    Single qubit in superposition
    
    State: |ψ⟩ = α|0⟩ + β|1⟩
    
    where:
    - α = complex amplitude of |0⟩ state
    - β = complex amplitude of |1⟩ state
    - |α|² = probability of measuring 0
    - |β|² = probability of measuring 1
    - |α|² + |β|² = 1 (must always be true!)
    """
    
    def __init__(self, alpha: complex = 1.0, beta: complex = 0.0):
        """
        Initialize qubit in superposition
        
        Args:
            alpha: Amplitude of |0⟩ state (default: 1.0 = pure |0⟩)
            beta: Amplitude of |1⟩ state (default: 0.0)
        
        Examples:
            >>> q = Qubit()                    # |0⟩ state
            >>> q = Qubit(0, 1)               # |1⟩ state  
            >>> q = Qubit(1/√2, 1/√2)         # |+⟩ state (equal superposition)
            >>> q = Qubit(0.6, 0.8)           # 36% |0⟩, 64% |1⟩
        """
        self.alpha = complex(alpha)
        self.beta = complex(beta)
        self.normalize()
        
        # Metadata (for tracking in distributed system later)
        self.miner_id = None
        self.consciousness_level = 0
        self.phase_offset = 0.0
    
    def normalize(self):
        """
        Ensure |α|² + |β|² = 1
        
        Critical: Quantum states MUST be normalized!
        """
        norm = np.sqrt(abs(self.alpha)**2 + abs(self.beta)**2)
        
        if norm < 1e-10:  # Avoid division by zero
            # Default to |0⟩ if collapsed to zero
            self.alpha = 1.0
            self.beta = 0.0
        else:
            self.alpha /= norm
            self.beta /= norm
    
    @property
    def state_vector(self) -> np.ndarray:
        """
        Return state as numpy vector: [α, β]
        """
        return np.array([self.alpha, self.beta], dtype=complex)
    
    @property
    def probability_zero(self) -> float:
        """Probability of measuring |0⟩"""
        return abs(self.alpha) ** 2
    
    @property
    def probability_one(self) -> float:
        """Probability of measuring |1⟩"""
        return abs(self.beta) ** 2
    
    def to_bloch_sphere(self) -> Tuple[float, float]:
        """
        Convert qubit state to Bloch sphere coordinates
        
        Bloch sphere: Visual representation of qubit
        - North pole: |0⟩
        - South pole: |1⟩
        - Equator: Superposition states
        
        Returns:
            (theta, phi) in radians
            theta ∈ [0, π]   (polar angle)
            phi ∈ [0, 2π]    (azimuthal angle)
        """
        # |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
        
        # Calculate theta
        theta = 2 * np.arccos(abs(self.alpha))
        
        # Calculate phi (phase difference)
        if abs(self.alpha) < 1e-10:
            phi = 0.0
        else:
            phi = np.angle(self.beta / self.alpha)
        
        return (theta, phi)
    
    def visualize_bloch(self, title: str = "Qubit State"):
        """
        Visualize qubit on Bloch sphere
        
        Useful for debugging and understanding quantum states
        """
        theta, phi = self.to_bloch_sphere()
        
        # Convert to Cartesian coordinates
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)
        
        # Create 3D plot
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw sphere
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        sphere_x = np.outer(np.cos(u), np.sin(v))
        sphere_y = np.outer(np.sin(u), np.sin(v))
        sphere_z = np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(sphere_x, sphere_y, sphere_z, alpha=0.1, color='cyan')
        
        # Draw axes
        ax.plot([0, 0], [0, 0], [-1.5, 1.5], 'k-', alpha=0.3)  # Z-axis
        ax.plot([0, 1.5], [0, 0], [0, 0], 'k-', alpha=0.3)      # X-axis
        ax.plot([0, 0], [0, 1.5], [0, 0], 'k-', alpha=0.3)      # Y-axis
        
        # Label states
        ax.text(0, 0, 1.3, '|0⟩', fontsize=14)
        ax.text(0, 0, -1.3, '|1⟩', fontsize=14)
        ax.text(1.3, 0, 0, '|+⟩', fontsize=12)
        ax.text(0, 1.3, 0, '|+i⟩', fontsize=12)
        
        # Draw qubit state vector
        ax.quiver(0, 0, 0, x, y, z, color='red', arrow_length_ratio=0.1, linewidth=3)
        ax.scatter([x], [y], [z], color='red', s=100)
        
        # Add state information
        info = f"α = {self.alpha:.3f}\n"
        info += f"β = {self.beta:.3f}\n"
        info += f"P(0) = {self.probability_zero:.3f}\n"
        info += f"P(1) = {self.probability_one:.3f}"
        ax.text2D(0.02, 0.98, info, transform=ax.transAxes, 
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(title)
        
        plt.show()
    
    def __repr__(self) -> str:
        return f"Qubit(α={self.alpha:.3f}, β={self.beta:.3f})"
    
    def __str__(self) -> str:
        """Pretty print qubit state"""
        return f"|ψ⟩ = {self.alpha:.3f}|0⟩ + {self.beta:.3f}|1⟩"


class QubitRegister:
    """
    Register of multiple qubits (quantum register)
    
    State: |ψ⟩ = |q₀⟩ ⊗ |q₁⟩ ⊗ ... ⊗ |qₙ₋₁⟩
    
    For n qubits: 2^n possible states!
    
    Examples:
        2 qubits: |00⟩, |01⟩, |10⟩, |11⟩ (4 states)
        3 qubits: |000⟩ ... |111⟩ (8 states)
        10 qubits: 1024 states
        50 qubits: 1,125,899,906,842,624 states (limit of classical simulation!)
    """
    
    def __init__(self, num_qubits: int):
        """
        Initialize quantum register
        
        Args:
            num_qubits: Number of qubits (max ~50 for classical simulation)
        """
        if num_qubits > 20:
            print(f"⚠️  WARNING: {num_qubits} qubits = {2**num_qubits} states!")
            print(f"   This might be slow or run out of memory.")
            print(f"   Recommended: ≤ 20 qubits for fast simulation")
        
        self.num_qubits = num_qubits
        self.num_states = 2 ** num_qubits
        
        # State vector: Complex amplitudes for ALL possible states
        # Initial state: |00...0⟩ (all qubits in |0⟩)
        self.state_vector = np.zeros(self.num_states, dtype=complex)
        self.state_vector[0] = 1.0  # |00...0⟩ has amplitude 1
        
        # Metadata
        self.miners = []  # List of miner IDs (for distributed system)
        self.entanglements = []  # Pairs of entangled qubits
    
    def get_probabilities(self) -> np.ndarray:
        """
        Get probability distribution over all states
        
        Returns:
            Array of probabilities: [P(|00...0⟩), P(|00...1⟩), ...]
        """
        return np.abs(self.state_vector) ** 2
    
    def get_state_string(self, state_index: int) -> str:
        """
        Convert state index to binary string
        
        Args:
            state_index: Index in state vector (0 to 2^n - 1)
        
        Returns:
            Binary string, e.g., "101" for state |101⟩
        
        Examples:
            >>> reg = QubitRegister(3)
            >>> reg.get_state_string(0)  # "000" = |000⟩
            >>> reg.get_state_string(5)  # "101" = |101⟩
        """
        return format(state_index, f'0{self.num_qubits}b')
    
    def print_state(self, threshold: float = 0.01):
        """
        Print current quantum state (only significant amplitudes)
        
        Args:
            threshold: Minimum probability to display (default: 1%)
        """
        print(f"\nQuantum State ({self.num_qubits} qubits):")
        print("=" * 50)
        
        probabilities = self.get_probabilities()
        
        for i, (amplitude, prob) in enumerate(zip(self.state_vector, probabilities)):
            if prob > threshold:
                state_str = self.get_state_string(i)
                print(f"|{state_str}⟩: {amplitude:>8.3f}  (P = {prob:.3f})")
        
        print("=" * 50)
        
        # Verify normalization
        total_prob = np.sum(probabilities)
        print(f"Total probability: {total_prob:.6f} (should be 1.0)")
        
        if abs(total_prob - 1.0) > 1e-6:
            print("⚠️  WARNING: State not normalized!")
    
    def __repr__(self) -> str:
        return f"QubitRegister({self.num_qubits} qubits, {self.num_states} states)"


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    print("🌌 QDL Quantum Simulator - Qubit Demo\n")
    
    # Test 1: Single qubit states
    print("=" * 60)
    print("TEST 1: Single Qubit States")
    print("=" * 60)
    
    print("\n1. Pure |0⟩ state:")
    q0 = Qubit(1, 0)
    print(q0)
    print(f"   P(0) = {q0.probability_zero:.3f}")
    print(f"   P(1) = {q0.probability_one:.3f}")
    
    print("\n2. Pure |1⟩ state:")
    q1 = Qubit(0, 1)
    print(q1)
    print(f"   P(0) = {q1.probability_zero:.3f}")
    print(f"   P(1) = {q1.probability_one:.3f}")
    
    print("\n3. Equal superposition |+⟩ = (|0⟩ + |1⟩)/√2:")
    q_plus = Qubit(1/np.sqrt(2), 1/np.sqrt(2))
    print(q_plus)
    print(f"   P(0) = {q_plus.probability_zero:.3f}")
    print(f"   P(1) = {q_plus.probability_one:.3f}")
    print("   → 50/50 chance!")
    
    print("\n4. Custom superposition (60% |0⟩, 40% |1⟩):")
    q_custom = Qubit(np.sqrt(0.6), np.sqrt(0.4))
    print(q_custom)
    print(f"   P(0) = {q_custom.probability_zero:.3f}")
    print(f"   P(1) = {q_custom.probability_one:.3f}")
    
    # Test 2: Quantum register
    print("\n\n" + "=" * 60)
    print("TEST 2: Quantum Register (3 qubits)")
    print("=" * 60)
    
    reg = QubitRegister(3)
    print(f"\nCreated: {reg}")
    reg.print_state()
    
    print("\n✅ Qubit simulation working!")
    print("   Next: Implement quantum gates (H, CNOT, etc.)")
