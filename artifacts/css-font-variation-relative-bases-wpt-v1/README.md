# Variation-settings numeric font-relative bases: focused WPT preparation

Prepared standalone WPT coverage, not executed in a browser. This package tests only `font-variation-settings`, with the metric-affecting `wdth` tag. It does not change any native source or add feature-settings policy to the proposed repair. The files are tentative because the current-draft font-affecting definition and interoperability remain under active discussion; the narrower width-axis reproduction is separately established by root's saved runs.

## Established evidence versus new coverage

The sealed parent-metrics probe and two immutable runtime packages are references, not results for these new tests. Root recorded 66 stable calibrated observations on archived native e86 and installed Firefox158. The wdth/em discriminator gave child 40/40/60 for parent/child 20/40, 30/40, 30/60, while the current-draft rule requires parent 20/30/30. Those observations motivate this WPT. They do not establish any new animation, root, line-height or vertical result. This artifact did not launch a browser or independently rerun those saved executions.

Three pages provide 36 conformance callbacks. Twelve additional orientation cases remain an explicit unrun proposal outside the staged tests:

| Page | Callbacks | Scope |
| --- | ---: | --- |
| font-variation-relative-bases.tentative.html | 12 | Twelve local/root units in ordinary declarations with fixed horizontal writing mode and explicit line height |
| font-variation-relative-animation.tentative.html | 12 | The same twelve units through paused Web Animations keyframes with distinct 1-unit and 3-unit endpoints sampled at 50% |
| font-variation-root-relative-bases.tentative.html | 12 | Every local/root unit on the root element itself, compared to initial-font/line-height metrics captured before changing root family/size/line-height |

## Expected bases

The twelve units are em/ex/ch/cap/ic/lh and rem/rex/rch/rcap/ric/rlh. Current Values4 says that a font-affecting property uses parent metrics when the relative length refers to that same element; with no parent, initial font and line-height metrics are used. A non-root child's r* units still refer to the root, so they must retain actual root semantics, not blindly become parent-relative. Root self-reference instead reaches the initial-metrics rule.

`webspec-index query` of Values4#font-relative-lengths succeeded in tool 77db14 and matched the previously saved source hash 1c4ce22ba37b4ced4cb6360ea3d4657eb0f52ba7406d99b28f0f1a2e574ed34d. The first sandboxed query 35e4b8 failed because its normal cache update was read-only; no specification text was manually altered. The sealed SPEC-TRACE retains the Fonts4 category, variation grammar, dimensional-division chain and issue history. This package does not extrapolate a feature-settings/shaping policy resolution from that text.

Ordinary non-font width declarations measure 100 units divided by 100 in a reference that inherits the parent or root style. Font-family is monospace; no particular platform glyph width is asserted. The parent reference remains `font-variation-settings:normal`, as does the separate child-metric calibration. The target's wdth value must not change the parent reference. Root self-reference starts with `font:initial;line-height:initial`, records the relevant initial metric, then changes root to monospace 40/60px with 79/99px line-height. This supplies environmental initial metrics instead of assuming 16px or a particular normal line-height.

## Controls and mutations

Each ordinary/keyframe callback retains all four phases before result assertions: initial parent 20/child 40/root 23, parent-only 30/40/23, child-only 30/60/23, root-only 30/60/31. Explicit parent, child and root line heights mutate independently. Both the first target read after mutation and a fonts-ready/two-frame settled read are retained. Every row includes raw serialization, declaration/CSS.supports admission, literal 20 and calc(20px/1px) controls, actual font sizes/line heights, and an unrelated opacity calc(1em/100px) control that must continue to use the child's size. Rejected arithmetic or unparseable settings cannot masquerade as a successful parent-base result.

For keyframes the same animation survives the mutations. Two distinct endpoint expressions interpolate to twice the expected base at 50%; actual progress, paused state and keyframe count are asserted. This reaches the animation conversion contract, rather than only changing a static declaration and calling it an animation test. Saved source shows ordinary generated cascade and AnimationValue::from_declaration are distinct conversion entries. ANIMATION-CONTEXT-SPEC.log and ANIMATION-SPEC.log retain the actual Web Animations algorithms: compute keyframe properties in the target dependency context before calculating the effect value (source hash d08d2fe8cdb2b15b9da8fb1a18e372ba60edbcc94070cd9d9cc67b6f00eb959f). There is no claimed browser verification of this route yet.

The core fixes parent and child axes to horizontal-tb/mixed. Bounded peer review identified the proposed vertical ch/normal-lh oracle as unresolved: parent font choice is not automatically proof of parent axis choice, and existing native behavior cannot settle the specification. The exact twelve-case proposal is retained in pending/orientation-oracle-proposal.js, excluded from resources and the genuine WPT manifest. pending/README.md explains the required same-parent-font/different-axis diagnostic and missing-glyph calibration. No conformance PASS/FAIL expectation is assigned to those pending cases.

All frames are owned by one promise_test and removed through its cleanup; animations are cancelled. `window.variationBaseObservations` retains rows for diagnostics without console output. Root-self-reference callbacks retain both first/settled samples for two different root styles. No authored fonts, preferences, native instrumentation, or expected-failure metadata are used.

## Preparation checks and remaining obligations

PRE-REVIEW records retain successful 4c2f50/0 preparation of the initial 48-case proposal. After review, final CHECK from de461b/0 records the reduced 36-case staged roster (12/12/12), genuine Manifestv9 entries for three long testharness pages and zero WPT lint findings; the pending 12 orientation cases are excluded. Callback extraction does not execute callbacks. Node syntax passes. Actual final d46d25/0 ran two synthetic checker positives and nine rejecting controls using the fixture's exact checker, including the observed child-base values, stale parent value, broken literal/absolute controls, global numeric rebasing, rejected grammar, omitted phase, wrong orientation and unsampled animation. Four malformed serialization controls also reject. These are oracle checks, not browser observations or source/native refinement.

No test assumes these new 36 callbacks already fail or pass on either browser. Root should first run the exact package against the archived original and later the isolated native repair, retaining all controls, raw values, metadata and lifecycle provenance. A target mismatch whose calibration fails is not evidence of this bug. The root-self-reference cases may expose distinct existing conversion limitations; keep their names/results separate rather than weakening them to force a green pair.

Zoom, media-query conversion, @font-face descriptors, unavailable-glyph fallback selection, variable-font shaping, duplicate-entry conversion side effects, registered custom-value conversion and other numeric properties beyond the opacity control remain outside this fixture. Existing source effects/readset obligations remain necessary. The scheduler 19-input work and MathML package are separate immutable artifacts.
