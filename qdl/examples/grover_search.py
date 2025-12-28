"""
Grover's Algorithm - Quantum Search
====================================

Classical search: O(N) - must check every item
Quantum search: O(√N) - QUADRATIC SPEEDUP!

Example: Search 1,000,000 items
- Classical: ~1,000,000 operations
- Quantum: ~1,000 operations (1000× faster!)

How it works:
1. Start in equal superposition (all items at once!)
2. Oracle: Mark the target item (flip phase)
3. Diffusion: Amplify marked item's amplitude
4. Repeat √N times
5. Measure → find target with high probability!

For 4 items (2 qubits):
- Classical: 4 checks worst case
- Quantum: 1-2 iterations (π/4 × √4 ≈ 1.57)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from simulator.qubit import QubitRegister
from simulator.gates import hadamard, pauli_z, pauli_x, cnot, cz
from simulator.measurement import measure_all
import numpy as np


def create_oracle(register: QubitRegister, target: int):
    """
    Oracle: Mark target state by flipping its phase
    
    Oracle |x⟩ = -|x⟩ if x == target, else |x⟩
    
    For 2 qubits, 4 possible targets:
    - target=0 (|00⟩): Apply Z₀Z₁
    - target=1 (|01⟩): Apply Z₀X₁Z₁X₁  
    - target=2 (|10⟩): Apply X₀Z₀X₀Z₁
    - target=3 (|11⟩): Apply Z₀ or Z₁ or CZ
    
    Args:
        register: Quantum register (must be in superposition!)
        target: Index to mark (0 to 2^n - 1)
    """
    n = register.num_qubits
    
    if n != 2:
        raise NotImplementedError("Oracle only implemented for 2 qubits")
    
    # Convert target to binary
    target_bits = [int(b) for b in format(target, f'0{n}b')]
    
    # Flip qubits that should be 0 (so target becomes |11⟩)
    for i, bit in enumerate(target_bits):
        if bit == 0:
            pauli_x(register, i)
    
    # Apply CZ (marks |11⟩)
    cz(register, 0, 1)
    
    # Flip back
    for i, bit in enumerate(target_bits):
        if bit == 0:
            pauli_x(register, i)


def grover_diffusion(register: QubitRegister):
    """
    Grover diffusion operator (amplitude amplification)
    
    D = 2|ψ⟩⟨ψ| - I
    
    where |ψ⟩ = equal superposition = H^⊗n|0⟩
    
    Implementation:
    1. Apply H to all qubits
    2. Apply X to all qubits
    3. Multi-controlled Z (flip |00...0⟩)
    4. Apply X to all qubits
    5. Apply H to all qubits
    
    This inverts amplitudes around average → amplifies marked state!
    """
    n = register.num_qubits
    
    # Step 1: H to all qubits
    for i in range(n):
        hadamard(register, i)
    
    # Step 2: X to all qubits (|ψ⟩ → |0⟩)
    for i in range(n):
        pauli_x(register, i)
    
    # Step 3: Multi-controlled Z (for 2 qubits, just CZ)
    if n == 2:
        cz(register, 0, 1)
    else:
        # For n>2, need multi-controlled gate (not implemented yet)
        raise NotImplementedError(f"Diffusion for {n} qubits not implemented")
    
    # Step 4: X to all qubits (|0⟩ → |ψ⟩)
    for i in range(n):
        pauli_x(register, i)
    
    # Step 5: H to all qubits
    for i in range(n):
        hadamard(register, i)


def grover_search(num_qubits: int, target: int, verbose: bool = True):
    """
    Run Grover's algorithm to find target
    
    Args:
        num_qubits: Number of qubits (database size = 2^n)
        target: Index to search for (0 to 2^n - 1)
        verbose: Print step-by-step output
    
    Returns:
        Measurement result (should be target!)
    """
    if verbose:
        print(f"🔍 Grover's Search Algorithm")
        print(f"   Database size: 2^{num_qubits} = {2**num_qubits} items")
        print(f"   Target: {target} (binary: {format(target, f'0{num_qubits}b')})")
        print("=" * 60)
    
    # Step 1: Initialize in equal superposition
    register = QubitRegister(num_qubits)
    
    if verbose:
        print("\nStep 1: Initialize equal superposition (H to all qubits)")
    
    for i in range(num_qubits):
        hadamard(register, i)
    
    if verbose:
        register.print_state()
        print(f"   → All {2**num_qubits} states equally likely!")
    
    # Step 2: Calculate optimal iterations
    # Optimal: π/4 × √N where N = 2^n
    N = 2 ** num_qubits
    optimal_iterations = int(np.pi / 4 * np.sqrt(N))
    
    if optimal_iterations < 1:
        optimal_iterations = 1
    
    if verbose:
        print(f"\nOptimal Grover iterations: π/4 × √{N} ≈ {optimal_iterations}")
    
    # Step 3: Grover iterations
    for iteration in range(optimal_iterations):
        if verbose:
            print(f"\n{'='*60}")
            print(f"Iteration {iteration + 1}/{optimal_iterations}")
            print(f"{'='*60}")
        
        # Apply Oracle (mark target)
        if verbose:
            print(f"\n  3a. Oracle: Mark target |{format(target, f'0{num_qubits}b')}⟩")
        
        create_oracle(register, target)
        
        if verbose:
            register.print_state(threshold=0.001)
            print(f"     → Target state phase flipped!")
        
        # Apply Diffusion (amplify target)
        if verbose:
            print(f"\n  3b. Diffusion: Amplify marked state")
        
        grover_diffusion(register)
        
        if verbose:
            register.print_state(threshold=0.001)
            
            # Show target probability
            probs = register.get_probabilities()
            target_prob = probs[target]
            print(f"     → Target probability: {target_prob:.1%}")
    
    # Step 4: Measure
    if verbose:
        print(f"\n{'='*60}")
        print("Step 4: Measure")
        print(f"{'='*60}")
    
    result_bits = measure_all(register)
    result = int(''.join(map(str, result_bits)), 2)
    
    if verbose:
        print(f"\nMeasurement result: {result} (binary: {''.join(map(str, result_bits))})")
        
        if result == target:
            print(f"✅ SUCCESS! Found target {target}")
        else:
            print(f"❌ Found {result}, but target was {target}")
            print(f"   (Grover is probabilistic, try again!)")
    
    return result


def demonstrate_grover_speedup():
    """
    Compare classical vs quantum search
    """
    print("\n" + "="*60)
    print("QUANTUM SPEEDUP DEMONSTRATION")
    print("="*60)
    
    num_qubits = 2
    N = 2 ** num_qubits
    
    print(f"\nDatabase: {N} items")
    print(f"Target: Random item (index 2)")
    
    print(f"\n📊 Classical Search:")
    print(f"   Best case: 1 check (lucky first try)")
    print(f"   Average: {N/2} checks")
    print(f"   Worst case: {N} checks (always check last!)")
    
    print(f"\n⚡ Quantum Search (Grover):")
    optimal = int(np.pi / 4 * np.sqrt(N))
    print(f"   Iterations: {optimal}")
    print(f"   Success probability: ~100% (after {optimal} iterations)")
    print(f"   Speedup: {N / optimal:.1f}× faster than classical average!")
    
    print(f"\n🌟 For larger databases:")
    for n in [10, 20, 30]:
        N_large = 2 ** n
        classical = N_large / 2
        quantum = int(np.pi / 4 * np.sqrt(N_large))
        speedup = classical / quantum
        
        print(f"   {N_large:,} items: Classical {classical:,.0f} vs Quantum {quantum:,} → {speedup:.0f}× speedup!")


def run_multiple_trials(target: int = 2, num_trials: int = 10):
    """
    Run Grover multiple times to show success rate
    """
    print("\n" + "="*60)
    print(f"GROVER SUCCESS RATE ({num_trials} trials)")
    print("="*60)
    
    successes = 0
    
    for trial in range(num_trials):
        result = grover_search(num_qubits=2, target=target, verbose=False)
        
        if result == target:
            successes += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"Trial {trial+1:2d}: {status} (result={result}, target={target})")
    
    success_rate = successes / num_trials * 100
    
    print(f"\n📊 Success rate: {successes}/{num_trials} = {success_rate:.0f}%")
    print(f"   Theory: ~100% with optimal iterations")
    
    if success_rate >= 80:
        print(f"   ✅ Excellent! Grover working correctly")
    elif success_rate >= 60:
        print(f"   ⚠️  Good, but could be better (check iterations)")
    else:
        print(f"   ❌ Too low! (Bug in implementation?)")


if __name__ == "__main__":
    print("🌌 QDL Quantum Simulator - Grover's Algorithm Demo\n")
    
    # Demo 1: Single search with detailed output
    print("\n" + "="*70)
    print("DEMO 1: Find item #2 in database of 4 items")
    print("="*70)
    
    result = grover_search(num_qubits=2, target=2, verbose=True)
    
    # Demo 2: Compare classical vs quantum
    demonstrate_grover_speedup()
    
    # Demo 3: Success rate over multiple trials
    run_multiple_trials(target=2, num_trials=20)
    
    # Final message
    print("\n" + "="*70)
    print("✨ GROVER'S ALGORITHM DEMONSTRATED!")
    print("="*70)
    print("\nKey insights:")
    print("  ✅ Quantum search is √N faster than classical")
    print("  ✅ For 1,000,000 items: 500,000 → 1,000 operations!")
    print("  ✅ Amplitude amplification = quantum magic")
    print("\nApplications:")
    print("  - Database search (obvious)")
    print("  - Breaking symmetric crypto (AES256 → AES128 effective)")
    print("  - SAT solving (NP-complete problems)")
    print("  - ZION: Mining optimization, humanitarian matching")
    
    print("\n🌟 Next: Quantum Fourier Transform (for Shor's algorithm)")
