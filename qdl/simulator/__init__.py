"""
QDL Quantum Simulator
=====================

Phase 0 proof-of-concept quantum simulator.

Limitations:
- Classical simulation (not true quantum hardware)
- Limited to ~10 qubits (2^10 = 1024 states)
- Single machine only (no distribution yet)

But: Sufficient to validate QDL concept and algorithms!
"""

__version__ = "0.1.0-alpha"
__author__ = "Maitreya (ZION Team)"
__status__ = "Proof of Concept"

from .qubit import Qubit, QubitRegister
from .gates import *
from .measurement import measure, measure_all

__all__ = [
    'Qubit',
    'QubitRegister', 
    'measure',
    'measure_all'
]
