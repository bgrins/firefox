# Replay

First authenticate FREEZE.json against the independently supplied pin, its MANIFEST.json hash, and every manifest entry. The checker repeats authentication before executing any retained generator or proof.

```
python3 check.py
python3 check.py --run --output /private/tmp/string-provider-fresh-output
python3 gates.py --output /private/tmp/string-provider-fresh-gates
```

Outputs must not exist. TOOLCHAIN.json pins the Lean executable and Rust compiler. LEAN/RUSTC overrides require the recorded Lean digest and exact Rust version. This source-only package needs no live tree, cached olean, Cargo, Firefox build or browser. The checker regenerates the exact source fixture, compiles all Lean modules, audits all named theorems, executes debug/release extracted native code and validates five semantic mutants. gates.py adds a source-only relocation and four authentication-before-execution tamper tests.

Read REPORT.md and SOURCE-MAPPING.md for the mathematical/source/native boundaries and all twelve remaining-scope statuses. The retained failed development mutation harnesses had a missing Byte namespace import and an opaque-recursion witness requiring explicit unfolding; neither is counted as a semantic rejection. A later strict diagnostic classifier initially rejected the genuine lost-prefix proof type mismatch; that tooling failure and the semantic log are retained too.
