# Source-only replay

```sh
python3 /absolute/path/to/css-tokenizer-name-escape-admission-v1/check.py \
  --lean /absolute/path/to/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --output /private/tmp/name-escape-fresh
```

The output must not exist. Required: Python 3 and the pinned Lean 4.35.0-rc4 macOS ARM64 distribution. No network, Cargo, browser, Gecko build or mutable live source is used. The complete input inventory is MANIFEST.json plus that manifest and FREEZE.json; exclude replay outputs, bytecode and .olean files. The separate narrow repair capsule owns candidate bytes/checksum/WPT acceptance. This component retains original source and its counterexamples.
