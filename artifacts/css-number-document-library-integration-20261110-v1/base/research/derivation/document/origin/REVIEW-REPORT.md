# Generic document schema implementation review

Accepted as the bounded document-schema milestone described below. No blocking
finding remains after independent source review and a complete fresh source-only
replay, including semantic controls and actual-file execution.

Reviewed capsule: `css-document-schema-20261110-v1`. The frozen 45-input
`SOURCE-ONLY.json` SHA256 is
`f1edabfc7536fcd774189f89fd18fd9972b672296465a2a0e976bd2740071029`.
The author's final report SHA256 is
`7170d4f79ab6a73fe4a0de99fd179caf686e33de19278034bac5a026eb3943f5`.

## Independent relations and executable correspondence

`ExactKeys` is a permutation of the object's enumerated key list and the
expected names, rather than a renamed Boolean check. `exactFields_spec` proves
the count/length implementation equivalent when expected names are unique.
The uniqueness premise is material: repeated expected names can otherwise let
an unrelated extra key through the old count-based test. The duplicate-profile
semantic mutation specifically exercises that case.

`DefinitionSchema` requires an actual empty-alias `ExprSchema` derivation and
an existential expression typed at the signature's singleton context, with
exact encoded data and alias identity. It does not call a reader or checker.
The explicit ordered nil/cons `DefinitionListSchema` preserves pairwise
signature/alias alignment. `DefinitionsSchema` adds distinct signature names
and exact definition keys. The three admission iff theorems cover arbitrary
finite profiles and actual `Lean.Json` values, rather than only the escape
fixture. Name order and uniqueness are separately proved.

`Field` intentionally shares `Json.getObjVal?`. This is a primitive boundary,
not a separately verified map-lookup implementation. Key enumeration and lookup
are not equated: the raw-map case has correct cached sizes and all expected
keys, yet a misplaced key is not found by lookup. Numeric version extraction
and object classification likewise retain their Lean primitives. No valid
ordering or cache-size invariant is silently imposed on arbitrary raw objects.

The new document relation has no high-level reader/checker-success predicate.
It records exact outer fields, admitted definitions, actual program JSON schema,
and normalized typed erasure. `document_sound` proves accepted documents satisfy
it. `escape_wrapper_equivalent` proves equality with the old fixed escape reader
for every JSON value, including refusal paths, not merely selected fixtures.
The fixture bridge transfers the existing CSS escape relation for every scalar
input. No new CSS semantics is inferred from generic document admission.

## Alias noncapture and the deliberately absent converse

The implementation closes the prior prototype's normalization premise:
`definition_data_normalized` derives it from actual definition acceptance via
alias-free schema normalization and typed encoding. `selected_alias_semantics`
starts with accepted definitions and actual first-match lookup, finds an aligned
declared singleton expression, and proves that decoding canonical
`nodeJson "use" [name]` at a matching head returns its singleton meaning under
any tail types and values. Fold binders preserve their local scalar/accumulator
prefix. The head marker alone is not treated as sufficient validation.

This is a conditional selected-use theorem over the canonical use-node shape.
It is not a whole-program alias-evaluation theorem, a theorem for every raw use
object layout, or a recursive-module model. Definition bodies remain alias-free;
forward and self references are refused. Trusted Lean callers supply profile
names and types; JSON cannot select the typing assumptions against which it
will be admitted. The CLI offers four concrete profiles, while the reader and
theorems quantify over arbitrary finite profiles and result types.

The independent `Boundary.lean` proves four additional facts. Besides admitted
definition-count alignment, it constructs a document whose constant natural
alias is used directly at an empty context. `DocumentSchema` holds for the
normalized constant program, but `readDocumentWith` rejects the missing scope
head. A final theorem refutes the general relation-to-reader converse. This
kernel-checked counterexample confirms why normalized erasure cannot replace
scoped typing. It is an advertised contract boundary, not an implementation
bug or a request to add the excluded general converse.

## Independent validation and harness review

The final independent replay passed 156 audits (108 canonical, seven prototype,
and 41 new declarations including 20 cases), 25 actual-file rows, eight precise
malformed-file refusals, four compiling semantic mutations, and three provenance
controls. `full-replay/report.json` is this review's actual fresh result.
`CHECK.json` binds it, the final 45 inputs, and the independent core receipt.

`core-check.py` authenticated 21 canonical module objects at standalone commit
`898fb45815c115362093116d81c09715ba94fcab` and two prior prototype objects at
Firefox commit `713bb6d320ece5371c107794b10180b91a82fef8`. Its fresh 21-module
closure compiled and all four independent boundary theorem audits passed.
Three inherited fixture/provenance Git objects were also independently
authenticated during finalization, for 26 total origin objects. These exact
core hashes match the final source manifest. Object contents were
authenticated; this review does not independently verify commit signatures.

The first review proof attempt used `decide` directly on the opaque ExactKeys
predicate and lacked a synthesized decision instance. It was corrected by
applying the proved Boolean reflection theorem. The failed attempt is retained
in `core-replay1`; the accepted result is `core-replay2`. No author source changed.

The frozen harness copies its complete source allowlist into a fresh temporary
tree and rejects source changes before/after execution. Its audit scanner
includes annotated declarations and compares the exact theorem roster with
strict printed axiom records, allowing only the established standard axioms.
Actual-file execution goes through `Runner` to `readDocumentWith` and executes
the returned program. The runner imports no generated escape fixture/reference.
Five files exercise four profiles, including executable-looking but inert
source-map content. Eight malformed-file controls require the exact document
refusal diagnostic.

Four implementation mutations remove duplicate-signature rejection, ignore a
declared result type, select the wrong definition name, or execute source-map
data. Each must compile before an unchanged theorem fails, and its unchanged
positive witness must fail with the exact false-proposition diagnostic. The
initial duplicate-guard mutation's extra diagnostic was rejected by the strict
checker, then replaced structurally; the implementation and acceptance rule
were not weakened. Three additional controls detect preserved-input drift.

Temporary compilation trees are removed. No canonical library, native source,
browser, Git index, or commit is changed by these replays.

## Scope of acceptance

The milestone is research-format value-level admission, compatibility and
selected-use meaning. It does not prove JSON text parsing, duplicate text-key
collapse, numeric lexical spelling, arbitrary source-map meaning, recursive
aliases, mechanical CSS prose derivation, new normative CSS feature coverage,
or Stylo/browser refinement. Finite CLI observations are kept separate from
the universal Lean theorems. The generic reader exists in this capsule; canonical
library integration remains a separate action.
