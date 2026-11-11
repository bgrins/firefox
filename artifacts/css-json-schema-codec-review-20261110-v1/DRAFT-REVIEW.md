# Initial schema/reader source review

The draft uses actual `Lean.Json`; it does not substitute a renamed raw AST for JSON. `Node` enumerates the four two-entry tree shapes and key arrangements, requiring exactly one string `op` field and one array `args` field. Arbitrary cached sizes are accepted deliberately. This is compatible with considering all raw Json objects rather than silently assuming a valid canonical map. `ExprArguments`/`StmtArguments` specify explicit operation tags, argument lengths, literal kinds, ordered child roles and scan budgets. The relations are defined independently of Reader success.

`readExpr`/`readStmt` return subtype witnesses of these relations. Pattern branches construct the corresponding relation constructors. Recursive calls consume strict JSON substructure; alias bodies are supplied constructor data rather than recursively read from an alias's text. Alias references pin the first matching `find?` result and its name, not arbitrary membership. The explicit name equality guard is redundant with the find predicate but safe.

No blocking schema/reader mismatch found in these draft bytes. Numeric meaning delegates to `Lean.Json.getNat?` in both schema and reader; this primitive is a shared interpretation boundary, not an independently proved decimal parser. Scalar bounds are explicit. Scope-head and expression/statement type validation are intentionally deferred to the existing typed checker; the final accepted typed theorem must expose both layers.

Still pending: generic canonical encoder, roundtrip/accepted-result theorems, source-only harness, exact adapter linkage from the document/file runner, malformed actual-file controls, and independent replay. Do not treat this draft review as final acceptance.

A proof-carrying decoder can reject certain wrong-op mutations at implementation compilation. That is useful kernel protection but is not a compiling semantic mutant. Validation should also include at least a compiling semantic change, such as decoder over-rejection or encoder wrong opcode/child order, that an unchanged theorem and concrete false witness detect.
