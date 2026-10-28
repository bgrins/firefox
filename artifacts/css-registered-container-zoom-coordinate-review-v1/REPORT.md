The per-container normalization rule is suitable for an isolated prototype, but remains an explicit coordinate-contract inference. It must operate per physical axis before merging lookup results, preserve viewport fallback as a different provenance, and avoid re-dividing by the querying element's zoom. This report accepts no fix and supplies no new normative WPT oracle.

The saved capture was independently authenticated and replayed through its sealed validator: all 42 cases, 94 initial observations and three mutation sequences are present, with no registration errors. RESULT reports complete preservation and no errors. Root observed session 21242 terminal 784d77 exit 0; this reviewer did not observe that OS exit directly or launch a browser. The profile is fresh/default, not the WPT preference configuration.

Selected actual values (CSSOM / rect width, CSS px):

| Parent local zoom | Target local zoom | Ordinary 100cqw | Registered custom CSSOM | Registered width / rect |
|---|---|---|---|---|
| 1 | 1 | 200 / 200 | 200 | 200 / 200 |
| 1 | 2 | 100 / 200 | 100 | 200 / 400 |
| 1 | 0.5 | 400 / 200 | 400 | 200 / 100 |
| 2 | 1 | 200 / 400 | 200 | 400 / 800 |
| 2 | 2 | 100 / 400 | 100 | 400 / 1600 |
| 2 | 0.5 | 400 / 400 | 400 | 400 / 400 |

Direct and ready-primary/unused-fallback registered paths agree in these rows. Target-zoom and parent-zoom cycles return to their initial measurements; changing container width 200→300→200 changes the captured values proportionately and then restores them. Literal and viewport controls show the existing registered-value scale discrepancy too. Percentage custom values remain `100%`; do not normalize percentages as length leaves.

Supported spec chain:

1. [Conditional container lengths](https://drafts.csswg.org/css-conditional-5/#container-lengths) delegates unit evaluation to size-query rules, selecting eligible ancestors per axis and small-viewport fallback when none exists. Its width/height features use the selected container's content box. This supports retaining the provenance of each physical dimension; one shared ancestor is not guaranteed.
2. [Viewport zoom](https://drafts.csswg.org/css-viewport/#zoom-property) defines effective zoom through ancestor multiplication and defines an element-relative unscaled length by division by that element's effective zoom. [CSSOM interaction](https://drafts.csswg.org/css-viewport/#zoom-om) requires unscaled non-percentage length values and scaled bounding rectangles.
3. [CSSWG issue 10268](https://github.com/w3c/csswg-drafts/issues/10268) resolves query-condition behavior; its linked WPT does not exercise cqw conversion. [Bug 1894104](https://bugzilla.mozilla.org/show_bug.cgi?id=1894104) explicitly tracks existing container-unit zoom handling. Ordinary Firefox cqw is not a normative calibration oracle.

Implementation inference: if lookup supplies a scaled physical content-box dimension D belonging to container C, canonical storage should receive D / effectiveZoom(C). Apply this independently for width and height while C is known, then perform unit arithmetic. The saved source's Gecko_GetQueryContainerSize returns frame content dimensions, while ContainerSizeQueryResult currently retains only optional Au width/height. A scale-aware lookup or provenance-bearing result is therefore necessary; dividing the eventual merged result by the target zoom loses information. The raw-Au interpretation is supported by these simple, transform-free measurements, not established for every layout mode by them.

Under that proposed contract, all core 100cqw registered values become 200px; consuming width remains 200 CSS px and its rect becomes 200 times the consumer's full effective zoom. For parent2/target2, that predicts width200/rect800, not the ordinary row's width100/rect400. This intentional difference must remain explicit pending spec/implementation adjudication, rather than being presented as ordinary parity.

Per-axis evidence: the outer horizontal size container has width640/height360 in its rect and effective zoom2; the inner vertical inline-size container has width200/height120 and effective zoom1 (ancestor2 × local0.5). Physical width comes from outer, height from inner. Proposed canonical physical dimensions are therefore width320 and height120. Dividing both by target effective zoom2 would incorrectly make height60. No-container fallback at target zoom2 captures ordinary cqw width683/rect1366, registered width1366/rect2732, and ordinary 100svw width1366/rect2732. Its canonical fallback is viewport1366, not viewport/targetZoom.

Logical-axis limitation: with a horizontal target under the vertical inner container, ordinary cqi uses the width path while registered cqi uses the height path; cqb is swapped. With a vertical target, the axis choices agree. The saved ContainerSizeQueryResult getters choose via context.builder.writing_mode. Early registered conversion observing inherited writing mode is a plausible source cause, not proven by this capture. Keep final writing-mode readiness and per-axis source zoom as separate obligations. This report does not settle the full logical-axis normative mapping or assert new cqi/cqb expected values; a normalization-only patch cannot silently claim those rows fixed. cqmin/cqmax must likewise normalize each selected physical source before min/max, once logical selection is adjudicated.

Verdict: INCONCLUSIVE for a fully normative cross-zoom container-unit algorithm. The supported clauses and observed scale separation justify the proposed per-source canonical experiment, but do not prescribe Gecko's internal representation. Missing work is an explicit cross-zoom unit interpretation plus correct logical-axis scheduling. Current source/cache handling, box variants, transforms, subframes and rounding require separate validation. Spec clauses were read directly from primary documents; no exhaustive automated graph trace is claimed (webspec-index unavailable in this environment).
