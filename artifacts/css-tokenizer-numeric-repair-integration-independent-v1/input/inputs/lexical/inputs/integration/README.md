# Replay

```sh
python3 /absolute/path/to/css-tokenizer-name-escape-repair-integration-v1/check.py \
  --lean /absolute/path/to/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --output /private/tmp/name-escape-integration-fresh
```

The output directory must not exist. Python 3 and the pinned Lean 4.35.0-rc4 macOS ARM64 distribution are required. Replay uses only authenticated local sources and no browser/native build. MANIFEST.json, FREEZE.json and every manifest-listed path form the complete companion inventory. Both predecessors are copied unchanged, including their manifests. Generated replay outputs, Python bytecode and .olean files are excluded.
