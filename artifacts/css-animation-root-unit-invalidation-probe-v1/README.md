# Root-unit animation invalidation observation

Prepared, unrun diagnostic. The frozen archived-original36 WPT run reported six root-relative animation failures at root-only/first while six ordinary root-relative cases passed. Examples: rem46 rather than62 and rlh74 rather than94. BASELINE-EXCERPTS pins the exact raw assertions. Later rows existed in the fixture window but were not emitted: settled staleness and native cause remain unknown.

## Root execution recipe

Open a fresh owned about:blank tab or empty probe.html host in the verified archived e86 browser. Evaluate the complete probe.js async expression and save its entire returned JSON plus separate actual browser/application/source identity and archive preservation receipts. Required context: normal document with a body, same-origin srcdoc frames, Web Animations, requestAnimationFrame and FontFaceSet. No existing site or session is needed. Root owns browser/native serialization; this artifact launches nothing.

There are six fresh standards-mode frames: rem and rlh, each with variation-first, width-first and opacity-first getter orders. Six phases per frame each have first and fonts-ready/two-rAF settled observations: initial, root-change, seek-quarter, seek-half, recreate-same-target and new-target. That is72 rows, each with three principal animated values, or216 scalar observations. Parent30px/61px and child60px/99px remain fixed; root changes23px/37px to31px/47px.

The three separately paused effects interpolate endpoints1 and3: variation wdth calc(unit/1px), ordinary width in unit, and nonfont opacity calc(unit/1000px). The opacity denominator avoids endpoint clamping for every declared value; the assessor scales it back for comparison only. Effects start at50%, seek to25% and back, are cancelled/recreated on the same targets, then recreated on fresh same-style elements. The fresh-target phase intentionally creates a new conversion context. The chosen first animation getter runs before all static/reference/control getters in every sample.

Controls: static variation/width with2unit, static opacity2unit/1000px,100unit root reference, absolute variation, literal variation and width animations at50%, unrelated child-em opacity, actual root/parent/child font sizes and root line-height, CSS.supports, actual paused progress/currentTime and keyframe arrays. rem and explicit rlh avoid platform glyph-metric assumptions. All animations are cancelled and all frames removed in finally; errors and partial results survive.

## Interpretation

The saved Web Animations algorithms compute keyframe properties in their target dependency context before effect interpolation. This diagnostic reports current-root/original-root/other observations, not automatic conformance verdicts for first-frame timing. Settled samples, seek behavior and fresh conversion must be considered separately. Failed static/literal/reference calibration makes the row uncalibrated.

A possible native cause is numeric calc dependency information staying in a temporary Context/StyleBuilder instead of reaching retained keyframe data. That is a hypothesis, not a finding. Variation versus opacity versus width distinguishes candidate boundaries without attributing source cause. The existing parent-font-base candidate remains unchanged and is not assumed to fix root-unit invalidation. No new bug or accepted fix is counted.

After saving the exact returned object, root can run:

```
python3 -I -S -B artifacts/css-animation-root-unit-invalidation-probe-v1/assess.py SAVED-RESULT.json
```

Unwrap connector envelopes first without discarding rows. The assessor checks six exact frame identities and72 ordered rows, supports/progress, raw-versus-parsed consistency, root mutations, controls and cleanup. Both expected numeric alternatives are recomputed independently. Output retains all216 classifications and calibration failures; native_acceptance isfalse.

## Saved preparation

JavaScript syntax d1a9f3/0. Assessor check4280e8/0 covers four synthetic paths: current, retained-old-until-recreation, first-only transient, numeric-only old while width is current. Ten corruptions reject, and a separate bad literal control becomes uncalibrated. These are checker controls, not browser observations. Peer6484d9 read exact source/assessor and cleared this bounded diagnostic scope without rerunning tests. No native/browser/archive/live-source operation ran. Source-cause investigation remains pending actual output.
