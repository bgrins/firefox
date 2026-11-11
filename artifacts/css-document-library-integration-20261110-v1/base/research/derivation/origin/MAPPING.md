# JSON-value schema and proof boundary

This capsule closes the expression/statement JSON-value adapter gap left by the typed-data codec. The new universal statements quantify over `Lean.Json` values, not a second standalone raw-tree representation. The wire schema is a research-tool contract inherited from the existing first-order IR fixture; it is not itself a W3C CSS grammar or an automatically derived formalization of prose.

## Schema, reader and typed composition

`Schema.lean` gives independent inductive `ExprSchema`/`StmtSchema` relations. Each constructor fixes the operation tag, exact argument count, literal interpretation and ordered child roles. Numbers use the existing `Json.getNat?` primitive; scalar literals additionally require the Unicode scalar bounds. The `use` constructor explicitly requires first-match alias lookup and records the declared scope head/body. It does not substitute arbitrary alias membership for the reader's lookup policy.

`Reader.lean` returns a data tree paired with a proof of the corresponding schema relation. It traverses the finite JSON structure with a proved decreasing measure, without fuel or a partial definition. The proof carrier ensures that an accepted node has a schema derivation. `SchemaLaws.lean` separately proves completeness by induction over the schema. Consequently:

```lean
readExprData aliases j = some e ↔ ExprSchema aliases j e
readStmtData aliases j = some p ↔ StmtSchema aliases j p
```

These are soundness and completeness for the stated JSON-value grammar, not merely an implication from returning a certificate. They do not assert that every JSON value is admissible, that arbitrary data has the requested type, or that the reader accepts all unrelated JSON object conventions.

`Encoder.lean` emits actual JSON objects from the existing typed `Expr Γ t`/`Stmt Γ t`. `EncoderLaws.lean` proves their schema derivations and universal typed roundtrips for all contexts, result types and finite typed trees. Scalar encoding uses `Char.toNat`, the character's validity proof and `Char.ofNat_toNat`; it does not silently wrap arbitrary naturals into characters.

The final reader composes schema decoding with the preserved typed checker, including its canonical-erasure guard. For supplied aliases, accepted typed results have a schema derivation for a raw tree and an exact equality between the typed erasure and normalized raw tree. Normalization removes declared alias-scope wrappers; the typed checker validates the wrapper's head and all variable/binder types before accepting it.

For an empty alias environment, `TypedSchemaLaws.lean` proves that schema trees contain no effective scope wrappers. This gives the stronger actual-JSON equivalence:

```lean
checkExprJson [] Γ t j = some e ↔ ExprSchema [] j (encodeExpr e)
checkStmtJson [] Γ t j = some p ↔ StmtSchema [] j (encodeStmt p)
```

Here `encodeExpr`/`encodeStmt` are the preserved typed-data erasures. Thus arbitrary accepted alias-free JSON is related to the exact returned typed tree. This is not a claim that re-encoding an arbitrary accepted JSON value reproduces its original representation: field placement, raw cached sizes, numeric representations and aliases can differ while denoting the same admitted tree.

## Raw object representation

`Lean.Json.obj` exposes a raw binary map tree. `Node` explicitly admits all four exact two-entry arrangements: either child direction and either placement of `op`/`args`. Cached size fields may be arbitrary. In particular, the theorem does **not** assume all supplied raw maps are valid, sorted, balanced or produced by `Json.mkObj`. The reader pattern-matches the representation rather than relying on map lookup. Each admitted node still contains exactly one `op` string and one `args` array; duplicate raw keys, extra nodes and unsupported shapes do not match.

The canonical encoder chooses a valid two-entry `args`-then-`op` tree with correct cached sizes. The universal theorem concerns the explicit `Node` grammar; it does not prove a general raw-map normalization library or any property of arbitrary map lookup on malformed trees. Child array order remains significant and is preserved.

## Actual document route and aliases

`Document.lean` preserves the existing fixed four-definition document protocol. Every definition and the program now use the **new proved AST reader**. Definitions are read with an empty alias environment, checked at the declared singleton head/result type, and then supplied to program decoding. Cyclic/recursive aliases and tail capture are refused by that route. Generic alias-parameterized schema theorems do not assume singleton validation; that validation belongs to this document adapter. Alias scope weakening or complete document orchestration is not separately proved universally.

The top-level version/field/name checks, metadata handling and field lookup still use the preserved document helpers. `source_map` is inert provenance and must be an object; its contents are not a semantic proof. The old `foldJson` implementation remains in a preserved imported module but is not called by the new `Document`, `Reader`, `Encoder` or standalone runner path. This distinction can be checked directly from those definitions.

`FixtureJson.lean` is an unchanged standard `json%` quotation of the exact preserved `escape.json` bytes. The harness verifies that correspondence. `fixture_decodes` is a kernel-checked concrete theorem that the new full document route yields the old proved `escapeTree`; `fixture_relation` composes its value/remainder/EOF behavior with the existing escape relation. Kernel-checked `cbv` performs this closed computation and selected boundary computations; per-declaration axiom audits permit only standard logical dependencies. No native-decision axiom is used.

`Runner` imports only the new document route and executes the typed value decoded from the actual file. `RoundtripRunner` encodes that result as canonical JSON, compresses/parses it, checks the canonical AST through the same reader, compares typed erasures and executes the decoded canonical result. `ReferenceRunner` separately compares the actual-file decoded erasure to the proved escape tree before executing the decoded result. The reference is used for comparison, never substituted as the runtime result.

## Text and specification boundaries

The universal theorems are over JSON **values**. Standard `Json.parse`, `Json.compress`, quotation/elaboration, UTF/string/numeric text lexing and duplicate-text-key policy are not proved here. The text parser keeps the last duplicate object key before the AST reader sees the object. Its natural-number representation admits spellings such as `1e1` as 10 while rejecting `1.0`; `PARSER-EXPECTED.json` records these runtime observations. The actual fixture's text roundtrip is observed, not promoted to a universal serializer/parser theorem.

The CSS interpretation and caller obligations remain those of the pinned predecessor. `CLAUSES.json` retains seven exact excerpts and manually chosen AST-pointer links from [CSS Syntax at c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67](https://github.com/w3c/csswg-drafts/blob/c410ee5e4d2afe6d8b2e8ce53723b8d1eb3b5b67/css-syntax-3/Overview.bs), including [consume an escaped code point](https://drafts.csswg.org/css-syntax-3/#consume-escaped-code-point). Character definitions retain the earlier [Infra source pin](https://github.com/whatwg/infra/blob/c67ae1fb1d161b23d0f8c9bf9917ea1993f7b19a/infra.bs). These are inherited reviewed interpretations, not fresh extraction or latest-draft coverage. The scalar-list input still requires the earlier caller/preprocessing contract for CSS conformance; raw DOMString coercion, bytes and native cursors are outside this milestone.

`PRESERVED.json` pins fifteen copied predecessor files from signed commit `2f8edd8effa87071d0576d488cb6cfa2fc65721c`. Root independently authenticated their Git objects in `ROOT-ORIGINS.json`. Shared pure primitives, the semantic meaning of the IR, the old CSS reference relation and the prose-to-AST interpretation remain trust boundaries. No Firefox source, browser build, WPT, canonical library or Git history is changed by this artifact.

## Validation interpretation

The checker audits all new and preserved theorem declarations, runs kernel boundary cases, executes the three actual-file routes, observes parser boundaries and refuses malformed actual documents. Semantic mutants alter compilable encoder definitions, reader acceptance or document alias selection. Each witness must pass on the baseline; the mutant implementation must compile; an unchanged theorem must fail; and the concrete witness must end in Lean's explicit false-proposition diagnostic. A proof-carrying reader's compile-time refusal to construct an invalid certificate is not mislabeled as a compiling semantic mutant. Hash/literal controls separately test provenance refusal.
