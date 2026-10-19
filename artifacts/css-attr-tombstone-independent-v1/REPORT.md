# Typed-attribute tombstone repair: independent review

## Static verdict

No blocking defect found in the reviewed presence guard or final ten-case WPT. The guard is a narrow correction to lazy discovery: a stored invalid entry must not be treated as an attribute that has never been read. Native build, final WPT baseline/candidate pairing, formatting and standalone patch isolation belong to root's separate gates. No compiler, browser, Git action or production edit was performed by this review.

The root-communicated final native patch is `00695f5b4c04ada6624521bed29c942cab0b4e585db45beeb338ef7b64973361`. Final WPT is `e913d5358d8eee8bf4af067ac4f3317ccc59151177aa70b31311e304e0b23ee3`. Complete final source copies and exact original namespace-v3 files are retained. The historical longer probe is retained under `baseline/attr-cycle-repeated-reference.html`; both the initial captured candidate WPT and `final-input` contain the final concise bytes. These are not interchangeable runtime identities.

## Independent normative oracle

The retained primary CSS Values 5 snapshot was retrieved HTTP200 on 2026-10-19 and its digest and anchors are checked. In `attr-substitution`, a typed attribute's contents undergo arbitrary-function substitution under the attribute context before requested-syntax parsing. The guarding algorithm marks repeated contexts in the cycle invalid. A failed attribute result then selects the outer attr occurrence's own fallback. A universal `type(*)` syntax does not bypass the preceding substitution step.

For `x="attr(x type(*))"`, the cyclic attribute context is invalid; the outer `--out` context is not itself in that self-cycle. Thus two sibling references with fallbacks13px and37px produce `--out:13px 37px`, not raw attr tokens. `x="var(--missing)"` similarly fails substitution. A two-attribute cycle invalidates both attributes. A distinct y which references cyclic x also fails, without requiring y to be a member of x's SCC. Literal19px is valid for both occurrences. A constrained `<length>` request must also choose the fallbacks; its existing parser can mask the resurrection by rejecting leaked tokens, which makes it a useful negative control.

The computed custom-property serialization and absolute two-value margins provide independent observables. No prefixed chained attribute is required, so the known bug2021110 namespace-parser limitation is separate. This review makes no novelty claim and does not certify the whole current substitution algorithm.

## Actual baseline evidence

The captured `css-attr-reload-browser-v1/baseline-v1` raw JSONL matches every status in its receipt: 7 PASS,4 FAIL,1 harness OK and one suite_end, exit1, with equal before/after pins. Failing cases are repeat-cycle, repeat-invalid, repeat-two-node-cycle and same-cycle-value-different-names. Actual custom-property outputs contain raw tokens in BOTH positions: respectively repeated `attr(x type(*))`, `var(--missing)`, `attr(y type(*))`, and `attr(x type(*))`.

The causal sequence is traversal before substitution: first discovery loads and invalidates the attribute; later discovery reloads raw data because get_attr flattens both missing and invalid slots to None; traversal finds the existing index and does not recompute that raw value. Final outer substitution then reads the resurrected map for both sibling occurrences. The baseline assertions fail at the custom-property check, so this receipt alone does not report the later margin assertions for those failing cases. It is not evidence of a partially substituted first sibling.

The producer's frozen trace correction is retained: for root index0 and completed x index1, visit_link takes the larger-index lowlink branch; it does not consult the finished marker there. An earlier finished child can instead take the no-active-marker path. Neither path re-resolves the loaded value. The final concise WPT has ten cases and different bytes, so root's final baseline must be used for its exact paired result; the old11-status receipt is historical supporting evidence only.

## Guard and map-write audit

`contains_attr(name, namespace)` first selects the resolved namespace bucket, then asks `OwnMap::contains_key(name)`. It returns true for both `Some(value)` and a stored `None`; a missing bucket or missing local key returns false. Checking only bucket existence would be incorrect; this implementation checks the complete key. `get_attr` remains unchanged for actual value consumption and still returns None for invalid entries.

| Source transition | Storage effect | Consequence for the new guard |
|---|---|---|
| typed eager preload in update_attributes_map | first successful admitted query inserts Some(raw value) | Discovery uses it; it does not reload an existing raw value |
| visit_value_references lazy discovery | absent successful query inserts Some(raw value) | Only this insertion site is guarded by the new presence predicate |
| get_attr_value_for_cycle_resolution failure | no insertion | Genuine absence, missing DOM attrs and initial parse failure remain retryable |
| Context::handle_loop → remove_attr | inserts None at the qualified key | Cycle invalidation is preserved |
| failed substitute_references_if_needed_and_apply for Attr | inserts None at the qualified key | Noncycle substitution invalidation is also preserved |
| successful attribute apply | inserts newly substituted Some(value) | Existing resolved value is preserved |
| geckolib arbitrary-expression helper | independent local map with qualified raw insertions | No shared traversal/index reuse; unchanged |

All these sites retain the same resolved namespace. Unknown namespaces still take the existing rejection/fallback path before the guard, and a valid null namespace remains a concrete key. The helper does not clone atoms, mutate entries, allocate, change graph indexes, or alter fallback selection itself. Successful writes and explicit invalidation remain the existing functions; this is not a global prohibition on replacing values.

## Traversal resets and lifetime

`Context::reset` clears count, every index map, VarInfo and stack between independent roots. It deliberately does not clear `computed_context.builder.substitution_functions`. A completed invalid result should remain invalid for later roots in the same computation. Keeping the tombstone prevents redundant raw reload after the reset as well; the independent-declarations control checks observable compatibility with the existing fresh-root behavior.

The ordinary cascade initializes attributes empty in `init_custom_properties`; keyframe custom-property builder construction does the same. A StyleBuilder constructed from existing style copies custom properties but supplies None attributes. Thus this patch does not persist invalid attribute entries across new style calculations or keyframe construction. The visited cascade clones the already-computed unvisited substitution state; retaining its invalid entries is consistent with that existing sharing design. No new DOM lifetime or script reentry behavior is introduced by a pure membership check.

The source audit establishes these specific write/reset paths, not a universal theorem that every possible terminal value is semantically correct. Contextual registered/prioritary dependencies, fallback eligibility and recursive preload have separate known obligations. The fix must not be credited with closing them. Existing namespace-key and index models remain conditional on native map/evaluator admission; no Lean replay or new proof is claimed here.

## Final WPT review and necessary gates

The concise test contains ten ordinary synchronous testharness tests, creates a fresh div for each, uses null-namespace setAttribute, sets --out and margins inline, appends before reading computed style, and registers cleanup. There is no optional support exit or prediction metadata. Failure to parse/support the feature cannot silently pass the expected custom-property and margin assertions. No font, timing or platform-dependent geometry assumption is involved.

Its cases preserve the original self-cycle/repeated/missing-variable/literal/distinct-cycle/two-node/shared-dependency/separate-declaration controls. Whitespace normalization is appropriate for these simple token strings and cannot hide leaked attr/var functions. Both custom-property tokens and physical margins are asserted. The final WPT does not directly test namespace aliasing, dynamic new-style invalidation, or a provider that initially fails and later succeeds; the source guard truth table preserves absence retries, while root's existing namespace/cycle regressions and final paired browser gate remain relevant. No matrix expansion is necessary solely to re-test unrelated container-query or InspectorUtils behavior.

Suggested acceptance boundary: exact final WPT paired baseline/candidate; existing namespace and attr-cycle regressions; native build; format/lint; standalone isolation. The baseline source includes earlier namespace and local cascade work, so this review is not a claim that the two-file delta applies independently to an unrelated upstream base.

## Replay and limits

Authenticate the communicated manifest before running `check.py --manifest-sha DIGEST`. The standard-library checker authenticates all files before interpreting inputs, verifies exact minimal native transformations and patch reconstruction, checks the helper/body correspondence and retained reset operations, matches the historical baseline raw statuses/pins, verifies spec anchors and final WPT identity, and rejects a deliberate source modification. It does not execute Rust or JavaScript and is not a compiler correctness or CSS conformance proof.

## Final baseline and producer seal addendum

Root subsequently completed the exact final ten-case WPT baseline-v2:4 FAIL,6 PASS,1 harness OK. The four failing names correspond to the same repeated/self-cycle, missing-variable, two-attribute-cycle and shared-cyclic-dependency witnesses; the six controls pass. The same run reports the21-case namespace test all PASS, existing attr-cycle37 PASS, and two namespace reftests PASS. The copied raw JSONL exactly matches the receipt, all before/after pins match, and the final WPT pin is the reviewed e913… bytes. This establishes the final-file baseline; candidate runtime remains root's pending gate.

The producer has now sealed its package. `producer-seal` retains the seal/input map/review, and `FINAL-ADMISSION.json` records its digest alongside the independently communicated root patch/WPT identities. Exact native originals/candidates still match the initial captured sources. No producer executable was imported or run. The source-only independent checker below authenticates and rederives its own narrow observations.

Skipping a redundant reload also skips its redundant AttributeTracker query. The original successful load that created the subsequently invalidated slot already observed the attribute; genuine failed lookup paths remain unchanged. This local observation is not a universal event-trace or DOM invalidation proof.

Stack context from root: the namespace repair is already committed. The occupancy-versus-value distinction also applies to the old name-only map, where the analogous helper would use direct contains_key(name); this exact reviewed patch deliberately uses the current namespace-aware APIs. No separate backport was authored or claimed tested. Root reports build41686 exit0; final candidate WPT and lint are running. Those reports do not alter this frozen source review's independent execution scope.

The first development checker rejected an incorrect file association: the candidate WPT had already been simplified when copied, so it could not authenticate baseline-v1's longer test. The exact still-retained original test was then copied from the test tree after matching baseline-v1's recorded2dec… hash; the checker now authenticates that separate historical file. No receipt was relabeled or silently substituted. `DEVELOPMENT-CHECK-CORRECTION.json` preserves this packaging correction.
