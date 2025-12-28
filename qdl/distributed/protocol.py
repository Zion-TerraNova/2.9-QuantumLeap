"""
Distributed Quantum Protocol
=============================

Communication protocol for quantum state synchronization between ZION miners.

Design principles:
1. Minimal latency (quantum coherence ~100μs in real systems)
2. State serialization (complex amplitudes → bytes)
3. Entanglement preservation (synchronized measurements)
4. Error detection (checksums, version compatibility)
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
import struct
import hashlib


class ProtocolVersion:
    """Protocol versioning for backward compatibility."""
    MAJOR = 1
    MINOR = 0
    PATCH = 0
    
    @classmethod
    def to_string(cls) -> str:
        return f"{cls.MAJOR}.{cls.MINOR}.{cls.PATCH}"
    
    @classmethod
    def compatible(cls, other_version: str) -> bool:
        """Check if versions are compatible (same MAJOR version)."""
        other_major = int(other_version.split('.')[0])
        return other_major == cls.MAJOR


class MessageType(Enum):
    """Types of quantum network messages."""
    
    # Connection management
    CONNECT = "CONNECT"              # Initial handshake
    DISCONNECT = "DISCONNECT"        # Graceful shutdown
    HEARTBEAT = "HEARTBEAT"          # Keep-alive ping
    
    # Quantum state operations
    SYNC_STATE = "SYNC_STATE"        # Synchronize quantum register
    ENTANGLE = "ENTANGLE"            # Create entanglement between miners
    MEASURE = "MEASURE"              # Coordinated measurement
    APPLY_GATE = "APPLY_GATE"        # Distributed gate operation
    
    # Quantum Pulse (collective)
    PULSE_INIT = "PULSE_INIT"        # Initialize Quantum Pulse
    PULSE_SYNC = "PULSE_SYNC"        # Synchronize to frequency
    PULSE_TRIGGER = "PULSE_TRIGGER"  # Activate collective state
    
    # Error handling
    ERROR = "ERROR"                  # Error response
    ACK = "ACK"                      # Acknowledgment


@dataclass
class QuantumMessage:
    """
    Network message for quantum operations.
    
    Format:
    - Header: version, type, sender_id, timestamp
    - Payload: operation-specific data
    - Checksum: SHA-256 hash for integrity
    """
    
    msg_type: MessageType
    sender_id: str
    payload: Dict
    version: str = ProtocolVersion.to_string()
    timestamp: float = 0.0
    checksum: Optional[str] = None
    
    def to_bytes(self) -> bytes:
        """Serialize message to bytes for network transmission."""
        data = {
            'version': self.version,
            'type': self.msg_type.value,
            'sender': self.sender_id,
            'timestamp': self.timestamp,
            'payload': self.payload
        }
        
        json_bytes = json.dumps(data).encode('utf-8')
        
        # Compute checksum
        checksum = hashlib.sha256(json_bytes).hexdigest()
        
        # Pack: [4 bytes length][json_bytes][32 bytes checksum]
        length = len(json_bytes)
        return struct.pack('!I', length) + json_bytes + checksum.encode('ascii')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'QuantumMessage':
        """Deserialize message from bytes."""
        # Unpack length
        length = struct.unpack('!I', data[:4])[0]
        
        # Extract components
        json_bytes = data[4:4+length]
        received_checksum = data[4+length:4+length+64].decode('ascii')
        
        # Verify checksum
        computed_checksum = hashlib.sha256(json_bytes).hexdigest()
        if received_checksum != computed_checksum:
            raise ValueError("Checksum mismatch - message corrupted!")
        
        # Parse JSON
        msg_data = json.loads(json_bytes.decode('utf-8'))
        
        return cls(
            msg_type=MessageType(msg_data['type']),
            sender_id=msg_data['sender'],
            payload=msg_data['payload'],
            version=msg_data['version'],
            timestamp=msg_data['timestamp'],
            checksum=received_checksum
        )
    
    def validate(self) -> bool:
        """Validate message format and version compatibility."""
        if not ProtocolVersion.compatible(self.version):
            return False
        
        if not isinstance(self.payload, dict):
            return False
        
        return True


class QuantumStateSerializer:
    """
    Serialize quantum states for network transmission.
    
    Challenge: Complex amplitudes (α, β) → bytes
    Solution: Use float64 for real/imaginary parts
    """
    
    @staticmethod
    def serialize_amplitude(amplitude: complex) -> bytes:
        """Convert complex amplitude to 16 bytes (2 × float64)."""
        real = amplitude.real
        imag = amplitude.imag
        return struct.pack('!dd', real, imag)
    
    @staticmethod
    def deserialize_amplitude(data: bytes) -> complex:
        """Convert 16 bytes back to complex amplitude."""
        real, imag = struct.unpack('!dd', data)
        return complex(real, imag)
    
    @staticmethod
    def serialize_state(amplitudes: List[complex]) -> bytes:
        """Serialize full quantum state (list of amplitudes)."""
        # Header: number of amplitudes (4 bytes)
        n = len(amplitudes)
        result = struct.pack('!I', n)
        
        # Amplitudes: n × 16 bytes
        for amp in amplitudes:
            result += QuantumStateSerializer.serialize_amplitude(amp)
        
        return result
    
    @staticmethod
    def deserialize_state(data: bytes) -> List[complex]:
        """Deserialize quantum state from bytes."""
        # Read header
        n = struct.unpack('!I', data[:4])[0]
        
        # Read amplitudes
        amplitudes = []
        for i in range(n):
            offset = 4 + i * 16
            amp_bytes = data[offset:offset+16]
            amplitudes.append(QuantumStateSerializer.deserialize_amplitude(amp_bytes))
        
        return amplitudes


# ============================================================================
# Protocol Message Builders
# ============================================================================

def build_connect_message(miner_id: str, num_qubits: int) -> QuantumMessage:
    """Build CONNECT message for joining quantum network."""
    return QuantumMessage(
        msg_type=MessageType.CONNECT,
        sender_id=miner_id,
        payload={
            'num_qubits': num_qubits,
            'capabilities': ['bell_state', 'grover', 'qft'],
            'protocol_version': ProtocolVersion.to_string()
        }
    )


def build_entangle_message(
    miner_id: str,
    local_qubit: int,
    target_miner: str,
    target_qubit: int
) -> QuantumMessage:
    """Build ENTANGLE message for creating Bell pair across miners."""
    return QuantumMessage(
        msg_type=MessageType.ENTANGLE,
        sender_id=miner_id,
        payload={
            'local_qubit': local_qubit,
            'target_miner': target_miner,
            'target_qubit': target_qubit,
            'operation': 'CNOT'
        }
    )


def build_sync_state_message(
    miner_id: str,
    state_amplitudes: List[complex]
) -> QuantumMessage:
    """Build SYNC_STATE message with serialized quantum state."""
    state_bytes = QuantumStateSerializer.serialize_state(state_amplitudes)
    
    return QuantumMessage(
        msg_type=MessageType.SYNC_STATE,
        sender_id=miner_id,
        payload={
            'state_data': state_bytes.hex(),  # Hex string for JSON compatibility
            'num_qubits': (len(state_amplitudes) - 1).bit_length()
        }
    )


def build_pulse_init_message(
    miner_id: str,
    frequency: float,
    target_miners: List[str]
) -> QuantumMessage:
    """Build PULSE_INIT message for starting Quantum Pulse."""
    return QuantumMessage(
        msg_type=MessageType.PULSE_INIT,
        sender_id=miner_id,
        payload={
            'frequency': frequency,  # Hz (432, 528, etc.)
            'target_miners': target_miners,
            'pulse_type': 'GHZ_STATE',
            'coherence_threshold': 0.85
        }
    )


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("🌐 QDL Distributed Quantum Protocol v1.0\n")
    
    # Test 1: Message serialization
    print("Test 1: Message Serialization")
    print("-" * 50)
    
    msg = build_connect_message("miner_001", num_qubits=2)
    msg_bytes = msg.to_bytes()
    print(f"Original: {msg.msg_type.value} from {msg.sender_id}")
    print(f"Serialized: {len(msg_bytes)} bytes")
    
    msg_decoded = QuantumMessage.from_bytes(msg_bytes)
    print(f"Decoded: {msg_decoded.msg_type.value} from {msg_decoded.sender_id}")
    print(f"Checksum valid: {msg_decoded.validate()}")
    print()
    
    # Test 2: Quantum state serialization
    print("Test 2: Quantum State Serialization")
    print("-" * 50)
    
    # Bell state: (|00⟩ + |11⟩)/√2
    bell_state = [
        complex(1/2**0.5, 0),  # |00⟩
        complex(0, 0),          # |01⟩
        complex(0, 0),          # |10⟩
        complex(1/2**0.5, 0)   # |11⟩
    ]
    
    state_bytes = QuantumStateSerializer.serialize_state(bell_state)
    print(f"Bell state: {len(bell_state)} amplitudes")
    print(f"Serialized: {len(state_bytes)} bytes")
    
    decoded_state = QuantumStateSerializer.deserialize_state(state_bytes)
    print(f"Decoded: {len(decoded_state)} amplitudes")
    
    # Verify accuracy
    for i, (original, decoded) in enumerate(zip(bell_state, decoded_state)):
        match = abs(original - decoded) < 1e-10
        print(f"  State {i}: {original:.6f} → {decoded:.6f} {'✅' if match else '❌'}")
    
    print()
    
    # Test 3: Protocol messages
    print("Test 3: Protocol Messages")
    print("-" * 50)
    
    messages = [
        build_connect_message("miner_001", 2),
        build_entangle_message("miner_001", 0, "miner_002", 0),
        build_pulse_init_message("miner_001", 432.0, ["miner_002", "miner_003"])
    ]
    
    for msg in messages:
        print(f"📨 {msg.msg_type.value}")
        print(f"   From: {msg.sender_id}")
        print(f"   Payload: {list(msg.payload.keys())}")
    
    print("\n✨ Protocol validation complete!")
    print("📡 Ready for distributed quantum networking!")
