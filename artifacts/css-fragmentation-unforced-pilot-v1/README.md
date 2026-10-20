# Fragmentation rule and grid pilot

A standalone Lean component implementing concrete unforced-break rules, finite grid placement, ordered stage selection and conditional emergency progress. Read SCOPE.md and SOURCE-MAPPING.md before interpreting the results. CSS sufficiency, candidate-region and layout/provider admissions remain open.

## Replay

Python 3 standard library and Lean 4.35.0-rc4 are required; no Mathlib, browser, Firefox build or network. The reference toolchain is retained at `artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64`. Its executable SHA is checked; its runtime and standard library remain external trusted dependencies.

```sh
python3 -I -S artifacts/css-fragmentation-unforced-pilot-v1/check.py --lean /absolute/path/to/lean-4.35.0-rc4/bin/lean --output /absolute/new/output
```

For relocation, copy exactly MANIFEST.json's files plus MANIFEST.json and FREEZE.json. Run the copied checker with absolute toolchain/output paths. The checker authenticates the closed roster before creating output, checks source slices and exact theorem/axiom inventories, recompiles all modules and tests semantic mutants.

Mutants change a single actual definition and compile the full definition dependency chain with proof declarations removed. Each unchanged concrete gate first passes against the complete baseline and then fails by kernel reduction against the compiled mutant. Rejection by syntax/name errors does not pass. Generated `.olean` files and logs belong only in the new output directory; do not add them to the source package.

The commit roster is MANIFEST.json plus the two seals. The separate development directory and replay outputs are not dependencies. No source in the existing CSS Lean library or any Firefox native/WPT file was changed.
