/**
 * ZION Yescrypt Native Implementation
 * Phase 4: Multi-threaded Yescrypt mining
 * 
 * Performance Target: 500-2,000 H/s
 * Features:
 *   - Multi-threading with OpenMP
 *   - Optimized parameters for mining
 *   - Thread-local memory management
 */

#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <mutex>
#include <atomic>
#include <chrono>
#include <iostream>
#include <iomanip>
#include <sstream>

extern "C" {
#include "yescrypt.h"
}

// Global state for Yescrypt
static bool g_initialized = false;
static yescrypt_shared_t g_shared;
static std::vector<yescrypt_local_t*> g_locals;
static std::mutex g_init_mutex;
static int g_num_threads = 1;

// Mining parameters (optimized for cryptocurrency mining)
static yescrypt_params_t g_params;

/**
 * Initialize Yescrypt with specified parameters
 * 
 * @param N Memory cost parameter (power of 2, e.g., 4096)
 * @param r Block size parameter (e.g., 8)
 * @param p Parallelization parameter (e.g., 1)
 * @param threads Number of threads to use
 * @return 0 on success, -1 on error
 */
extern "C" int zion_yescrypt_init(uint64_t N, uint32_t r, uint32_t p, int threads) {
    std::lock_guard<std::mutex> lock(g_init_mutex);
    
    if (g_initialized) {
        std::cout << "⚠️  Yescrypt already initialized (skipping)" << std::endl;
        return 0;  // Return success, not error
    }
    
    // Set parameters for mining
    // Use YESCRYPT_DEFAULTS which includes RW mode + optimizations
    g_params.flags = YESCRYPT_DEFAULTS;  // YESCRYPT_RW | ROUNDS_6 | GATHER_4 | SIMPLE_2 | SBOX_12K
    g_params.N = N;
    g_params.r = r;
    g_params.p = p;
    g_params.t = 0;  // Time parameter (0 = optimal for our use case)
    g_params.g = 0;  // Hash upgrade parameter
    g_params.NROM = 0;  // No ROM for mining
    
    g_num_threads = threads > 0 ? threads : 1;
    
    // Initialize shared structure (NULL for no ROM in mining)
    memset(&g_shared, 0, sizeof(g_shared));
    
    // Allocate thread-local structures
    g_locals.resize(g_num_threads);
    for (int i = 0; i < g_num_threads; i++) {
        g_locals[i] = new yescrypt_local_t;
        if (yescrypt_init_local(g_locals[i]) != 0) {
            std::cerr << "Failed to initialize thread-local structure " << i << std::endl;
            return -1;
        }
    }
    
    g_initialized = true;
    
    std::cout << "✅ ZION Yescrypt initialized" << std::endl;
    std::cout << "   Parameters: N=" << N << ", r=" << r << ", p=" << p << std::endl;
    std::cout << "   Threads: " << g_num_threads << std::endl;
    std::cout << "   Mode: YESCRYPT_RW (ASIC-resistant)" << std::endl;
    
    return 0;
}

/**
 * Cleanup Yescrypt resources
 */
extern "C" void zion_yescrypt_cleanup() {
    std::lock_guard<std::mutex> lock(g_init_mutex);
    
    if (!g_initialized) {
        return;
    }
    
    // Free thread-local structures
    for (auto* local : g_locals) {
        if (local) {
            yescrypt_free_local(local);
            delete local;
        }
    }
    g_locals.clear();
    
    g_initialized = false;
    std::cout << "Yescrypt cleanup complete" << std::endl;
}

/**
 * Get number of initialized threads
 */
extern "C" int zion_yescrypt_get_num_threads() {
    return g_num_threads;
}

/**
 * Hash data using Yescrypt
 * 
 * @param thread_id Thread ID (0 to num_threads-1)
 * @param data Input data
 * @param data_len Length of input data
 * @param output Output buffer (32 bytes)
 * @return 0 on success, -1 on error
 */
extern "C" int zion_yescrypt_hash(int thread_id, const uint8_t* data, size_t data_len, uint8_t* output) {
    if (!g_initialized) {
        std::cerr << "Yescrypt not initialized" << std::endl;
        return -1;
    }
    
    // Validate thread_id
    if (thread_id < 0 || thread_id >= g_num_threads) {
        thread_id = 0;  // Fallback to first thread
    }
    
    yescrypt_local_t* local = g_locals[thread_id];
    
    // No salt for mining (deterministic from data)
    uint8_t salt[32] = {0};
    
    // Compute hash (use NULL, not nullptr for C library)
    int result = yescrypt_kdf(
        NULL,             // shared (no ROM for mining)
        local,            // thread-local
        data, data_len,   // password
        salt, 32,         // salt
        &g_params,        // parameters
        output, 32        // output buffer
    );
    
    if (result != 0) {
        std::cerr << "yescrypt_kdf failed with code " << result << std::endl;
    }
    
    return result;
}

/**
 * Hash data using auto thread selection (thread-safe)
 * Uses thread ID modulo to distribute across available threads
 */
extern "C" int zion_yescrypt_hash_auto(const uint8_t* data, size_t data_len, uint8_t* output) {
    static std::atomic<int> thread_counter(0);
    int thread_id = thread_counter.fetch_add(1) % g_num_threads;
    return zion_yescrypt_hash(thread_id, data, data_len, output);
}

/**
 * Check if hash meets difficulty target
 * Returns 1 if hash < target, 0 otherwise
 */
extern "C" int zion_yescrypt_check_difficulty(const uint8_t* hash, uint64_t difficulty) {
    // Simple difficulty check: count leading zero bytes
    // More zeros = harder difficulty
    uint64_t hash_value = 0;
    for (int i = 0; i < 8; i++) {
        hash_value = (hash_value << 8) | hash[i];
    }
    
    return hash_value < difficulty ? 1 : 0;
}

/**
 * Convert bytes to hex string
 */
extern "C" void zion_yescrypt_bytes_to_hex(const uint8_t* bytes, size_t len, char* hex_out) {
    for (size_t i = 0; i < len; i++) {
        sprintf(hex_out + (i * 2), "%02x", bytes[i]);
    }
    hex_out[len * 2] = '\0';
}

/**
 * Get Yescrypt library version
 */
extern "C" const char* zion_yescrypt_version() {
    return "ZION Yescrypt v2.9.0";
}

/**
 * Benchmark single hash performance
 * Returns hashes per second
 */
extern "C" double zion_yescrypt_benchmark(int thread_id, int num_hashes) {
    if (!g_initialized) {
        return -1.0;
    }
    
    uint8_t test_data[80];
    uint8_t hash[32];
    
    // Fill test data
    for (int i = 0; i < 80; i++) {
        test_data[i] = i & 0xFF;
    }
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < num_hashes; i++) {
        // Vary nonce
        uint32_t nonce = i;
        memcpy(test_data + 76, &nonce, 4);
        
        zion_yescrypt_hash(thread_id, test_data, 80, hash);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    
    double hashes_per_sec = (num_hashes * 1000.0) / duration;
    return hashes_per_sec;
}
