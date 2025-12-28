/**
 * ZION RandomX C API Wrapper
 * 
 * Simple C API for Python ctypes integration
 * Provides high-level hash computation interface
 * Supports multi-threaded mining
 * 
 * @version 2.9.0
 * @date 2025-11-11
 */

#include <cstring>
#include <cstdint>
#include <cstdlib>
#include <cstdio>

#ifdef _WIN32
    #define ZION_EXPORT __declspec(dllexport)
#else
    #define ZION_EXPORT
#endif

// Forward declarations from zion-randomx.cpp
extern "C" bool randomx_init(const void* key, size_t key_size, int threads);
extern "C" void zion_randomx_hash_raw(const void* input, size_t input_size, void* output);
extern "C" void zion_randomx_hash_vm(int vm_index, const void* input, size_t input_size, void* output);
extern "C" int randomx_get_num_threads();
extern "C" void randomx_cleanup();

/**
 * Simple C API for Python
 */

// Initialize RandomX with pool key and thread count
extern "C" ZION_EXPORT int zion_randomx_init(const char* key_hex, int threads) {
    if (!key_hex) return 0;
    if (threads < 1) threads = 1;
    
    // Convert hex string to bytes
    size_t key_len = strlen(key_hex) / 2;
    uint8_t* key_bytes = (uint8_t*)malloc(key_len);
    
    for (size_t i = 0; i < key_len; i++) {
        sscanf(key_hex + 2*i, "%2hhx", &key_bytes[i]);
    }
    
    bool success = randomx_init(key_bytes, key_len, threads);
    free(key_bytes);
    
    return success ? 1 : 0;
}

// Calculate hash from hex string input
extern "C" ZION_EXPORT void zion_randomx_hash(const char* input_hex, char* output_hex) {
    if (!input_hex || !output_hex) return;
    
    // Convert input hex to bytes
    size_t input_len = strlen(input_hex) / 2;
    uint8_t* input_bytes = (uint8_t*)malloc(input_len);
    
    for (size_t i = 0; i < input_len; i++) {
        sscanf(input_hex + 2*i, "%2hhx", &input_bytes[i]);
    }
    
    // Calculate hash (32 bytes)
    uint8_t hash[32];
    zion_randomx_hash_raw(input_bytes, input_len, hash);
    
    // Convert hash to hex string
    for (int i = 0; i < 32; i++) {
        sprintf(output_hex + 2*i, "%02x", hash[i]);
    }
    output_hex[64] = '\0';
    
    free(input_bytes);
}

// Calculate hash from raw bytes
extern "C" ZION_EXPORT void zion_randomx_hash_bytes(const uint8_t* input, size_t input_len, uint8_t* output) {
    if (!input || !output) return;
    zion_randomx_hash_raw(input, input_len, output);
}

// Calculate hash using specific VM (for manual thread control)
extern "C" ZION_EXPORT void zion_randomx_hash_bytes_vm(int vm_index, const uint8_t* input, size_t input_len, uint8_t* output) {
    if (!input || !output) return;
    zion_randomx_hash_vm(vm_index, input, input_len, output);
}

// Get number of threads
extern "C" ZION_EXPORT int zion_randomx_get_num_threads() {
    return randomx_get_num_threads();
}

// Check if hash meets difficulty
extern "C" ZION_EXPORT int zion_randomx_check_difficulty(const uint8_t* hash, int difficulty) {
    if (!hash || difficulty < 1 || difficulty > 32) return 0;
    
    // Count leading zero bytes
    int zeros = 0;
    for (int i = 0; i < 32; i++) {
        if (hash[i] == 0) zeros++;
        else break;
    }
    
    return zeros >= difficulty ? 1 : 0;
}

// Cleanup
extern "C" ZION_EXPORT void zion_randomx_cleanup() {
    randomx_cleanup();
}

// Get version
extern "C" ZION_EXPORT const char* zion_randomx_version() {
    return "ZION RandomX 2.9.0 (Multi-threaded)";
}
