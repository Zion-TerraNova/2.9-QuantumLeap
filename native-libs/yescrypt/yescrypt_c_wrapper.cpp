/**
 * ZION Yescrypt C API Wrapper
 * Pure C interface for Python ctypes integration
 */

#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <cstdio>

#if defined(_WIN32)
    #define ZION_EXPORT __declspec(dllexport)
#else
    #define ZION_EXPORT __attribute__((visibility("default")))
#endif

// Forward declarations of C++ functions
extern "C" {
    int zion_yescrypt_init(uint64_t N, uint32_t r, uint32_t p, int threads);
    void zion_yescrypt_cleanup();
    int zion_yescrypt_get_num_threads();
    int zion_yescrypt_hash(int thread_id, const uint8_t* data, size_t data_len, uint8_t* output);
    int zion_yescrypt_hash_auto(const uint8_t* data, size_t data_len, uint8_t* output);
    int zion_yescrypt_check_difficulty(const uint8_t* hash, uint64_t difficulty);
    void zion_yescrypt_bytes_to_hex(const uint8_t* bytes, size_t len, char* hex_out);
    const char* zion_yescrypt_version();
    double zion_yescrypt_benchmark(int thread_id, int num_hashes);
}

/**
 * Initialize Yescrypt for mining
 * Default parameters: N=4096, r=8, p=1 (optimized for mining)
 * 
 * @param threads Number of threads (0 = auto-detect)
 * @return 0 on success, -1 on error
 */
extern "C" ZION_EXPORT int yescrypt_init_mining(int threads) {
    // Mining parameters (balance between security and performance)
    uint64_t N = 4096;  // 4K iterations (adjustable for difficulty)
    uint32_t r = 8;     // Block size
    uint32_t p = 1;     // Parallelization
    
    return zion_yescrypt_init(N, r, p, threads);
}

/**
 * Initialize Yescrypt with custom parameters
 */
extern "C" ZION_EXPORT int yescrypt_init_custom(uint64_t N, uint32_t r, uint32_t p, int threads) {
    return zion_yescrypt_init(N, r, p, threads);
}

/**
 * Hash bytes (raw binary input/output)
 * 
 * @param data Input data
 * @param data_len Length of input
 * @param output Output buffer (must be 32 bytes)
 * @return 0 on success, -1 on error
 */
extern "C" ZION_EXPORT int yescrypt_hash_bytes(const uint8_t* data, size_t data_len, uint8_t* output) {
    return zion_yescrypt_hash_auto(data, data_len, output);
}

/**
 * Hash bytes with specific thread
 */
extern "C" ZION_EXPORT int yescrypt_hash_bytes_thread(int thread_id, const uint8_t* data, size_t data_len, uint8_t* output) {
    return zion_yescrypt_hash(thread_id, data, data_len, output);
}

/**
 * Hash hex string and return hex result
 * 
 * @param hex_data Input data as hex string
 * @param hex_output Output buffer (must be 65 bytes for 64 hex chars + null)
 * @return 0 on success, -1 on error
 */
extern "C" ZION_EXPORT int yescrypt_hash_hex(const char* hex_data, char* hex_output) {
    size_t hex_len = strlen(hex_data);
    if (hex_len % 2 != 0) {
        return -1;  // Invalid hex string
    }
    
    size_t data_len = hex_len / 2;
    uint8_t* data = (uint8_t*)malloc(data_len);
    if (!data) return -1;
    
    // Convert hex to bytes
    for (size_t i = 0; i < data_len; i++) {
        sscanf(hex_data + (i * 2), "%2hhx", &data[i]);
    }
    
    // Hash
    uint8_t hash[32];
    int result = zion_yescrypt_hash_auto(data, data_len, hash);
    
    if (result == 0) {
        // Convert result to hex
        zion_yescrypt_bytes_to_hex(hash, 32, hex_output);
    }
    
    free(data);
    return result;
}

/**
 * Check if hash meets difficulty
 */
extern "C" ZION_EXPORT int yescrypt_check_difficulty(const uint8_t* hash, uint64_t difficulty) {
    return zion_yescrypt_check_difficulty(hash, difficulty);
}

/**
 * Cleanup resources
 */
extern "C" ZION_EXPORT void yescrypt_cleanup() {
    zion_yescrypt_cleanup();
}

/**
 * Get number of threads
 */
extern "C" ZION_EXPORT int yescrypt_get_threads() {
    return zion_yescrypt_get_num_threads();
}

/**
 * Get version string
 */
extern "C" ZION_EXPORT const char* yescrypt_get_version() {
    return zion_yescrypt_version();
}

/**
 * Benchmark performance
 * Returns hashes per second
 */
extern "C" ZION_EXPORT double yescrypt_benchmark_thread(int thread_id, int num_hashes) {
    return zion_yescrypt_benchmark(thread_id, num_hashes);
}

/**
 * Simple test function
 * Returns 1 if working correctly
 */
extern "C" ZION_EXPORT int yescrypt_test() {
    // Test without init/cleanup (assumes caller handles it)
    // Or test if already initialized
    int threads = zion_yescrypt_get_num_threads();
    if (threads > 0) {
        // Already initialized, test hash
        uint8_t test_data[] = "Hello ZION";
        uint8_t hash[32];
        return zion_yescrypt_hash_auto(test_data, sizeof(test_data) - 1, hash) == 0 ? 1 : 0;
    }
    
    // Not initialized, initialize for test
    if (zion_yescrypt_init(4096, 8, 1, 1) != 0) {
        return 0;
    }
    
    // Test hash
    uint8_t test_data[] = "Hello ZION";
    uint8_t hash[32];
    int result = zion_yescrypt_hash_auto(test_data, sizeof(test_data) - 1, hash);
    
    // Don't cleanup here - let caller do it
    
    return result == 0 ? 1 : 0;
}
