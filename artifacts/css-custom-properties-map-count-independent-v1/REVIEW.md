# Independent native count and iterator review

Verdict: the bounded native count repair and corrected-iterator composition are supported by source inspection and the final local paired evidence. Exact final packaging is verified below. Both formal components have separate accepted conditional reviews under iterator-formal/ and count-formal/; their joint bridge remains separate and open here.

## Final candidate and observations

Complete source pins: count-only `33723e4815ccf2cca81f5da7eec73514043fcca406a2cf71408ab31ea6195bdd`; combined `9ce38cf97e1ae93c134e80a1efc936f307d7311b8d7cf160331e9fa690ff5e9d`. The final native delta from the initial reviewed variants is rustfmt wrapping only. The final ten-case invalid-enumeration WPT pin is `371ab53b44e998961c5e02558a72c5eec4dd06389c5c0d8be21ebfc3ed8fb628`.

Reviewer-owned parsing of retained raw receipts establishes:

| Variant | PASS | FAIL | Harness OK |
|---|---:|---:|---:|
| Original | 30 | 11 | 7 |
| Count only | 38 | 3 | 7 |
| Count plus iterator | 41 | 0 | 7 |

All runs have the same 41 distinct subtests, exact expected per-file counts, seven distinct harnesses, and one suite_end after all test observations. Builds exit zero. Source, test, runner and binary pin associations agree with the build records; nonvariant pins are stable. These are shared-tree local runs, not isolated-upstream runtime. Count-only introduces no newly failing row in this set. Its three remaining failures are shadow/ancestor enumeration cases addressed by the iterator patch.

Both newly added tests fail original and pass count-only: removal/restoration of the last live value, and inherited/reset-map indexing through zero/one/both-live transitions. The live computed-style object is reused. Valid-empty controls retain exact name/count assertions and trim only the known-present empty value, avoiding an unrelated serialization oracle. Guaranteed-invalid assertions remain exact empty.

Formatting and scoped lint exit zero; three ignored-WPT ESLint warnings remain documented. A warnings-enabled ESLint invocation exits one because of those warnings, not errors. No performance-neutrality claim is made: get_index adds a filter; count insertion performs effective lookup before mutation.

## Source conclusion and limits

SOURCE-REVIEW.md gives the full count equation, all COW branches, raw iterator behavior, caller offsets and arithmetic bounds. None remains a masking tombstone; a valid empty value remains Some. The corrected loop skips a shadowed ancestor entry by continuing the outer traversal. With unique per-node keys, the combined stream contains exactly nearest-owner entries, and filtering Some gives live enumeration.

The label-only iterator must not be advertised as independently safe upstream. The old count can exceed the newly unique stream length, reaching the CSSOM offset subtraction with an index below inherited.len and producing a bare '--' diagnostic. The literal old-counterexample and historical four-variant raw matrix are retained, including the fact that its restoration row already failed original with a different diagnostic.

The native reasoning assumes coherent finite acyclic parent chains, IndexMap uniqueness/order and provider behavior, immutable shared parents, correct Arc copying/borrowing, successful normal completion, and machine headroom. The count decrement follows from old effective presence; increment and CSSOM u32 conversions/sums still need bounds. No allocation, compiler or whole-DOM refinement theorem is claimed.

CSSOM concatenates counts/indexing from inherited and non-inherited maps while get_for_cssom prefers inherited. Whole-computed-map uniqueness therefore requires disjoint live name domains and consistent registration routing across updates. Supplied registration.inherits() controls map_mut/get; no opposite-map cleanup is established here. The new mixed-map test does not prove arbitrary re-registration/cache lifetime coherence.

Native PartialEq may identify only a payload projection: VariableValue equality compares CSS text, whereas other metadata is checked separately elsewhere. Count invariant preservation does not need full payload equality. A formal requested-value history theorem must explicitly admit the payload quotient and observer compatibility; it cannot infer full metadata identity from the skip branch.

## Evidence and status

The source, primary specification snapshots, exact input variants, old counterexample, 39-case history and final 41-case receipts are retained. Independently written review_matrix39.py and review_matrix41.py verify the raw identities and provenance associations. literal_witness.py checks its finite source-shaped witness against an independent effective-map reference. None of these is presented as a universal native proof.

Main-stack order is count repair then iterator repair. An upstream standalone iterator alternative needs the shared count/filter support and relevant tests, explicitly identified in its inventory. The root six-check packaging receipt binds branch ba62cc3f59ea7f1cfd8bcdecbdb067be0d224476 and upstream 976279105b2e78b8666a959eb3f25c9176cefaf8. The count patch has two files; the subsequent iterator patch adds a native delta and two WPTs (three files); the standalone iterator alternative has four files including the necessary count support and all three WPTs. The reviewer independently applied and reversed all three paths with patch --fuzz=0 in artifact-only scratch, checking every final byte against the authenticated native/WPT snapshots. Root Git base receipts are inspected evidence, not reviewer Git execution; no isolated upstream runtime is claimed. No native files, WPTs, Git state, browser, or Firefox build were changed by this reviewer.
