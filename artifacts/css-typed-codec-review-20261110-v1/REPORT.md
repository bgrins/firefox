# Independent typed codec acceptance review

Verdict: accept the bounded typed-data codec and concrete JSON fixture artifact.
No source blocker remains. The reviewed 28-input manifest has SHA-256
`5f4a130655199d333171c931127d261fdfc0859ce491d620782fcbc0bde0ce29`.
`REVIEWED.json` binds every reviewed source byte. No canonical library, Firefox
native source, browser, build tree, Git index or commit was changed by this review.

## What is established

The generic roundtrip laws quantify over all typed variable/expression/statement
trees, contexts and result types. Context inference checks both a variable's
index and the type stored at that index. Binder extensions are correct for let,
read, bounded scan and fold. Equal-type transport is guarded by proved type
equality; no type coercion oracle or executable source payload is used.

`checkExpr_faithful` and `checkStmt_faithful` establish exact accepted-result
erasure against `normalizeExpr`/`normalizeStmt`. Those normalizers remove only
alias scope wrappers. They preserve opcode, literal, variable index, child
order and scan budget. This is stronger than recovery only on encoded images,
but is a theorem about the constructor-data layer relative to the reviewed
encoder/normalizer definitions. It does not establish arbitrary JSON or CSS
semantics. The same-type-opcode and index controls distinguish these claims
from type safety alone.

The scope-head guard is checked before a wrapper is erased. During review I
flagged that canonical roundtrips alone would not detect removal of that guard;
the author added `scope_mismatch_rejected`, a universal rejection theorem, and
the corresponding mutant now fails it and a false semantic witness. Fixed
alias bodies are first checked without aliases in their singleton context.
Reuse under a matching head rechecks the unchanged tree in the actual context;
references to extra ambient tail variables cannot pass singleton validation.
No general alias-weakening theorem is claimed.

JSON dispatch is explicit and data-only. Exact node fields, operator arity,
primitive kinds and scalar literal bounds are checked. Alias definitions cannot
invoke other aliases. `source_map` is an object containing inert provenance;
it is not executed or interpreted as declarations. The decoder contains no
reference-parser call, arbitrary Lean function field, eval of supplied text,
reflection oracle, or dynamically chosen import.

## The emitter is actually bypassed

`Runner.lean` imports only JsonCodec, reads the actual JSON file, calls decodeText,
and executes the returned typed program. Its transitive runtime imports do not
contain GeneratedFirstOrder, FOBridge or the Python AST emitter. The separate
RuntimeCheck imports the reference solely to compare canonical encoded trees;
it still executes the decoded value. Both paths produced the same 13 expected
rows in the independent clean replay.

The concrete `fixture_decodes` theorem is checked by kernel reflexivity over
an exact-byte `json%` fixture quotation and equals the prior escapeTree. The
execution/relation theorems then connect that fixture to the existing escape
relation. The quotation and runtime Json.parse are separate interfaces. The
file runner's erased-tree comparison is a finite observed check of their
agreement on this fixture, not a universal JSON-parser theorem.

## Trust and scope boundaries retained

The universal accepted-erasure theorem begins at DataExpr/DataStmt, after the
JSON-to-constructor adapter. No universal JSON schema correspondence or typed
AST JSON serialization roundtrip is proved. Lean's Json.parse, its object map,
number representation, quotation macro, file acquisition and external text
linkage remain trusted or concretely observed boundaries.

Independent parser observations confirm duplicate text keys are collapsed with
last occurrence winning. Field counting cannot recover them afterward. Numeric
admission uses parsed nonnegative mantissa/zero-exponent representation: 1e1
and 1.0e1 are accepted as 10; 1.0 and 10e-1 are rejected; signed zero is accepted.
No lexical compatibility with the old Python emitter is claimed. The preserved
fixture avoids these ambiguous spellings and duplicates.

The source recognizer, prose-to-AST choice, shared arithmetic/character
primitives and interpretation of the old reference relation remain reviewed
assumptions. Clause hashes authenticate provenance, not normative semantics.
CSS caller readiness still requires normalized validated escape input and an
already-consumed backslash. This is not new CSS feature coverage, a fresh-draft
claim, a DOMString or byte decoder, native cursor refinement, browser result,
memory-safety proof, resource bound or performance measurement.

## Validation and provenance

Independent source-only replay rebuilt the 19-module closure in fresh temporary
storage: 115 exact theorem audits using only the allowed standard axioms,
13 actual-file rows for each runner,13 parser observations, and three additional
malformed actual-file documents rejected by the standalone runner. All 19 Lean
sources and runtime inputs match the final frozen manifest. The 19 modules
include reference proofs; 46 declarations are new, including 28 boundary cases.
The temporary source/object directory was removed.

The reviewer also authenticated 10 prior Git objects independently. The author's
final harness was inspected and its seven semantic-control receipts were
hash-checked: each witness first passes on baseline, the mutated implementation
compiles, an unchanged theorem fails, and Lean explicitly determines the same
concrete witness proposition false. Three provenance controls reject IR,
clause-record and fixture-quotation drift. These 10 author controls were not
independently rerun by this review; root may replay the complete frozen bundle.

`replay4/REPORT.json` is the successful independent replay receipt. Earlier
review-local attempts failed in the review wrapper's toolchain-import and mutual
namespace discovery, before acceptance; their logs are retained. They are not
codec defects or counted negative controls. Final source checks and audit sets
are bound in CHECK.json. The author's MAPPING.md accurately limits its claims.
