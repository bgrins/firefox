# Numeric repair integration

This additive component binds the accepted v2 numeric source to the sealed original lexical model. All original capsules remain unchanged.

```sh
python3 /absolute/path/to/css-tokenizer-numeric-repair-integration-v2/check.py \
  --lean /absolute/path/to/lean-4.35.0-rc4-darwin_aarch64/bin/lean \
  --output /private/tmp/numeric-repair-integration-clean
```

Use a fresh output path. The checker authenticates all source inputs and parent manifests before importing helpers. Requirements are Python 3, the pinned Lean binary and the pinned Rust 1.92.0 compiler/toolchain; vendored Rust dependencies are included. Replay is offline and does not invoke Mach, Git, a browser or a Gecko build. Compiler/runtime/system libraries remain trusted external tooling.

The replay compiles the 20 unchanged predecessor Lean modules and three additive modules, checks every audited theorem name against AUDIT-INVENTORY.json and audits axioms, checks the complete source delta and new helper bodies, builds uninstrumented original/candidate cssparser, compares the retained 90-case lexical matrix, and checks 84 captured-prefix traces. Three traces start after a UTF-8 prefix. A compiled native mutation extends the slice into a unit and is rejected by FromStr; the model's corresponding slice equality is false.

The full original lexical replay recipe remains included under `inputs/lexical`. Its earlier four mutation families are retained there; the integration replay runs its own slice mutation rather than claiming those earlier mutation runs were repeated.

Read REPORT.md for the exact library, metadata, machine-arithmetic and source-to-model boundaries. The scanner shim qualification is retained under `inputs/shim`. No universal numeric payload, i32 value or whole-tokenizer proof is claimed.

V2 replaces the new trace prefix’s pictographic character with the supplementary letter U+10000, and adds an exact theorem-name inventory and an automatic pre-compilation source-tamper gate. Historical v1 remains unchanged.
