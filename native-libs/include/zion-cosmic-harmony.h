#ifndef ZION_COSMIC_HARMONY_H
#define ZION_COSMIC_HARMONY_H

#include <cstdint>
#include <cstring>
#include <vector>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include "blake3.h"  // Fixed include path

namespace zion {

// Golden Ratio constants
constexpr uint32_t PHI_UINT32 = 0x9E3779B9;
constexpr uint64_t PHI_UINT64 = 0x9E3779B97F4A7C15;
constexpr double PHI = 1.618033988749895;

class CosmicHarmonyHasher {
public:
    // Cosmic state structure
    struct CosmicState {
        uint8_t blake3_hash[32];      // Stage 1: Blake3
        uint8_t keccak256_hash[32];   // Stage 2: Keccak-256
        uint8_t sha3_512_hash[64];    // Stage 3: SHA3-512
        uint64_t golden_matrix[8];    // Stage 4: Golden Ratio Matrix
        uint32_t harmony_factor;      // Cosmic resonance
        uint32_t cosmic_nonce;        // Nonce marker
    };
    
    // Initialize Cosmic Harmony
    static bool initialize();
    
    // Main hashing function
    static void cosmic_hash(const uint8_t* input, size_t input_len, 
                           uint32_t nonce, uint8_t* output);
    
    // Advanced hashing with state
    static CosmicState cosmic_hash_advanced(const uint8_t* input, 
                                           size_t input_len, 
                                           uint32_t nonce);
    
    // Galactic matrix operations (Keccak-256)
    static void galactic_matrix_ops(const uint8_t* input, uint8_t* keccak_output);
    
    // Stellar harmony processing (SHA3-512)
    static void stellar_harmony_process(const uint8_t* input, uint8_t* sha3_output);
    
    // Golden ratio matrix transformation
    static void golden_matrix_transform(const uint8_t* input, uint64_t* matrix);
    
    // Cosmic fusion - final stage
    static void cosmic_fusion(const CosmicState& state, uint8_t* final_hash);
    
    // Check difficulty threshold
    static bool check_difficulty(const uint8_t* hash, uint64_t target_difficulty);
    
private:
    static bool s_initialized;
    static EVP_MD_CTX* s_keccak_ctx;
    static EVP_MD_CTX* s_sha3_ctx;
};

} // namespace zion

#endif // ZION_COSMIC_HARMONY_H
