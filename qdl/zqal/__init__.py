"""
ZQAL (ZION Quantum Algorithm Language) - Python Runtime
========================================================

Integration layer between ZQAL DSL and QDL quantum runtime.

Exports:
- ZQALInterpreter: Parse and execute .zqal programs
- ToneSystem: 70 light language tones
- QuantumBridge: ZQAL ↔ QDL integration (import separately)
"""

from .interpreter import ZQALInterpreter
from .tones import ToneSystem, SacredFrequency

# Note: QuantumBridge must be imported separately due to relative imports
# from QDL.zqal.bridge import QuantumBridge

__all__ = [
    'ZQALInterpreter',
    'ToneSystem', 
    'SacredFrequency',
]

__version__ = "0.2.0"
__mantra__ = "JAY RAM SITA HANUMAN ✨"
