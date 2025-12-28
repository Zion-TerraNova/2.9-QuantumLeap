# 🚀 QDL Quick Start Guide

**Get started with Quantum Data Language in 5 minutes!**

---

## ⚡ Installation (< 1 minute)

```bash
# 1. Activate Python virtual environment
cd /path/to/zion-project
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\Activate.ps1  # Windows

# 2. Dependencies already installed! ✅
# (numpy, scipy, matplotlib)

# 3. Verify installation
python -c "import numpy; print('NumPy:', numpy.__version__)"
```

---

## 🎯 Run Your First Quantum Program (30 seconds)

### Example 1: Bell State (Quantum Entanglement)

```powershell
python QDL\examples\bell_state.py
```

**What you'll see:**
```
✨ Bell state created!
   Qubits 0 and 1 are now ENTANGLED

Results after 1000 measurements:
  |00⟩: 516 times (51.6%)
  |11⟩: 484 times (48.4%)
  |01⟩: 0 times (0.0%)  ← Forbidden by entanglement!
  |10⟩: 0 times (0.0%)  ← Forbidden by entanglement!

✅ PERFECT CORRELATION!
```

**What just happened?**
- Created 2 qubits in superposition
- Entangled them using CNOT gate
- Measured 1000 times
- Qubits ALWAYS measured in same state (00 or 11)
- This is **quantum entanglement** - Einstein's "spooky action"!

---

### Example 2: Grover's Search (Quantum Speedup)

```powershell
python QDL\examples\grover_search.py
```

**What you'll see:**
```
🔍 Grover's Search Algorithm
   Database size: 4 items
   Target: 2

Optimal Grover iterations: 1

Step 4: Measure
✅ SUCCESS! Found target 2

Success rate: 20/20 = 100%
```

**What just happened?**
- Searched database of 4 items
- Found target in **1 iteration** (classical needs 2 average)
- 100% success rate over 20 trials
- For 1M items: **652× faster** than classical!

---

## 📖 Learn by Examples

All examples in `QDL/examples/`:

| File | Difficulty | What You Learn | Time |
|------|-----------|----------------|------|
| `bell_state.py` | Beginner | Entanglement, measurement | 2 min |
| `grover_search.py` | Intermediate | Quantum speedup, amplitude amplification | 3 min |
| `syntax_demo.qdl` | Reference | QDL language syntax | 10 min |

---

## 🛠️ Interactive Tutorial

### Step-by-Step: Create Your Own Quantum Circuit

```powershell
# Open Python REPL
python
```

```python
# Import QDL simulator
import sys
sys.path.append('QDL')

from simulator.qubit import Qubit, QubitRegister
from simulator.gates import hadamard, cnot, pauli_x
from simulator.measurement import measure_all

# Step 1: Create 2 qubits
reg = QubitRegister(2)
print("Initial state:")
reg.print_state()
# Output: |00⟩ with 100% probability

# Step 2: Apply Hadamard to qubit 0 (create superposition)
hadamard(reg, 0)
print("\nAfter Hadamard:")
reg.print_state()
# Output: 50% |00⟩, 50% |10⟩

# Step 3: Apply CNOT (create entanglement!)
cnot(reg, 0, 1)
print("\nAfter CNOT (ENTANGLED!):")
reg.print_state()
# Output: 50% |00⟩, 50% |11⟩ ← Bell state!

# Step 4: Measure
result = measure_all(reg)
print(f"\nMeasurement: {result}")
# Output: [0, 0] or [1, 1] (always matching!)
```

---

## 🎓 Understanding Quantum Concepts

### Superposition
```python
qubit = Qubit(1/np.sqrt(2), 1/np.sqrt(2))
print(qubit)  # |ψ⟩ = 0.707|0⟩ + 0.707|1⟩
print(f"P(0) = {qubit.probability_zero}")  # 0.5 (50%)
print(f"P(1) = {qubit.probability_one}")   # 0.5 (50%)
```

**Key insight:** Qubit is BOTH 0 AND 1 simultaneously until measured!

### Entanglement
```python
# Bell state: (|00⟩ + |11⟩)/√2
# If qubit 0 = 0, then qubit 1 = 0 (100% certain)
# If qubit 0 = 1, then qubit 1 = 1 (100% certain)
# Correlation is INSTANT (faster than light!)
```

**Key insight:** Measuring one qubit affects the other instantly, no matter the distance!

### Quantum Gates
```python
# Hadamard: |0⟩ → (|0⟩ + |1⟩)/√2
hadamard(reg, 0)

# Pauli-X: Quantum NOT (|0⟩ → |1⟩)
pauli_x(reg, 0)

# CNOT: Controlled-NOT (creates entanglement)
cnot(reg, control=0, target=1)
```

**Key insight:** Gates are reversible (unitary matrices)!

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'numpy'`
```powershell
# Solution: Install dependencies
pip install numpy scipy matplotlib
```

### Issue: `ImportError: attempted relative import`
```bash
# Solution: Run from project root
cd /path/to/zion-project
python qdl/examples/bell_state.py  # ✅ Correct
```

### Issue: State not normalized (total probability ≠ 1.0)
```python
# Solution: Always call normalize() after manual state changes
qubit.normalize()
```

---

## 📊 Performance Tips

### Simulation Limits
- **1-10 qubits:** Lightning fast ⚡
- **10-20 qubits:** Fast (few seconds) 🚀
- **20-30 qubits:** Slow (minutes) 🐌
- **30+ qubits:** Very slow (hours+) 🐢
- **50+ qubits:** Classical simulation impossible! 🚫

**Why?** 
- N qubits = 2^N states
- 50 qubits = 1,125,899,906,842,624 states (too many!)

### Optimization
```python
# Don't print every state
reg.print_state(threshold=0.01)  # Only show P > 1%

# Use specific line ranges when reading files
# (Already optimized!)
```

---

## 🎯 Next Steps

### Learn More Algorithms
1. **Quantum Fourier Transform** (coming soon)
2. **Shor's Algorithm** - Factor numbers exponentially faster
3. **Quantum Teleportation** - Beam quantum states
4. **VQE** - Quantum chemistry simulation

### Write Your Own QDL Programs
```qdl
# File: my_first_quantum.qdl
program hello_quantum:
    qubit q0
    
    H q0              # Create superposition
    measure q0 -> c0  # Collapse to 0 or 1
    
    print "Result:", c0
end
```

### Contribute to ZION
- Join Discord: [link]
- GitHub: [link]
- Read Genesis: `docs/genesis/`
- Understand Sacred Knowledge: `docs/SACRED_KNOWLEDGE/`

---

## 💡 Pro Tips

1. **Start small:** 2-3 qubits for learning
2. **Visualize:** Use `qubit.visualize_bloch()` (requires GUI)
3. **Test often:** Quantum bugs are subtle!
4. **Read examples:** Best way to learn
5. **Ask questions:** Community is here to help!

---

## 🌟 ZION Quantum Vision

QDL is not just a toy simulator - it's the foundation for:
- **Quantum Pulse:** 144+ miners in collective entanglement
- **Distributed quantum computing:** 1000+ miners = quantum supercomputer
- **Consciousness mining:** Sacred frequencies + quantum coherence
- **Humanitarian optimization:** Grover search for aid matching
- **Post-quantum security:** Future-proof blockchain

**We're building the future of conscious technology!**

---

## 📞 Support

- **Documentation:** `QDL/README.md`
- **Examples:** `QDL/examples/`
- **API Reference:** (coming soon)
- **Discord:** (coming soon)
- **GitHub Issues:** (coming soon)

---

**ON THE QUANTUM STAR!** 🌌⭐

*Last updated: December 17, 2025*
