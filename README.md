# ZION TerraNova v2.9 — Public (QuantumLeap)

This folder is a **draft export** prepared from the private monorepo.

## What’s included

- `miner/`: ZION Miner v2.9 (Stratum/XMRig-style client)
- `native-libs/`: C++ source code for native mining algorithms (Cosmic Harmony, RandomX, Yescrypt)
- `node-skeleton/`: minimal P2P node skeleton + protocol specs (no consensus)
- `docs/`: public documentation (whitepaper-lite, API, economic model, FAQ, mining guide, roadmap)
- `zqal-sdk/`: ZION Quantum Algorithm Language (DSL for mining algorithms)
- `qdl/`: Quantum Data Language — distributed quantum computing framework
- `golden-egg/`: Golden Egg treasure hunt game skeleton (1.75B ZION prize pool)
- `assets/logo/`: official ZION logos and brand assets

## What's intentionally NOT included

- Blockchain core / consensus implementation
- Pool backend, presale/eshop backend, premine distribution tooling
- Any secrets, mnemonics, private keys, production infrastructure details

## Next step (publish)

- Copy the contents of this `public-export/` folder into the public GitHub repo root.
- Run secret scan (gitleaks / trufflehog) before first push.
