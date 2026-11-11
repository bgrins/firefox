# Independent number-document review

Accepted within the stated model boundaries; no blocking finding. This is an actual `Lean.Json` interchange and execution theorem, not mechanical derivation of CSS prose or native Stylo refinement.

## Authenticated inputs and reproduction

Reviewed `css-number-document-transfer-20261110-v1` at source manifest SHA256 `45851e7ad67daa48022c5c1388250fdd129a9858e6c00c52376abd3fe14c2330` (62 inputs). `CHECK.json` binds the independent receipts and all 129 command/refusal logs. The independent complete replay exactly matches the author's receipt, SHA256 `7b9e11ba573844b498fccc326d7995a0c9e4f60f255a21b61ad7a42586364c55`.

`core-check.py` separately authenticated 49 immutable Git origins, representing 40 unique preserved inputs, and exact import-line transport. Origins are canonical library revision `56c09405cd45a3c9b333dcec747e39efaebc7e1b` and accepted ParserIR/lowering revision `7d4e7fcd82e8557ea9d236f412930b7b3bd8d073`. This authenticates object bytes and revision attribution, not new cryptographic signature validation. The CSS Syntax source remains the accepted pinned revision, not a claim about the newest specification.

Reproduce the full review with the author's `replay.py --lean <pinned lean> --out <fresh directory>`, and the additional boundary checks with this directory's `core-check.py` using the same arguments. Both use fresh temporary source trees and remove compiled output. No native build, browser execution, canonical library modification, or Git mutation was performed for this review.

## Proof and implementation assessment

`ParserSchema` is an independent inductive relation over actual JSON nodes and typed parser constructors. It contains no decoder-success predicate. The seven constructor forms have exact argument arities, ordered roles and shape checks. Predicate and legacy statement leaves use the existing proved alias-free reader with empty alias environments; legacy statements have empty variable scope. The recursive reader terminates structurally on JSON size, rather than an arbitrary fuel cutoff.

`decodeParser_spec` provides soundness and completeness for this relation. Canonical encoders round-trip universally. The versioned envelope's exact keys, version, object-valued inert source map and program relation give `document_spec` an actual-JSON equivalence. Raw object enumeration and keyed lookup are separately represented; malformed raw maps do not gain lookup success merely by containing the right key list. Text parsing, duplicate textual key handling and serialization are separate boundaries.

Execution actually runs the decoded parser. Structural lowering does not call the high-level ParserIR interpreter as an oracle. The composition preserves complete successful values and state. Failure is mapped to an explicitly atomic `(none, originalState)` result; the source interface erases failed state, so this is an explicit strengthening, not recovery of hidden source state. Pair/right/nonempty rollback and optional behavior depend on the accepted lowering theorem and shared primitive semantics.

The number result type does not identify the CSS algorithm. The fixed fixture equality and prior `NumericResult` relation supply that identity. The generic accepted-document theorem applies to any parser of `NumberShape`; `fixed_number_ready` separately requires the caller's `StartsNumber` premise. Empty and nonnumeric runtime rows test total model behavior, not invocation by the normative CSS algorithm.

The document supplies the parser/control program. Exact numeric projection remains the fixed ordinary Lean function `NumberTransfer.project` applied after the lowered parser executes; this milestone neither serializes nor newly lowers that projection. Exact integer/decimal results do not establish IEEE conversion, native overflow behavior, memory safety or machine resource bounds. English-to-model correspondence and the shared primitive definitions remain explicit trust boundaries.

## Independent validation

The fresh full replay passed 325 axiom audits, including 57 new declarations and 30 kernel cases; 84 actual-file runtime rows; nine malformed-file refusals; four compiling semantic mutants; and three provenance controls. These totals include preserved proofs and must not be counted as 325 new CSS results. Both actual files were decoded and executed by the same runner, with no profile-based tree selection. The independent reference uses regular expressions and exact Python integers. Semantic controls rebuild the modified implementation before requiring the intended false-witness diagnostic.

A separate fresh core build checked 46 source modules and `Boundary.lean`. Its 12 additional kernel proofs cover all four raw two-field tree/key-order layouts with arbitrary cached sizes, raw duplicate/extra-field rejection, rejection of a legacy expression capturing an unavailable variable, the distinction between outer decode failure and accepted parser failure, and the limit of shape checking. In particular, the changed valid document consumes `1+2` as significand 1 with scale 2, while the pinned number parser retains `+2` and returns scale 0. This supplies an executable counterexample to identifying CSS semantics from result shape alone.

The boundary proofs and all accepted audits use only the permitted standard axioms. All frozen inputs were authenticated again after execution. No compiled outputs remain in this review directory. `CHECK.json`, `core/report.json`, `replay/report.json` and their retained logs are the detailed receipts.
