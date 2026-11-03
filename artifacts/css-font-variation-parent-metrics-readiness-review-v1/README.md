# Variation parent-metric candidate: bounded readiness review

GO for isolated four-role native typechecking and diagnostic browser validation. No concrete source blocker was found in sealed candidate dbc24d6e. NO-GO for publication or an all-font/all-axis correctness claim: no candidate native result exists, and the existing animation tests combine conversion with separately demonstrated invalidation behavior. This review changes no source, test, lifecycle or live state.

## Normative boundary

Question: does a horizontal non-root variation `wdth` number computed from `calc(1em / 1px)` use the parent's size? Assume admitted arithmetic, a real parent, differing parent/child sizes and no orientation or form-control complication.

1. [Fonts4 variation settings](https://drafts.csswg.org/css-fonts-4/#font-variation-settings-def) accepts a tag/number; [Values4 type checking](https://drafts.csswg.org/css-values-4/#calc-type-checking) cancels equal length dimensions through division.
2. [Fonts4 font-relative interaction](https://drafts.csswg.org/css-fonts-4/#font-relative) includes reset-only font shorthand members. Variation settings belongs to that category.
3. [Values4 font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths) selects “the computed metrics of the parent element” when the property affects the referenced element's font.

**Verdict: REACHED** for this scoped current-draft wdth/em expectation. The primary drafts read this turn remain Values4 August24 and Fonts4 October26. This is a grammar/definition chain, not an event-algorithm trace. spec-index query/exists failed on a read-only cache; primary sections were read directly, with no claimed successful graph/anchor check.

| Context | Required reference |
| --- | --- |
| Non-root variation em/ex/cap/ch/ic/lh | Parent font metrics; lh uses parent line height |
| Non-root variation rem/rex/rcap/rch/ric/rlh | Actual root metrics, not local parent |
| Variation on the root itself, local or root units | Initial font/line-height metrics |
| Ordinary non-font numeric property | Its ordinary current/root rules remain |
| line-height property | lh and root-self rlh have the special parent/initial rule; em and root rem retain their ordinary references |

This table follows the same [Values4 section](https://drafts.csswg.org/css-values-4/#font-relative-lengths). It does not identify a font metric with shaped text geometry. The current Fonts4 list also reaches feature settings, but [issue14306](https://github.com/w3c/csswg-drafts/issues/14306) remains open on shaping-only membership. Leaving FeatureTagValue unchanged is deliberate scope, not proof the draft excludes it. No feature-policy fix should be bundled.

## Actual source and effects

The four roles are computed/mod.rs, computed/font.rs, generics/font.rs and specified/calc.rs. Both archived generated cascade and AnimationValue::from_declaration call ToComputedValue. The manual VariationValue implementation supplies one shared scoped inherited-base boundary. Its Drop guard restores nested/prior state; all five Context constructors default to CurrentStyle. The generic Number default is not globally rebased.

FontSettings still converts every item before deduplication, so losing duplicate entries retain their conversion effects. Tag/reverse conversion, selected Context/element/scope, random/tree-counting and non-font leaves remain intact. The @font-face parser separately rejects unresolved contextual settings; the shared generic type does not authorize arbitrary future descriptor conversion.

NoCalcLength is unchanged. Its dispatch retains inheritance zoom, root-device paths, viewport/container branches, registered-value treatment and dependency flags. query_font_metrics selects parent font/inherited writing mode under the new base and records inherited-metric dependencies. This is source correspondence, not proof that every ancestor-family/weight/variation/font-load mutation triggers the complete needed recascade.

Axis uncertainty is real and localized: ch metrics query parent writing mode, but its missing-metric fallback still reads consumer upright state; inherited normal-lh receives consumer writing mode. ic chooses an axis-sensitive metric too. Existing axis review1bac0c4b gives no unconditional cross-axis oracle. Keep these branches unchanged and the excluded twelve orientation proposals out of conformance gating. Minimum-font prefs, zoom, font-load/family changes and missing-metric selection remain additional coverage obligations; ratio-compatible observations alone do not prove a fallback branch.

## Baseline and next native step

Authenticated original36 is30FAIL6PASS/threeOK: ordinary local6FAIL/root-relative6PASS, ordinary root-self12FAIL, animation12FAIL. The six animation local cases first fail at initial conversion; six r* cases first fail at root-only mutation. Raw WPT exposes the first failing assertion, not every later collected row. Separate root-unit diagnostics establish the persistent-effect invalidation problem; do not relabel all30 failures as one conversion defect.

Important fixture distinction: variationRootCase performs ordinary root declarations, not root animations. The separate glue root-identity fix is not a prerequisite for these twelve existing callbacks. Future root-animation coverage would need actual target classification, but it is not silently part of this suite.

1. Reuse the existing four-role Cargo-check plan against freshly authenticated current preimages/inodes, keeping the candidate bytes unchanged. Require fresh style/geckoservo success; the saved6positive/5mutant extraction used support doubles and cannot replace this step.
2. If integration passes, one isolated four-file binaries build can run the existing unchanged36 suite. Assess ordinary12 and ordinary-root12 as direct conversion targets, retaining all twelve units, parent/child/root mutations and controls. Run animation12 diagnostically on the same image, preserving exact failures and first/settled scope. Do not impose36PASS as the standalone conversion acceptance gate or add expected-failure metadata.
3. A publishable animation WPT must separate fresh endpoint conversion from persistent-effect invalidation, or explicitly bind the independently validated font-unit admission repair as a predecessor. Do not assume that composition passes. Keep original36 intact as diagnostic evidence; no new fixture or composition is created here.

No second old baseline run is needed solely for this read. If the tested native predecessor changes, authenticate/rebase explicitly and compare the actual source set; archived e86 is historical e86. No new bug count, native correctness claim, or generic framework follows from this review.
