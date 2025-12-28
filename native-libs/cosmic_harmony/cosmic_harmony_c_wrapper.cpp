#include "zion-cosmic-harmony.h"
#include <cstring>

#ifdef _WIN32
    #define ZION_EXPORT __declspec(dllexport)
#else
    #define ZION_EXPORT
#endif

extern "C" {

ZION_EXPORT void cosmic_hash(const uint8_t* input, size_t input_len, uint32_t nonce, uint8_t* output) {
    zion::CosmicHarmonyHasher::cosmic_hash(input, input_len, nonce, output);
}

ZION_EXPORT bool cosmic_harmony_initialize() {
    return zion::CosmicHarmonyHasher::initialize();
}

ZION_EXPORT bool check_difficulty(const uint8_t* hash, uint64_t target_difficulty) {
    return zion::CosmicHarmonyHasher::check_difficulty(hash, target_difficulty);
}

}
