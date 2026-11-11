# JSON-schema proof boundary review

Predecessor source roster authenticated against commit `2f8edd8effa87071d0576d488cb6cfa2fc65721c`; all 28 allowlisted files match. The prior result proves generic constructor-data roundtrip and accepted typed erasure, plus one exact fixture equality at Lean.Json. It does not yet prove a generic Lean.Json schema correspondence.

Review the new artifact for:

1. Theorems quantify over actual `Lean.Json` values and the adapter used by the actual-file runner, not a newly renamed constructor tree.
2. Canonical encoding faithfully preserves tag, argument order/arity, literal, variable index, scope and budget. Its decoder roundtrip composes with the existing typed checker.
3. Accepted-input correspondence uses an independent schema interpretation or relation. It must not define the correspondence as decoder success and then merely restate it.
4. Scope wrappers and aliases retain declared-head/type checks; legacy document definitions, alias lookup and provenance fields are explicitly separated if not generically proved.
5. Representation-level JSON object traversal, numeric admission, and text parser normalization are distinguished. Value roundtrip does not prove duplicate-key handling, numeric lexical compatibility, or serializer/parser roundtrip.
6. Runtime executes the decoded object; no emitter, reference interpreter substitution, or generated-reference oracle enters the generic adapter.
7. Exact sources compile from fresh storage; all theorem axioms are audited, semantic controls must compile and fail for the intended semantic reason, and actual files are parsed/executed.

The CSS prose-to-IR mapping, shared primitives, native refinement and text parser remain explicit assumptions. No Firefox or native edits belong to this review.

## Agreed implementation boundary, before source review

The author plans an independent `ExprSchema`/`StmtSchema` relation over actual `Lean.Json`, with a proof-carrying adapter producing the existing constructor-data AST. Exact two-field node objects will account for both raw-tree arrangements and either field order without assuming valid ordering or cached map sizes. Aliases remain a parameter; their interpretation must match first-match lookup, not merely membership. Canonical typed encoders are alias-free. Accepted typed results will expose a raw schema witness and equality between re-encoded typed output and normalized raw data. The concrete legacy document will invoke this same adapter, with top-level orchestration and text parsing explicitly separate.

This is a proposed interface, not an acceptance result. Source implementation, proofs, harness, semantic controls and actual-file replay are pending review.
