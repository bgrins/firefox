# Portable ProviderObservation integration

Added `CssSemantics/ProviderObservation.lean` byte-identical to the independently reviewed capsule source (SHA256 dae3b26de60f862ce9c21b25144d451748c23f927613f7e5febf1b30f302f8d5). It can be imported directly; existing central inventories are intentionally unchanged.

From the Firefox checkout, invoke the dedicated replay with the SHA256 of INPUT-FILES.json and a fresh output directory:

```sh
python3 -I -S artifacts/css-provider-observation-library-integration-v1/replay.py \
  --manifest-sha INPUT_SHA \
  --library artifacts/css-spec-lean \
  --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --lean-sha d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf \
  --output /absolute/fresh/output
```

The library and replay inputs may be relocated. Only the two sources in LIBRARY-INPUTS.json, the replay inputs, Python's standard library and the Lean toolchain are required. Supply the actual compiler hash on another platform; the supported version is Lean4.35.0-rc4. The replay compiles copied sources in an owned temporary directory, imports the public module directly, audits every local theorem's axioms, and removes generated products. It does not use Lake, the central aggregator or the Firefox build system.

INPUT-FILES.json pins inputs only; later replay logs and reports are outputs. BEFORE-LIBRARY.json records pre-existing library files for this additive integration's preservation check, not a requirement to transport the full library. EVIDENCE-LINKAGE.json is historical linkage to negative validation and does not add runtime dependencies. See SCOPE.md for specification mapping and remaining integration requirements.
