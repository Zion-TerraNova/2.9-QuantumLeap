
#define kHashBytes 32
#define kStateBytes 64
#define kBlake2bBlockBytes 128
#define kMaxInputBytes 192
#define kCombinedBytes (kMaxInputBytes + 4)

// Constants
__constant ulong kBlake2bIV[8] = {
    0x6a09e667f3bcc908UL, 0xbb67ae8584caa73bUL,
    0x3c6ef372fe94f82bUL, 0xa54ff53a5f1d36f1UL,
    0x510e527fade682d1UL, 0x9b05688c2b3e6c1fUL,
    0x1f83d9abfb41bd6bUL, 0x5be0cd19137e2179UL
};

__constant uchar kBlake2bSigma[12][16] = {
    { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15 },
    {14,10, 4, 8, 9,15,13, 6, 1,12, 0, 2,11, 7, 5, 3 },
    {11, 8,12, 0, 5, 2,15,13,10,14, 3, 6, 7, 1, 9, 4 },
    { 7, 9, 3, 1,13,12,11,14, 2, 6, 5,10, 4, 0,15, 8 },
    { 9, 0, 5, 7, 2, 4,10,15,14, 1,11,12, 6, 8, 3,13 },
    { 2,12, 6,10, 0,11, 8, 3, 4,13, 7, 5,15,14, 1, 9 },
    {12, 5, 1,15,14,13, 4,10, 0, 7, 6, 3, 9, 2, 8,11 },
    {13,11, 7,14,12, 1, 3, 9, 5, 0,15, 4, 8, 6, 2,10 },
    { 6,15,14, 9,11, 3, 0, 8,12, 2,13, 7, 1, 4,10, 5 },
    {10, 2, 8, 4, 7, 6, 1, 5,15,11, 9,14, 3,12,13, 0 },
    { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15 },
    {14,10, 4, 8, 9,15,13, 6, 1,12, 0, 2,11, 7, 5, 3 }
};

typedef struct {
    ulong h[8];
    ulong t[2];
    ulong f[2];
    uchar buf[kBlake2bBlockBytes];
    size_t buflen;
} Blake2bState;

inline ulong rotr64(const ulong v, const uint c) {
    return (v >> c) | (v << (64U - c));
}

inline ulong load64(const uchar* src) {
    ulong w = 0;
    for (int i = 0; i < 8; ++i) {
        w |= ((ulong)src[i]) << (8 * i);
    }
    return w;
}

inline void store64(uchar* dst, ulong w) {
    for (int i = 0; i < 8; ++i) {
        dst[i] = (uchar)((w >> (8 * i)) & 0xFF);
    }
}

#define G(a, b, c, d, x, y) \
    v[a] = v[a] + v[b] + (x); \
    v[d] = rotr64(v[d] ^ v[a], 32); \
    v[c] = v[c] + v[d]; \
    v[b] = rotr64(v[b] ^ v[c], 24); \
    v[a] = v[a] + v[b] + (y); \
    v[d] = rotr64(v[d] ^ v[a], 16); \
    v[c] = v[c] + v[d]; \
    v[b] = rotr64(v[b] ^ v[c], 63)

void blake2b_compress(Blake2bState* S, const uchar block[kBlake2bBlockBytes]) {
    ulong m[16];
    ulong v[16];

    for (int i = 0; i < 16; ++i) {
        m[i] = load64(block + (i * 8));
    }

    for (int i = 0; i < 8; ++i) {
        v[i] = S->h[i];
        v[i + 8] = kBlake2bIV[i];
    }

    v[12] ^= S->t[0];
    v[13] ^= S->t[1];
    v[14] ^= S->f[0];
    v[15] ^= S->f[1];

    for (int r = 0; r < 12; ++r) {
        __constant uchar* s = kBlake2bSigma[r];
        G(0, 4, 8, 12, m[s[0]], m[s[1]]);
        G(1, 5, 9, 13, m[s[2]], m[s[3]]);
        G(2, 6, 10, 14, m[s[4]], m[s[5]]);
        G(3, 7, 11, 15, m[s[6]], m[s[7]]);
        G(0, 5, 10, 15, m[s[8]], m[s[9]]);
        G(1, 6, 11, 12, m[s[10]], m[s[11]]);
        G(2, 7, 8, 13, m[s[12]], m[s[13]]);
        G(3, 4, 9, 14, m[s[14]], m[s[15]]);
    }

    for (int i = 0; i < 8; ++i) {
        S->h[i] ^= v[i] ^ v[i + 8];
    }
}

void blake2b_init(Blake2bState* S, size_t outlen) {
    for (int i = 0; i < 8; ++i) {
        S->h[i] = kBlake2bIV[i];
    }
    S->h[0] ^= 0x01010000 ^ (uint)outlen;
    S->t[0] = 0;
    S->t[1] = 0;
    S->f[0] = 0;
    S->f[1] = 0;
    S->buflen = 0;
    for(int i=0; i<kBlake2bBlockBytes; i++) S->buf[i] = 0;
}

void blake2b_update(Blake2bState* S, const uchar* data, size_t len) {
    size_t offset = 0;
    while (len > 0) {
        size_t space = kBlake2bBlockBytes - S->buflen;
        size_t take = (len < space) ? len : space;
        
        for(size_t i=0; i<take; i++) {
            S->buf[S->buflen + i] = data[offset + i];
        }
        
        S->buflen += take;
        offset += take;
        len -= take;

        if (S->buflen == kBlake2bBlockBytes) {
            S->t[0] += kBlake2bBlockBytes;
            if (S->t[0] < kBlake2bBlockBytes) {
                S->t[1] += 1;
            }
            blake2b_compress(S, S->buf);
            S->buflen = 0;
        }
    }
}

void blake2b_final(Blake2bState* S, uchar* out, size_t outlen) {
    S->t[0] += S->buflen;
    if (S->t[0] < S->buflen) {
        S->t[1] += 1;
    }
    S->f[0] = 0xFFFFFFFFFFFFFFFFUL;
    
    for(size_t i=S->buflen; i<kBlake2bBlockBytes; i++) {
        S->buf[i] = 0;
    }
    
    blake2b_compress(S, S->buf);

    uchar hash[kStateBytes];
    for (int i = 0; i < 8; ++i) {
        store64(hash + (i * 8), S->h[i]);
    }

    for (size_t i = 0; i < outlen; ++i) {
        out[i] = hash[i];
    }
}

void blake2b_hash(uchar* out, size_t outlen, const uchar* data, size_t len) {
    Blake2bState state;
    blake2b_init(&state, outlen);
    blake2b_update(&state, data, len);
    blake2b_final(&state, out, outlen);
}

__kernel void autolykos_kernel(
    __global const uchar* inputs,
    const uint input_len,
    __global const uint* nonces,
    __global uchar* outputs,
    const uint count
) {
    const size_t idx = get_global_id(0);
    if (idx >= count) {
        return;
    }

    const uint nonce = nonces[idx];
    uchar combined[kCombinedBytes];
    
    // Copy shared input
    for (size_t i = 0; i < input_len; ++i) {
        combined[i] = inputs[i];
    }
    
    // Append nonce (little-endian)
    combined[input_len + 0] = (uchar)(nonce & 0xFF);
    combined[input_len + 1] = (uchar)((nonce >> 8) & 0xFF);
    combined[input_len + 2] = (uchar)((nonce >> 16) & 0xFF);
    combined[input_len + 3] = (uchar)((nonce >> 24) & 0xFF);

    const size_t combined_len = input_len + 4;
    uchar state[kStateBytes];
    blake2b_hash(state, kStateBytes, combined, combined_len);

    uchar block[kStateBytes + kCombinedBytes];
    
    // Memory-hard hashing: 8 rounds
    for (size_t round = 0; round < 8; ++round) {
        for (size_t i = 0; i < kStateBytes; ++i) {
            block[i] = state[i];
        }
        for (size_t i = 0; i < combined_len; ++i) {
            block[kStateBytes + i] = combined[i];
        }
        blake2b_hash(state, kStateBytes, block, kStateBytes + combined_len);
    }

    __global uchar* out_ptr = outputs + (idx * kHashBytes);
    for (size_t i = 0; i < kHashBytes; ++i) {
        out_ptr[i] = state[i];
    }
}
