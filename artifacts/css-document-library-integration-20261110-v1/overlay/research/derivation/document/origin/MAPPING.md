# Document and alias mapping

This is the research IR document format, not a CSS normative grammar. The new
reader keeps schema version 1 and fields `schema`, `definitions`, `program`, and
`source_map`. A trusted Lean caller supplies a finite signature list and program
result type. JSON cannot select its own typing assumptions. Definitions are flat,
alias-free expressions; forward references and cycles are refused. Source maps
are object-valued inert metadata. No new CSS feature coverage is claimed.

`ExactKeys` is an independent key-list permutation relation, proved equivalent
to the existing Boolean field check for unique expected names. `DefinitionSchema`
uses the actual empty-alias JSON expression schema and an existential typed
expression with exact encoding; it calls no decoder or checker. The ordered
nil/cons `DefinitionListSchema` is the explicit pairwise list relation.
`definitions_spec` is a full soundness/completeness iff for arbitrary finite
profiles and raw JSON values, including refusal of duplicate signature names.

`Field` deliberately uses the existing `Json.getObjVal?` primitive. Raw object
key enumeration and ordered-map lookup are distinct operations. The relation
requires both exact keys and successful named lookup and never assumes every
raw Json object has valid ordering or cached sizes. One case supplies correct
cached sizes but a misplaced key: enumeration has the expected keys while lookup
fails. Primitive map lookup correctness and JSON text parsing are shared Lean
library boundaries; they are not independently verified here.

`document_sound` gives the exact outer fields, admitted definitions, actual
program JSON schema, and normalized typed erasure. It does not prove a converse
for arbitrary alias-using programs. Removing scope wrappers during normalization
loses information needed by that converse. `escape_wrapper_equivalent` equates
all JSON values, successes and refusals, with the prior fixed escape reader.
The fixture bridge reuses the existing escape relation for every scalar input.

`definition_data_normalized` connects actual readDefinition acceptance to the
normalized-data premise from the prior prototype. `selected_alias_semantics`
starts with actual readDefinitions acceptance and actual first-match lookup,
finds the aligned declared singleton expression, and proves actual JSON `use`
decoding of canonical `nodeJson "use" [name]` returns its singleton meaning under
arbitrary ambient context tails. This is not a whole-program alias semantics
theorem or a theorem over every raw-object representation of a use node.
The proof retains fold binders and never assumes matching head type alone prevents
capture. Generic signature name alignment and admitted-name uniqueness are proved.

The CLI imports only DocumentModel, uses explicit caller-selected profiles,
parses the actual input file, and executes readDocumentWith's returned program.
It has no generated escape reference in its import closure. Actual-file results
are finite observations; the JSON text parser, duplicate text-key collapse,
numeric lexical spelling, and serialization are outside the value theorems.

All 21 canonical modules match signed 898fb45815c115362093116d81c09715ba94fcab.
The two prototype modules match signed Firefox artifact commit
713bb6d320ece5371c107794b10180b91a82fef8. ORIGINS.json records direct read-only Git
object authentication. The inherited CLAUSES.json keeps the existing escaped
code-point spec excerpts and URLs; this artifact adds no new normative CSS
interpretation. The specification-to-IR interpretation remains manually reviewed.
