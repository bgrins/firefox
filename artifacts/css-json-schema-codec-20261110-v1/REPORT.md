# Checked JSON values for the first-order CSS research IR

The JSON AST adapter now has universal soundness and completeness against an independent schema relation over actual `Lean.Json` values. Canonical encoders for all typed expressions/statements roundtrip through that adapter and the existing typed checker. For alias-free input, successful typed decoding is equivalent to the JSON schema describing the exact erased typed tree. This closes the JSON-value gap left by the preceding typed-data codec; it does not prove JSON text parsing or CSS prose interpretation.

The new reader also handles the fixed legacy aliases, and the actual escape document's definitions/program now use this same proved adapter. The concrete document theorem still connects the result to the existing `CssEscape.Escaped` relation. The standalone file runner imports no generated escape reference. Separate runners check canonical JSON serialization/reparse and compare the parsed tree with the proved fixture; all execute decoded values rather than substituting the reference program.

The main generic interfaces are:

```lean
readExprData aliases j = some e ↔ ExprSchema aliases j e
checkExprJson aliases Γ t (encodeExprJson e) = some e
checkExprJson [] Γ t j = some e ↔ ExprSchema [] j (encodeExpr e)
```

There are corresponding statement theorems. Nonempty alias environments retain an explicit schema-plus-normalization contract. The reader handles arbitrary finite JSON trees without fuel. Its schema explicitly covers both raw-map child directions and either field order, including arbitrary cached sizes; it assumes no raw-map invariant. Exact fields, operation tags, arities and ordered children are checked. Canonical scalar literals use a character's validity proof rather than natural-number wrapping.

The scope remains the existing first-order IR: naturals, Unicode scalars, Booleans, scalar lists and unit, with typed locals and the existing statement forms. This milestone does not serialize the separate `ParserIR` number-consumption extensions or add CSS feature coverage.

The complete author checker and clean replay from 34 source-only inputs passed. `verification/report.json` and `source-replay/report.json` record the results. The source inventory contains 143 theorem declarations: 82 preserved and 61 new, including 35 kernel boundary cases. The accepted run also exercised 13 actual-file rows per runner, 13 parser observations, four malformed-document refusals, six compiling semantic mutants and three provenance controls.

The semantic controls change an encoder opcode, operand order or scan budget; reject an admitted unit/raw-object shape; or select the wrong document alias. Each concrete assertion must pass on baseline, the mutated implementation must compile, an unchanged theorem must fail, and the concrete assertion must be explicitly proved false by Lean's decision procedure. The proof-carrying reader's inability to construct a wrong certificate is not counted as a compiling semantic mutant. Kernel-checked `cbv` supplies reductions where needed; strict audits retain every theorem's standard axiom dependencies.

[MAPPING.md](MAPPING.md) gives the exact guarantees, object representation, alias policy and remaining boundaries. These include standard JSON parsing/printing/quotation, duplicate-text-key behavior, numeric lexical spellings, general top-level document orchestration, shared primitive semantics, the reviewed CSS-to-IR interpretation and native refinement. The fixed document bridge and runtime observations cover this fixture; they do not turn those remaining boundaries into universal theorems.

The most direct next proof step is the outer document/alias environment contract, followed by reuse for another admitted algorithm representation if that removes a real workflow gap. There is no need to claim an entire JSON parser or an automatic CSS prose derivation from this milestone.

Reproduce with the pinned Lean 4.35.0-rc4 installation and new output directories:

```sh
python3 -I -B check.py --lean /absolute/path/to/lean --out /new/verification-directory
python3 -I -B replay.py --lean /absolute/path/to/lean --out /new/source-replay-directory
```

`SOURCE-ONLY.json` lists required sources and hashes. No prior capsule, canonical library, Firefox source, WPT, browser build, Git index or commit was modified. Owned development compiled output and replay temporary source/build trees have been removed.
