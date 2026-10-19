# Replay

Authenticate FREEZE.json against the separately supplied pin, then verify MANIFEST.json's digest and every entry before executing check.py. The checker repeats that authentication before imports of any package generator or proof execution.

```
python3 check.py
python3 check.py --run --output /private/tmp/comment-provider-fresh-output
python3 gates.py --output /private/tmp/comment-provider-fresh-gates
```

Output must not exist. TOOLCHAIN.json records the pinned Lean executable and Rust compiler. LEAN/RUSTC overrides are accepted only with the recorded Lean digest and exact Rust version. All source/proof inputs are retained; there is no live-tree input or precompiled olean requirement. No Firefox build is run. The checker compiles fresh Lean outputs, audits all named theorems, regenerates source spans and native fixtures, runs debug/release native checks and validates four semantic mutants. Relocation and tamper receipts are retained separately in this package's evidence directory.

Read REPORT.md for the exact component result and all twelve remaining-scope statuses. This is not whole-provider acceptance.
