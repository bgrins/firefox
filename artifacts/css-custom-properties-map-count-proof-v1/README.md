# Replay

Use the pinned Lean 4.35.0-rc4 Darwin AArch64 distribution already retained in `artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64`. The executable hash is checked; its standard library and runtime are external trusted toolchain dependencies. Python 3 standard library is required; there are no network or package downloads.

From the repository root, with a new output directory:

```sh
python3 -I -S artifacts/css-custom-properties-map-count-proof-v1/check.py --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean --output /private/tmp/css-count-replay-new
```

For relocation, copy exactly the paths in `MANIFEST.json` plus `MANIFEST.json` and `FREEZE.json` into a fresh directory, then run its `check.py` with an absolute toolchain path and new output directory. No repository source access is needed. The checker authenticates all inputs before compiling. Generated logs and `.olean` files belong only in the output directory.

The commit inventory is the manifest roster plus the two seal files. Do not include development builds or receipts as source inputs. The proof is conditional as stated in `SCOPE.md`; native mutation patches are explanatory source correspondence and are not native build results.
