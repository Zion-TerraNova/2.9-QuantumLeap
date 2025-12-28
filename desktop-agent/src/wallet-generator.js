// ZION Wallet Generator Module for Desktop Agent
// Ed25519 keypair generation + ZION address derivation

const crypto = require('crypto');
const { randomBytes } = crypto;

class ZionWalletGenerator {
  /**
   * Generate new ZION wallet
   * @returns {Object} Wallet with address, privateKey, publicKey, mnemonic
   */
  static generateWallet() {
    // Generate Ed25519 keypair
    const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519', {
      publicKeyEncoding: { type: 'spki', format: 'der' },
      privateKeyEncoding: { type: 'pkcs8', format: 'der' }
    });

    // Extract raw public key (last 32 bytes of DER encoding)
    const pubKeyRaw = publicKey.slice(-32);
    
    // Derive canonical ZION address: zion1... (bech32-like, chain-compatible)
    // NOTE: current chain validation checks only prefix/charset/length.
    const address = this.deriveAddress(pubKeyRaw);
    
    // Generate mnemonic (12-word seed phrase)
    const mnemonic = this.generateMnemonic();
    
    // Export keys as hex
    const privateKeyHex = privateKey.toString('hex');
    const publicKeyHex = pubKeyRaw.toString('hex');
    
    return {
      address,
      publicKey: publicKeyHex,
      privateKey: privateKeyHex,
      mnemonic,
      createdAt: new Date().toISOString()
    };
  }

  /**
   * Derive ZION address from public key
   * @param {Buffer} publicKey - Raw Ed25519 public key (32 bytes)
   * @returns {string} ZION address
   */
  static deriveAddress(publicKey) {
    // Create a zion1 address compatible with chain validation.
    // We deterministically map SHA256(pubkey) into the allowed bech32-like charset.
    const charset = '023456789acdefghjklmnpqrstuvwxyz';
    const hash = crypto.createHash('sha256').update(publicKey).digest();

    let data = '';
    let i = 0;
    while (data.length < 39) {
      const byte = hash[i % hash.length];
      data += charset[byte % 32];
      i++;
    }
    return 'zion1' + data;
  }

  /**
   * Base32 encoding (RFC 4648)
   */
  static base32Encode(buffer) {
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    let bits = 0;
    let value = 0;
    let output = '';

    for (let i = 0; i < buffer.length; i++) {
      value = (value << 8) | buffer[i];
      bits += 8;

      while (bits >= 5) {
        output += alphabet[(value >>> (bits - 5)) & 31];
        bits -= 5;
      }
    }

    if (bits > 0) {
      output += alphabet[(value << (5 - bits)) & 31];
    }

    // Pad to multiple of 8
    while (output.length % 8 !== 0) {
      output += '=';
    }

    return output;
  }

  /**
   * Generate 12-word mnemonic seed phrase
   * Simplified BIP39-like implementation
   */
  static generateMnemonic() {
    // Generate 128 bits of entropy (12 words)
    const entropy = randomBytes(16);
    
    // Word list (subset for demo - production would use full BIP39 list)
    const wordList = [
      'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
      'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
      'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual',
      'adapt', 'add', 'addict', 'address', 'adjust', 'admit', 'adult', 'advance',
      'advice', 'aerobic', 'afford', 'afraid', 'again', 'age', 'agent', 'agree',
      'ahead', 'aim', 'air', 'airport', 'aisle', 'alarm', 'album', 'alcohol',
      'alert', 'alien', 'all', 'alley', 'allow', 'almost', 'alone', 'alpha',
      'already', 'also', 'alter', 'always', 'amateur', 'amazing', 'among', 'amount',
      'amused', 'analyst', 'anchor', 'ancient', 'anger', 'angle', 'angry', 'animal',
      'ankle', 'announce', 'annual', 'another', 'answer', 'antenna', 'antique', 'anxiety',
      'any', 'apart', 'apology', 'appear', 'apple', 'approve', 'april', 'arch',
      'arctic', 'area', 'arena', 'argue', 'arm', 'armed', 'armor', 'army',
      'around', 'arrange', 'arrest', 'arrive', 'arrow', 'art', 'artefact', 'artist',
      'artwork', 'ask', 'aspect', 'assault', 'asset', 'assist', 'assume', 'asthma',
      'athlete', 'atom', 'attack', 'attend', 'attitude', 'attract', 'auction', 'audit',
      'august', 'aunt', 'author', 'auto', 'autumn', 'average', 'avocado', 'avoid',
      'awake', 'aware', 'away', 'awesome', 'awful', 'awkward', 'axis', 'baby',
      'bachelor', 'bacon', 'badge', 'bag', 'balance', 'balcony', 'ball', 'bamboo',
      'banana', 'banner', 'bar', 'barely', 'bargain', 'barrel', 'base', 'basic',
      'basket', 'battle', 'beach', 'bean', 'beauty', 'because', 'become', 'beef',
      'before', 'begin', 'behave', 'behind', 'believe', 'below', 'belt', 'bench',
      'benefit', 'best', 'betray', 'better', 'between', 'beyond', 'bicycle', 'bid',
      'bike', 'bind', 'biology', 'bird', 'birth', 'bitter', 'black', 'blade',
      'blame', 'blanket', 'blast', 'bleak', 'bless', 'blind', 'blood', 'blossom',
      'blouse', 'blue', 'blur', 'blush', 'board', 'boat', 'body', 'boil',
      'bomb', 'bone', 'bonus', 'book', 'boost', 'border', 'boring', 'borrow',
      'boss', 'bottom', 'bounce', 'box', 'boy', 'bracket', 'brain', 'brand',
      'brass', 'brave', 'bread', 'breeze', 'brick', 'bridge', 'brief', 'bright',
      'bring', 'brisk', 'broccoli', 'broken', 'bronze', 'broom', 'brother', 'brown',
      'brush', 'bubble', 'buddy', 'budget', 'buffalo', 'build', 'bulb', 'bulk',
      'bullet', 'bundle', 'bunker', 'burden', 'burger', 'burst', 'bus', 'business',
      'busy', 'butter', 'buyer', 'buzz', 'cabbage', 'cabin', 'cable', 'cactus'
    ];

    // Convert entropy to indices
    const words = [];
    for (let i = 0; i < 12; i++) {
      const index = (entropy[i] * 256 + (entropy[i + 1] || 0)) % wordList.length;
      words.push(wordList[index]);
    }

    return words.join(' ');
  }

  /**
   * Encrypt private key with password (AES-256-GCM)
   */
  static encryptPrivateKey(privateKeyHex, password) {
    const salt = randomBytes(16);
    const iv = randomBytes(12);
    
    // Derive key from password using PBKDF2
    const key = crypto.pbkdf2Sync(password, salt, 100000, 32, 'sha256');
    
    // Encrypt with AES-256-GCM
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    const encrypted = Buffer.concat([
      cipher.update(privateKeyHex, 'utf8'),
      cipher.final()
    ]);
    const authTag = cipher.getAuthTag();
    
    // Return encrypted data with metadata
    return {
      encrypted: encrypted.toString('hex'),
      salt: salt.toString('hex'),
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  }

  /**
   * Decrypt private key
   */
  static decryptPrivateKey(encryptedData, password) {
    const { encrypted, salt, iv, authTag } = encryptedData;
    
    // Derive key
    const key = crypto.pbkdf2Sync(
      password,
      Buffer.from(salt, 'hex'),
      100000,
      32,
      'sha256'
    );
    
    // Decrypt
    const decipher = crypto.createDecipheriv(
      'aes-256-gcm',
      key,
      Buffer.from(iv, 'hex')
    );
    decipher.setAuthTag(Buffer.from(authTag, 'hex'));
    
    const decrypted = Buffer.concat([
      decipher.update(Buffer.from(encrypted, 'hex')),
      decipher.final()
    ]);
    
    return decrypted.toString('utf8');
  }

  /**
   * Validate ZION address format
   */
  static validateAddress(address) {
    return this.getAddressType(address) === 'zion1';
  }

  /**
   * Identify address type.
   * - zion1: canonical chain-compatible address
   * - legacy: old desktop-agent style (ZION...)
   * - invalid: unknown/invalid
   */
  static getAddressType(address) {
    if (typeof address !== 'string') return 'invalid';
    const a = address.trim();
    if (!a) return 'invalid';

    // Canonical chain format
    if (a.startsWith('zion1')) {
      if (a.length < 42 || a.length > 90) return 'invalid';
      const validChars = /^[0-9acdefghjklmnpqrstuvwxyz]+$/;
      const data = a.slice(5);
      if (!data || !validChars.test(data)) return 'invalid';
      return 'zion1';
    }

    // Legacy format (kept only for compatibility display)
    const legacyRegex = /^ZION[A-Z2-7]{20,60}$/;
    if (legacyRegex.test(a)) return 'legacy';

    return 'invalid';
  }
}

module.exports = ZionWalletGenerator;
