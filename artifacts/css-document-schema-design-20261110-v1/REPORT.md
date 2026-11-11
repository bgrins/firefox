# Next milestone: a generic document profile and safe alias reuse

Implement a signature-parameterized outer document reader for a finite list of
flat, alias-free definitions. First prove document soundness, signature/definition
alignment, and exact compatibility with the existing escape reader. The small
prototype here already proves the main alias-reuse lemma: validating a definition
with one input is sufficient to reuse it under arbitrary extra local bindings
without capturing them, including inside `foldNat`.

This is an extension of the research IR transport contract. It adds no CSS feature
coverage and does not mechanically interpret CSS prose.

## Current boundary

The accepted `Document.readDefinition` decodes each body with an empty alias
environment and checks it at the singleton context `[head]`. The four definitions
have hard-coded names, input types, and result types. Program decoding resolves
`use` through first-match alias lookup, wraps the selected data in `.scope head`,
and rechecks it at the use-site context. Definitions cannot recursively reference
one another. The stored alias carries its input type and data; its result type is
inferred again at use sites after singleton validation.

Generic schema soundness/completeness and canonical JSON-value roundtrips are
already proved. For arbitrary alias-using programs, accepted typed correspondence
currently proves existence of the raw schema and exact normalized erasure. It
does not give a general converse: normalization removes `.scope` guards, so
matching normalized erasure alone cannot imply acceptance. The proposed document
soundness theorem must preserve this distinction.

Outer fields also have a separate boundary: `fieldsExactly` enumerates raw map
entries, while `field` uses Lean's map lookup. Arbitrary `Json.obj` values can have
invalid ordering or cached sizes. Do not silently identify tree membership with
successful lookup. Preserve the current lookup operation as an explicit shared
primitive in the first outer-schema theorem. JSON text parsing and duplicate-key
collapse remain outside the value-level theorem.

## Concrete interface

The narrow extension can keep the existing JSON format and version. A caller
supplies a trusted profile, rather than allowing JSON to choose its own typing
assumptions:

```lean
structure Signature where
  name : String
  head : FirstOrder.Ty
  result : FirstOrder.Ty

readDefinitions : List Signature → Lean.Json → Option TypedCodec.Aliases
readDocumentWith (signatures : List Signature) (result : FirstOrder.Ty)
  (j : Lean.Json) : Option (FirstOrder.Stmt [] result)
```

Reject duplicate signature names, require definitions to
have exactly those names, and process signatures in their supplied order. Decode
every definition with `readExprData []`, then check its declared singleton input
and result. Preserve `source_map` as an inert object and the existing four outer
field names. An empty profile is useful and should be admitted. No recursive
alias graph, dependency sort, arbitrary fuel, or new expression tags are needed.

Keep `readDocument` as the escape-profile wrapper and prove it equals the old
function on **every JSON value**, including refusal behavior. The fixed profile
has unique names and exactly the old order/types, so the proof should reduce the
generic definition traversal to the existing four binds. This makes the existing
actual-file runner use the new generic path without changing its interface.

## Independent relation and theorems

Define the outer relation without calling `readDocumentWith`, `readDefinitions`,
`readDefinition`, `checkExpr`, or `checkStmt`:

- `ExactKeys j names`: `j` is an object whose enumerated key list is a permutation
  of the distinct expected names. Prove `fieldsExactly` reflects this relation
  under name uniqueness; do not merely restate its Boolean result.
- `Field j key value`: successful existing `Json.getObjVal?` lookup. This is an
  explicitly shared map primitive, not a separately verified object-map parser.
- `DefinitionSchema signature definitions alias`: the named field exists; there
  is a typed `Expr [signature.head] signature.result` whose encoding is the
  alias body; and `ExprSchema []` relates that exact field JSON to that encoding.
  Preserve the alias name and head exactly.
- `DefinitionsSchema`: ordered `List.Forall₂` of the preceding relation, exact
  keys, and distinct signature names. This gives the first-match alias lookup an
  unambiguous identity; arbitrary membership is not a substitute.
- `DocumentSchema signatures result j p`: exact outer keys, schema number 1,
  object-valued source map, definitions satisfying `DefinitionsSchema`, and a
  program field with `StmtSchema aliases` whose normalized erasure is exactly
  `encodeStmt p`.

Prove these concrete results:

1. `readDefinitions signatures definitions = some aliases` iff
   `DefinitionsSchema signatures definitions aliases`. This is attainable with
   the existing alias-free expression iff plus structural list induction.
2. `readDocumentWith signatures result j = some p` implies
   `DocumentSchema signatures result j p`. Compose the definition result and
   existing accepted-statement schema theorem. This is **soundness**, not full
   document completeness for arbitrary alias-using programs.
3. Every validated alias reused in `head :: tail` returns the singleton meaning
   of its declared input, independently of all values/types in `tail`. The
   prototype supplies the generic erasure and evaluation lemmas needed here.
4. The escape-profile wrapper equals the previous fixed reader on all JSON
   values. Existing fixture correspondence and runner evidence then transfer.

A universal converse for `DocumentSchema` should be a separate change. It needs
an independent scoped typing relation retaining the `.scope` checks at the right
binder contexts. Simply adding `checkStmt ... = some p` to the relation would
hide that gap. A separate canonical document roundtrip for alias-free programs
can be useful later, but would not replace this missing alias-using converse.

## Prototype result

`Model.lean` defines context-tail weakening and environment append. `Prototype.lean`
proves seven generic laws over arbitrary finite typed expressions and contexts:
variable erasure, expression erasure, lookup preservation, evaluation preservation,
scoped rechecking, ambient-tail independence, and rechecking of already validated
normalized data. No additional axioms, arbitrary fuel, or unsafe evaluation are
used. The normalized-data premise is supplied by the existing alias-free JSON
schema theorem in the planned document integration; it is not asserted for
arbitrary unchecked alias data here.

The four kernel cases include a fold that uses both its accumulator and the
alias's original input, a rejected singleton tail reference, a wrong scope head,
and a constructive counterexample: checking `.scope nat (var 1)` only in
`[nat,nat]` succeeds and reads the ambient value 900. Thus the singleton-validation
step is essential; a matching head guard alone does not prevent capture.

Fresh source-only validation passed **24 theorem audits** (13 preserved, seven
new laws, four cases). A type-correct mutation replaces the weakened fold body
with constant zero. The implementation still compiles; unchanged laws fail and
a baseline-accepted concrete witness is decided false. This checks the binder
meaning, not only parser refusal. `verification/report.json` retains receipts.
Temporary compiled output was removed.

```sh
python3 -B check.py --lean /path/to/lean/bin/lean --out /new/report/path
```

Only the four required typed-IR/codec dependencies are copied. `PRESERVED.json`
and `INPUTS.json` identify hashes and their exact import-only integration origin.
The prototype does not implement the new outer reader or claim its theorem yet.

## Implementation and failure controls

Start with `Signature`, duplicate rejection, and structural `readDefinitions`.
Prove the exact-key and definition-list results, then lift the prototype's alias
lemmas into the accepted namespace. Add `readDocumentWith`, its soundness theorem,
and the all-JSON escape-wrapper equivalence. Keep the actual-file runner on that
wrapper. A second small profile, such as a natural-input scalar-successor alias,
should demonstrate the implementation is not hard-coded to escape names.

Include empty and several-definition profiles; duplicate signatures; missing,
extra, and duplicate raw definition keys; wrong singleton result/input; unknown
`use`; cycles/forward references; wrong use-site head; tail capture; and fold
binder references. Exercise malformed raw object ordering separately from normal
parser-produced objects. Keep duplicate text-key tests labeled parser observations.

Meaningful implementation mutations include validating definitions in a larger
ambient context, losing the definition result check, assigning a definition to
the wrong name, reversing signature/alias alignment, bypassing duplicate-name
rejection, and reading the wrong top-level field. Each accepted mutation must
compile, violate an unchanged theorem, and fail a concrete semantic witness.

This is a focused next artifact, with no JSON text parser proof, generalized
recursive module system, native compiler integration, or new CSS conformance claim.
