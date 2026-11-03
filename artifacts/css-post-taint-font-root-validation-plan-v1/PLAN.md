# Post-taint font and root validation plan

This is a future two-build plan, approved in root steering after the isolated root-self outcome. It creates no driver, authority receipt or live operation. Start only after the two actual taint native commits, their signed research predecessors and exact current source/epoch admission exist. Current disabled font/root publishers deliberately admit only artifact-only descendants of tested e86; do not widen that condition using this plan.

1. Build the actual taints+font-invalidation intermediate image, leaving root-identity code unchanged. Run the existing reparse4 + fallback28 + controls47 + composition3 + font_units14 lanes: **96 callbacks/eight endings must pass**. On the same image also run root_identity14 as an observation, preserving its complete raw stream and signatures. Its intermediate PASS/FAIL counts are **pending**, not assumed to equal any older baseline. Unexpected differences require investigation. This supplies the immediate predecessor observation without another original build.
2. After admitting/publishing the font fix against its actual predecessor, build the actual cumulative taints+font+root image. Run the union of those same lanes: **110 callbacks/nine endings must pass**. Preserve all prior-PASS and ending signatures and identify exactly which root observations change. Do not blindly require seven differences if the actual intermediate observation differs; resolve that first. Independent restoration and normal research-before-native publication remain required at each stage.

The shared47 controls run once per image, not once per inherited package. Reuse the existing build/WPT/restoration lifecycle and exact resources below. Two separately validated images preserve independently landable commits; a passing final combination alone cannot establish the intermediate font commit.

## Existing runnable lanes and exact resources

The pinned policies contain the full callback rosters, all support resource hashes, prefs and staging metadata. Resource paths below are unchanged; no new oracle is introduced.

[css-explicit-taint-combined-native-candidate-browser-v1/POLICY.json](../css-explicit-taint-combined-native-candidate-browser-v1/POLICY.json), SHA256 `1b86db659d814346605d577a5b51133fce30fe81939820d82982be2b75a47673`; FILES `e84f0d66f97085c5cff65b5ac54f370149fd60b62cf91051872ad940fda01273`.

- `reparse`: 4 callbacks/1 endings.
  - [/css/css-values/attr-taint-registration-transition.html](../css-explicit-attribute-taint-typed-reparse-fix-v1/tests/css/css-values/attr-taint-registration-transition.html)
- `fallback`: 28 callbacks/1 endings.
  - [/css/css-values/attr-fallback-taint.html](../css-attr-own-fallback-fix-v2/tests/css/css-values/attr-fallback-taint.html)
- `controls`: 47 callbacks/4 endings.
  - [/css/css-values/animation-base-equal-payload-taint.html](../css-explicit-attribute-taint-existing-controls-v1/tests/css/css-values/animation-base-equal-payload-taint.html)
  - [/css/css-values/animation-csswide-equal-payload-taint.html](../css-explicit-attribute-taint-existing-controls-v1/tests/css/css-values/animation-csswide-equal-payload-taint.html)
  - [/css/css-values/map-taint-equality.html](../css-explicit-attribute-taint-existing-controls-v1/tests/css/css-values/map-taint-equality.html)
  - [/css/css-values/registered-number-interpolation-attr-taint.html](../css-explicit-attribute-taint-existing-controls-v1/tests/css/css-values/registered-number-interpolation-attr-taint.html)
- `composition`: 3 callbacks/1 endings.
  - [/css/css-values/attr-fallback-taint-registration-transition.html](../css-explicit-taint-fallback-composition-review-v1/tests/css/css-values/attr-fallback-taint-registration-transition.html)

[css-keyframe-font-unit-candidate-browser-v3/POLICY.json](../css-keyframe-font-unit-candidate-browser-v3/POLICY.json), SHA256 `5aff4c69d38a2bc402f8f3eeeb6b9fd753cf3ffc920d0026dd48b177c6e7704a`; FILES `b836932924b5b203bec545c52f3679d1127de39e020e56c05edd7e7bb04a6f42`.

- `font_units`: 14 callbacks/1 endings.
  - [/web-animations/animation-model/keyframe-effects/root-font-unit-invalidation.html](../css-keyframe-font-unit-dependency-fix-v1/tests/web-animations/animation-model/keyframe-effects/root-font-unit-invalidation.html)

[css-root-self-animation-candidate-browser-v2/POLICY.json](../css-root-self-animation-candidate-browser-v2/POLICY.json), SHA256 `5bfa9e3511650f77b52ff51aa3ec4598df6858e9347585d19b1249f35d76507a`; FILES `af81c30fb718433e1dfb557aedc74928760ba1a7dd7aa3b225842f600f3bd7ca`.

- `root_identity`: 14 callbacks/1 endings.
  - [/web-animations/animation-model/keyframe-effects/root-font-self-reference.html](../css-root-self-animation-context-fix-v3/tests/web-animations/animation-model/keyframe-effects/root-font-self-reference.html)

## Existing validated evidence and interaction limits

- [css-explicit-taint-combined-outcome-v1/RESULT.json](../css-explicit-taint-combined-outcome-v1/RESULT.json): 82 PASS, 13 improvements, 69 preserved PASS and 7 endings. FILES `a4d47cbc6255be77232b9384154837e8e5a1311f5e8d847a4322979204bbbee2`.
- [css-keyframe-font-unit-native61-outcome-v2/RESULT.json](../css-keyframe-font-unit-native61-outcome-v2/RESULT.json): 61 PASS, 12 improvements, 49 preserved PASS and 5 endings. FILES `b00461302b589df509722c0a834ea8ed9ef46de4006c561996f78301378a681c`.
- [css-root-self-animation-native61-outcome-v3/RESULT.json](../css-root-self-animation-native61-outcome-v3/RESULT.json): 61 PASS, 7 improvements, 54 preserved PASS and 5 endings. FILES `246937aada70fc5cf2070a6787e065035a4c44a4ce3f88d490e0ce702d3ffc99`.

Those actual results establish isolated behaviors, not the unrun cumulative state. Source applicability and disjoint paths alone do not prove interaction safety. The union exercises registration/taint propagation, equal-payload interpolation, selected fallback, root/child/pseudo unit invalidation, CSS-generated keyframes and substituted root keyframes in each actual binary. It does not cover every root-target attr-tainted keyframe combination.

If further focused interaction coverage is needed, adapt the existing registration-transition test to a root/root-host-pseudo target using its existing taint oracle, and calibrate the variant before assigning a portable expectation. No such fixture, expected result or additional callback count is included here. Preserve ordinary/animation, root/pseudo and font-metric/taint distinctions; do not claim blanket compositional correctness.

Exact lane/resource and completed outcome metadata were read/authenticated read-only in cf19bd/63b23c. The plan assumes no future commit hash, successful signing, current capture, candidate outcome or new accepted fix.
