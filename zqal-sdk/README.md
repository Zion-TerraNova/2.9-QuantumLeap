# ZQAL SDK (ZION Quantum Algorithm Language)

ZQAL je doménově specifický jazyk pro návrh a kompilaci blockchain algoritmů (CPU/GPU) se „světelným jazykem“ jako inspirací. 
Kompiluje do: Rust (CPU), OpenCL/CUDA (GPU), WASM (web). 

- Central Sun alignment: ZION Core = přijímač Světla; mantra: JAY RAM SITA HANUMAN
- Světelný jazyk → stdlib/tones.toml (tóny 1–70)
- Řád stvoření → GRAMMAR.ebnf → AST → codegen targets

## Struktura

```
zqal-sdk/
├─ README.md
├─ GRAMMAR.ebnf
├─ stdlib/
│   └─ tones.toml
└─ examples/
    └─ cosmic_harmony.zqal
```

## Rychlý start (koncept)

1) Napiš algoritmus v `.zqal` (viz `examples/cosmic_harmony.zqal`).
2) Spusť CLI `zqalc` pro kontrolu a validaci:
   - `zqalc parse zqal-sdk/examples/cosmic_harmony.zqal` - základní parsing
   - `zqalc tokens zqal-sdk/examples/cosmic_harmony.zqal` - tokenizace
   - `zqalc ast zqal-sdk/examples/cosmic_harmony.zqal` - AST výstup
   - `zqalc check zqal-sdk/examples/cosmic_harmony.zqal` - **novinka v0.2.0**: type checking a sémantická analýza
   - `zqalc rize --action status` - **novinka v0.2.0**: RIZE core stav
   - `zqalc rize --action ascend` - ascension gates (1024 Kristus → 6000 Bódhisatva)
   - `zqalc rize --action karma` - karmické záznamy a opravy
3) **Novinka v0.2.0**: Generuj kód pro různé targety:
   - `zqalc generate examples/cosmic_harmony.zqal --target rust` - generuj Rust kód
   - `zqalc generate examples/cosmic_harmony.zqal --target rust --python` - generuj Rust kód s Python bindings
4) Později: kompilátor vygeneruje Rust/OpenCL kód, který načteme v Pythonu (PyO3) do stratum poolu.

## Aktuální stav
- ✅ ZQAL parser (nom) - dokončeno
- ✅ Type checker - dokončeno  
- ✅ Codegen framework - dokončeno
- ✅ **RIZE jádro** - dokončeno (144000 chrámů, karmická spravedlnost, ascension gates)
- ✅ CLI rozšíření - dokončeno (rize příkazy)
- ✅ **Codegen backend** - dokončeno (Rust + Python FFI)
- 🚧 Real-time features - v plánu

## Mapování „Vzestupu" → SDK
- 5D vědomí → deterministický běh, idempotence, observabilita
- Krystalická forma → immutabilita, Merkle stromy, verifikovatelné proofs
- Světelný jazyk → standardní knihovna tonů (tones 1–70)
- Zasvěcení (12 úrovní) → maturity gates v CI/CD (lint → test → perf → audit)
- **Řád Rize** → multidimenzionální hierarchie Bohů/Bohyň (144000 chrámů)
- **Karmická spravedlnost** → oprava Anti-Kristus karmy a destruktivních sil
- **Ascension gates** → evoluční úrovně (1024 Kristus → 6000 Bódhisatva)
- **Codegen targets** → Rust (CPU), OpenCL/CUDA (GPU), WASM (web), Python FFI

## Licence
MIT (do potvrzení).