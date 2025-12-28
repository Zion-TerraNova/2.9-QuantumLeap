#pragma once
#include <cstdint>
#include <cstddef>

struct ZionBig256 {
    uint32_t limb[8]{}; // little-endian limbs
    static ZionBig256 from_be_bytes(const uint8_t be[32]){
        ZionBig256 r; for(int i=0;i<32;i++){ int src=31-i; int li=i/4; int off=i%4; r.limb[li] |= ((uint32_t)be[src]) << (off*8); } return r; }
    static ZionBig256 from_hash_le(const uint8_t h[32]){
        ZionBig256 r; for(int i=0;i<32;i++){ int li=i/4; int off=i%4; r.limb[li] |= ((uint32_t)h[i]) << (off*8);} return r; }
    bool is_zero() const { for(int i=0;i<8;i++) if(limb[i]) return false; return true; }
};

inline int zion_big256_cmp(const ZionBig256& a, const ZionBig256& b){ for(int i=7;i>=0;--i){ if(a.limb[i]<b.limb[i]) return -1; if(a.limb[i]>b.limb[i]) return 1; } return 0; }

inline uint64_t zion_difficulty_from_target(const ZionBig256& t){
    // Precise floor((2^256 - 1) / target) but truncated to 64 bits.
    if(t.is_zero()) return 0;
    // Represent target and numerator as 16 32-bit limbs (little-endian) for long division.
    // Numerator: all 0xFFFFFFFF (2^256 -1)
    uint32_t denom[8]; for(int i=0;i<8;i++) denom[i]=t.limb[i];
    bool zero=true; for(int i=0;i<8;i++){ if(denom[i]){ zero=false; break; } }
    if(zero) return 0; // division by zero guard
    // Long division producing 256-bit quotient; we only need high significance up to when it overflows 64 bits.
    // We'll implement classical base-2^32 long division: numerator has 8 limbs of 0xFFFFFFFF.
    // Because numerator >= denom typically, result often large. We'll stop if quotient exceeds 64 bits (saturate at max uint64_t).
    uint32_t num[9]; for(int i=0;i<8;i++) num[i]=0xFFFFFFFFu; num[8]=0; // extra limb for normalization shifts if needed
    // Normalize (Knuth D) so that highest bit of denom's most significant limb is set.
    int msd=7; while(msd>0 && denom[msd]==0) --msd;
    uint32_t leading = denom[msd]; int shift=0; while(shift<32 && (leading & 0x80000000u)==0){ leading <<=1; ++shift; }
    auto shl_arr=[&](uint32_t *a,int n,int s){ if(s==0) return; uint64_t carry=0; for(int i=0;i<n;i++){ uint64_t v=((uint64_t)a[i]<<s)|carry; a[i]=(uint32_t)(v & 0xFFFFFFFFu); carry = v>>32; } if(n<9){} };
    auto shr_arr=[&](uint32_t *a,int n,int s){ if(s==0) return; uint32_t carry=0; for(int i=n-1;i>=0;--i){ uint32_t newcarry = a[i] << (32-s); a[i] = (a[i] >> s) | carry; carry=newcarry; if(i==0) break; } };
    if(shift){ shl_arr(denom,8,shift); shl_arr(num,9,shift); }
    // Division: quotient up to 8 limbs
    uint32_t quot[8]{};
    for(int i=8-1;i>=0;--i){ // position i
        // Compose 64-bit window (num[i+msd+1], num[i+msd]) but ensure index range.
        int idx = i+msd; if(idx+1 >=9) continue;
        __uint128_t hi = num[idx+1];
        __uint128_t lo = num[idx];
        __uint128_t dividend = (hi<<32) | lo;
        uint64_t d = denom[msd]; if(d==0) d=1; // guard
        uint64_t qhat = (uint64_t)(dividend / d);
        if(qhat > 0xFFFFFFFFu) qhat = 0xFFFFFFFFu;
        // Multiply denom by qhat and subtract from num segment
        __uint128_t borrow=0; for(int j=0;j<=msd; ++j){ __uint128_t prod = (__uint128_t)denom[j]*qhat; __uint128_t sub = (__uint128_t)num[i+j] - (prod & 0xFFFFFFFFu) - borrow; num[i+j] = (uint32_t)sub; borrow = (prod>>32) + ((sub>>64)&1); }
        // Handle potential negative (borrow remaining)
        if(borrow){ // qhat too big -> adjust
            --qhat;
            uint64_t carry=0; for(int j=0;j<=msd; ++j){ uint64_t sum = (uint64_t)num[i+j] + denom[j] + carry; num[i+j]=(uint32_t)sum; carry = sum>>32; }
        }
        quot[i] = (uint32_t)qhat;
    }
    if(shift){ shr_arr(num,9,shift); }
    // Collapse quotient limbs into 128 then 64 bits.
    // quot is little-endian; compute 64-bit by taking lower two limbs and higher as overflow.
    unsigned __int128 acc=0; for(int i=7;i>=0;--i){ acc = (acc<<32) | quot[i]; if(acc > (((unsigned __int128)~0ULL))) break; }
    uint64_t result = (uint64_t)(acc & 0xFFFFFFFFFFFFFFFFull);
    if(result==0) result=1; return result;
}

inline bool zion_hash_meets_target(const uint8_t hash[32], const uint8_t target_be[32]){
    ZionBig256 h=ZionBig256::from_hash_le(hash);
    ZionBig256 t=ZionBig256::from_be_bytes(target_be);
    return zion_big256_cmp(h,t)<=0;
}
