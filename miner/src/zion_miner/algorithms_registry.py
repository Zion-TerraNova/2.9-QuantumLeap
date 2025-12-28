#!/usr/bin/env python3
"""ZION Miner v2.9 — Algorithms Registry (Public)

This file is a **public-miner-only** extraction of the algorithm registry.

Design goals:
- Keep miner usable without importing blockchain core.
- Prefer native wrappers if available (optional).
- Provide safe pure-Python fallbacks for RandomX/Yescrypt (reduced, not full-performance).

Supported identifiers:
- `cosmic_harmony` (optional native wrapper)
- `randomx` (sha3-chain fallback)
- `yescrypt` (pbkdf2 fallback or optional bindings)
- `autolykos_v2` (optional OpenCL helper or blake2b fallback)

NOTE: This registry does not implement consensus or validation logic.
"""

from __future__ import annotations

import hashlib
from importlib import import_module
from typing import Dict

# --- Cosmic Harmony (optional native wrapper) -------------------------------
_get_cosmic_hasher = None
try:
    # If user provides a compatible wrapper on PYTHONPATH
    from cosmic_harmony_wrapper import get_hasher as _get_cosmic_hasher  # type: ignore
except Exception:
    _get_cosmic_hasher = None


def _hash_cosmic_harmony(data: bytes, nonce: int) -> bytes:
    if _get_cosmic_hasher is None:
        raise RuntimeError(
            "Cosmic Harmony wrapper not available. Install/build the native wrapper and expose cosmic_harmony_wrapper.get_hasher()."
        )
    hasher = _get_cosmic_hasher(use_cpp=True)
    if nonce == 0:
        return hasher.hash(data, 0)
    return hasher.hash(data, int(nonce))


COSMIC_HARMONY_AVAILABLE = _get_cosmic_hasher is not None

# --- RandomX (fallback) -----------------------------------------------------
_RANDOMX_BLOB_THRESHOLD = 64


def _prepare_randomx_input(data: bytes | None, nonce: int) -> bytes:
    data = data or b""
    if len(data) >= _RANDOMX_BLOB_THRESHOLD:
        return data
    nonce_bytes = int(nonce).to_bytes(8, "little", signed=False)
    return data + nonce_bytes


def _hash_randomx(data: bytes, nonce: int) -> bytes:
    # If nonce=0, assume blob already has embedded nonce
    if nonce == 0:
        state = hashlib.sha3_256(data).digest()
        for _ in range(16):
            state = hashlib.sha3_256(state + data).digest()
        return state

    input_bytes = _prepare_randomx_input(data, nonce)
    state = hashlib.sha3_256(input_bytes).digest()
    for _ in range(16):
        state = hashlib.sha3_256(state + input_bytes).digest()
    return state


# --- Yescrypt (optional bindings or fallback) --------------------------------
_yescrypt_hash = None
try:
    import yescrypt  # type: ignore

    def _yescrypt_hash(data: bytes, nonce: int) -> bytes:
        if nonce == 0:
            salt = hashlib.sha256(data).digest()
            return yescrypt.hash(data, salt)
        salt = hashlib.sha256(data + int(nonce).to_bytes(8, "little")).digest()
        return yescrypt.hash(data, salt)

except Exception:

    def _yescrypt_hash(data: bytes, nonce: int) -> bytes:
        if nonce == 0:
            salt = hashlib.sha256(data[:8]).digest()
        else:
            salt = hashlib.sha256(int(nonce).to_bytes(8, "little")).digest()
        return hashlib.pbkdf2_hmac("sha256", data, salt, iterations=1024, dklen=32)


# --- Autolykos v2 (optional OpenCL helper or fallback) -----------------------
_autolykos_opencl = None
_autolykos_native_available = False

try:
    from .algorithms.autolykos_opencl import AutolykosOpenCL

    _autolykos_opencl = AutolykosOpenCL()
    _autolykos_native_available = True

    def _hash_autolykos_v2(data: bytes, nonce: int) -> bytes:
        return _autolykos_opencl.hash_single(data, int(nonce))

except Exception:
    try:
        pyautolykos2 = import_module("pyautolykos2")  # type: ignore

        def _hash_autolykos_v2(data: bytes, nonce: int) -> bytes:
            return pyautolykos2.hash(data, int(nonce))

        _autolykos_native_available = True
    except Exception:

        def _hash_autolykos_v2(data: bytes, nonce: int) -> bytes:
            if nonce == 0:
                input_bytes = data
            else:
                input_bytes = data + int(nonce).to_bytes(8, "little", signed=False)
            state = hashlib.blake2b(input_bytes, digest_size=32).digest()
            for _ in range(8):
                state = hashlib.blake2b(state + input_bytes, digest_size=32).digest()
            return state


AVAILABLE_ALGOS: Dict[str, Dict[str, object]] = {
    "cosmic_harmony": {
        "available": COSMIC_HARMONY_AVAILABLE,
        "hash": _hash_cosmic_harmony if COSMIC_HARMONY_AVAILABLE else None,
    },
    "cosmic": {
        "available": COSMIC_HARMONY_AVAILABLE,
        "hash": _hash_cosmic_harmony if COSMIC_HARMONY_AVAILABLE else None,
    },
    "randomx": {"available": True, "hash": _hash_randomx},
    "yescrypt": {"available": True, "hash": _yescrypt_hash},
    "autolykos_v2": {"available": True, "hash": _hash_autolykos_v2},
}


def is_available(name: str) -> bool:
    info = AVAILABLE_ALGOS.get(name)
    return bool(info and info.get("available"))


def get_hash(name: str, data: bytes, nonce: int = 0) -> str:
    algo = AVAILABLE_ALGOS.get(name)
    if algo and algo.get("available") and callable(algo.get("hash")):
        hash_bytes = algo["hash"](data, int(nonce))  # type: ignore[index]
        return hash_bytes.hex()
    raise RuntimeError(f"Algorithm '{name}' is not available")


def list_supported() -> Dict[str, bool]:
    excluded = {"cosmic"}
    return {
        k: bool(v.get("available"))
        for k, v in AVAILABLE_ALGOS.items()
        if k not in excluded
    }
