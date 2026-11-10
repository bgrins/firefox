# Typed data codec for the existing escape IR

The new execution path reads the existing `escape.json` directly in Lean, checks its types/scopes/schema, and executes the resulting typed program. It does not run the old Python AST-to-Lean emitter. A standalone runner imports no generated escape reference; a separate harness compares the decoded tree with the previously proved tree before executing the decoded value.

The reusable proof is at the constructor-data boundary: encoding and decoding arbitrary typed variables, expressions and statements roundtrips for every context/result type. A final erasure check also proves that any accepted constructor tree preserves its exact operations, values and variable indices after alias scope wrappers are removed. A separate universal law rejects mismatched alias heads. This closes more than successful roundtripping of one example, but does not prove arbitrary JSON schema interpretation.

For the actual fixture, a kernel-checked equality proves that decoding its quoted `Lean.Json` value produces the old `escapeTree`. The composed correspondence preserves the result scalar, unread suffix and EOF error against the existing `CssEscape.Escaped` relation. The fixture quotation contains the exact preserved JSON bytes, checked by the harness. Standard JSON parsing/quotation and the old prose-to-AST interpretation remain explicit boundaries. See [MAPPING.md](MAPPING.md) for the exact theorem interfaces, source provenance, alias handling and remaining assumptions.

The author verification and a clean replay from 28 source-only inputs passed. Validation receipts are in `verification-final/report.json` and `source-replay/report.json`. The accepted set contains 115 audited declarations (69 preserved; 46 new, including 28 kernel boundary cases), 13 actual-file execution rows in each of two runners, 13 parser-boundary observations, seven semantic mutants and three provenance controls. Every semantic mutant compiled, failed an unchanged proof, and failed a concrete proposition that passed on the baseline and that Lean explicitly determined is false. The complete audit uses only standard `propext`, `Quot.sound`, and `Classical.choice`; per-declaration dependencies are retained.

The observed text parser keeps the last duplicate object key and recognizes natural numbers according to its internal representation. For example it accepts `1e1` as 10 but rejects `1.0`; these are documented compatibility limits, not a claim of parity with Python's former integer checks. The preserved fixture has no duplicate keys or such number spellings. Alias cycles, unknown aliases, tail capture, wrong types, invalid scalar literals, extra executable fields, wrong arities and unsupported tags are rejected by the checked path and covered by boundary cases.

The next useful proof boundary is the generic JSON-value schema adapter: establish a canonical JSON encoder/decoder theorem and an accepted-schema correspondence, rather than claiming that the current constructor roundtrip already proves it. JSON text parsing, duplicate-key policy, source-to-AST interpretation and native refinement would still remain separate tasks. No CSS feature coverage or Firefox bug count increases from this artifact.

Run from a copied source capsule using the pinned Lean 4.35.0-rc4 toolchain:

```sh
python3 -I -B check.py --lean /absolute/path/to/lean --out /new/verification-directory
python3 -I -B replay.py --lean /absolute/path/to/lean --out /new/source-replay-directory
```

`SOURCE-ONLY.json` lists the required source files and hashes. Replay copies only that allowlist, rebuilds the proofs and reruns controls, then removes its temporary source/build trees. Reports retain logs and hashes, not compiled outputs. No canonical library, Firefox source, WPT, browser build, Git index or commit was changed by this child task.
