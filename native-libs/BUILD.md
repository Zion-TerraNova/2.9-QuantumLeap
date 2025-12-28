# ZION Native Mining Libraries - Build Guide

Build instructions for native mining algorithm libraries.

---

## 📋 Supported Algorithms

| Algorithm | Type | Expected Performance |
|-----------|------|---------------------|
| **Cosmic Harmony** | CPU/GPU | 5,000-20,000 H/s |
| **RandomX** | CPU | 2,000-10,000 H/s |
| **Yescrypt** | CPU | 1,000-5,000 H/s |

---

## 🛠️ Prerequisites

### All Platforms

- **CMake** 3.15+
- **C++17** compiler (GCC 8+, Clang 10+, MSVC 2019+)
- **Git** (for cloning external dependencies)

### macOS

```bash
# Install dependencies
brew install cmake openssl libomp

# For ARM Macs (M1/M2/M3)
export OPENSSL_ROOT_DIR=$(brew --prefix openssl)
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install cmake build-essential libssl-dev libomp-dev git
```

### Windows

```powershell
# Install Visual Studio 2019/2022 with C++ workload
# Install CMake: https://cmake.org/download/
# Install OpenSSL: https://slproweb.com/products/Win32OpenSSL.html
```

---

## 📦 External Dependencies

Clone required external libraries:

```bash
cd native-libs
mkdir -p external && cd external

# Blake3 (for Cosmic Harmony)
git clone https://github.com/BLAKE3-team/BLAKE3.git blake3

# RandomX
git clone https://github.com/tevador/RandomX.git randomx

# Yescrypt
git clone https://github.com/openwall/yescrypt.git yescrypt
```

---

## 🔨 Build Instructions

### 1. Cosmic Harmony

```bash
cd native-libs/cosmic_harmony
mkdir build && cd build

# macOS/Linux
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DOPENSSL_ROOT_DIR=$(brew --prefix openssl)
make -j$(nproc)

# Windows (PowerShell)
cmake .. -G "Visual Studio 17 2022" -A x64
cmake --build . --config Release
```

**Output:** `libcosmic_harmony_zion.dylib` (macOS), `libcosmic_harmony_zion.so` (Linux), `cosmic_harmony_zion.dll` (Windows)

### 2. RandomX

```bash
cd native-libs/randomx
mkdir build && cd build

# macOS/Linux
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Windows
cmake .. -G "Visual Studio 17 2022" -A x64
cmake --build . --config Release
```

**Output:** `librandomx_zion.dylib/.so/.dll`

### 3. Yescrypt

```bash
cd native-libs/yescrypt
mkdir build && cd build

# macOS (with libomp)
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DZION_LIBOMP_ROOT=$(brew --prefix libomp)
make -j$(nproc)

# Linux
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Windows
cmake .. -G "Visual Studio 17 2022" -A x64
cmake --build . --config Release
```

**Output:** `libyescrypt_zion.dylib/.so/.dll`

---

## 📁 Installation

Copy built libraries to Python miner path:

```bash
# macOS/Linux
cp build/lib*.dylib /path/to/miner/src/zion_miner/
# or
cp build/lib*.so /path/to/miner/src/zion_miner/

# Windows
copy build\Release\*.dll C:\path\to\miner\src\zion_miner\
```

---

## 🧪 Testing

### Test Cosmic Harmony

```bash
cd cosmic_harmony/build
./test_cosmic_harmony
```

### Test RandomX

```bash
cd randomx/build
./test_randomx_basic
```

### Test Yescrypt

```bash
cd yescrypt/build
./test_yescrypt_basic
```

---

## 🐍 Python Integration

The miner automatically loads native libraries if available:

```python
from zion_miner.algorithms import get_algorithm_info

info = get_algorithm_info("cosmic_harmony")
print(f"Native: {info.native}")  # True if library found
print(f"Hashrate: {info.hashrate} H/s")
```

If native libraries are not found, the miner falls back to Python implementations.

---

## ⚠️ Troubleshooting

### "OpenSSL not found"

```bash
# macOS
export OPENSSL_ROOT_DIR=$(brew --prefix openssl)

# Linux
sudo apt install libssl-dev

# Windows: Install from https://slproweb.com/products/Win32OpenSSL.html
```

### "libomp not found" (macOS)

```bash
brew install libomp
cmake .. -DZION_LIBOMP_ROOT=$(brew --prefix libomp)
```

### "RandomX source not found"

```bash
git clone https://github.com/tevador/RandomX.git external/randomx
```

### Low hashrate

1. Ensure `-march=native` flag is used
2. Check OpenMP is enabled (parallel processing)
3. Verify CPU supports required SIMD instructions

---

## 📊 Performance Optimization

### CPU Flags

| Flag | Effect |
|------|--------|
| `-march=native` | Optimize for local CPU |
| `-O3` | Maximum optimization |
| `-fopenmp` | Enable parallel processing |
| `-mavx2` | Enable AVX2 SIMD (x86) |

### Thread Configuration

```bash
# Set optimal thread count
export OMP_NUM_THREADS=$(nproc)
```

---

## 📚 API Reference

### Cosmic Harmony C API

```c
// Initialize the algorithm
bool cosmic_harmony_init();

// Compute hash
void cosmic_harmony_hash(
    const uint8_t* input,
    size_t input_len,
    uint32_t nonce,
    uint8_t* output  // 32 bytes
);

// Cleanup
void cosmic_harmony_cleanup();
```

### RandomX C API

```c
bool randomx_zion_init(const uint8_t* seed, size_t seed_len);
void randomx_zion_hash(const uint8_t* input, size_t len, uint8_t* output);
void randomx_zion_cleanup();
```

### Yescrypt C API

```c
bool yescrypt_zion_init(int threads);
void yescrypt_zion_hash(const uint8_t* input, size_t len, uint8_t* output);
void yescrypt_zion_cleanup();
```

---

## 🔗 Links

- [Blake3 GitHub](https://github.com/BLAKE3-team/BLAKE3)
- [RandomX GitHub](https://github.com/tevador/RandomX)
- [Yescrypt Reference](https://www.openwall.com/yescrypt/)

---

*ZION TerraNova v2.9 — Native Mining Libraries* 🌟
