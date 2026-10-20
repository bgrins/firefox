# Independent base-animation metadata runtime review

## Decision

The retained eight-case run establishes an observable stale computed-style result on the combined local build after endpoint fix78, before any base-value repair. Four same-payload implicit-endpoint cases fail; all four controls pass. The immediate-result oracle is supported. This is acceptance of the diagnostic, not a candidate repair, standalone upstream reproduction, complete scheduler proof or security-impact claim.

The failure pattern is consistent with the source hypothesis that `EnsureBaseStyles` misses a metadata-only change when deciding to request resampling. Runtime alone does not uniquely prove that internal cause. A later successful query demonstrates recovery, not directly the state of `mBaseValues` during the first query.

## Authentication and reconstructed results

The source capsule's externally pinned FREEZE is `7b319a18ea483bb42ded05b4ff4fc65967bd6c78d0707a124208325952867c58`; its manifest is `7e8fb1b57a256c7e80bac13aa6715a99148ef2628987b81f175f40b728851b27`. I authenticated all 19 manifest entries before relying on its test/source. No producer script or browser was executed.

`review.py` independently parses raw JSON, checks the exact ordered eight identities, compares complete rows/harness with RUN.json, and reconstructs the source/binary provenance. Its retained output is RESULT.json.

| Exact case family | Result | Final discrepancy |
|---|---|---|
| Neutral start clean to tainted, same payload | FAIL | Old URL remains instead of none |
| Neutral end clean to tainted, same payload | FAIL | Old URL remains instead of none |
| Neutral start tainted to clean, same payload | FAIL | Old none remains instead of URL |
| Neutral end tainted to clean, same payload | FAIL | Old none remains instead of URL |
| Neutral start clean to tainted, different payload | PASS | None |
| Neutral start tainted to clean, different payload | PASS | None |
| Explicit replacement ignores base clean to tainted | PASS | None |
| Explicit replacement ignores base tainted to clean | PASS | None |

There is one test start, eight unique test-status rows, one harness OK, one suite end, no crash event, and process exit1 from the expected diagnostic failures. All failure messages identify `Immediate effect URL taint`; their stacks point to `check` called by the final assertion in `runCase`.

Each failing case therefore completed the earlier literal-image calibration, original base/effect payload and taint checks, changed nonanimated base check, and explicit-resample payload/taint check. Even the final immediate payload assertion passed before its image assertion failed. This is control-flow evidence from synchronous assertions, not separately logged per-assertion telemetry.

## Oracle and timing

The registration is noninherited `<string>` with a distinct literal initial value B. Base values A/C differ from B, so the selected implicit endpoint is not masked by equal explicit strings. There is one effect, default replace composition, no transition or animation declaration, and no additive-string assumption.

The Web Animations effect-value algorithm supplies the current underlying value for a missing endpoint at0 or1. Applying an effect stack starts from the property's current value without animations. Thus the missing endpoint is not an old snapshot or an additive string identity. [Effect values and application](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect).

Registered values animate according to their computed type; textual values interpolate discretely. At250ms the missing start is selected, and at750ms the missing end is selected. Advancing by1ms stays in the same half. [Registered animation behavior](https://drafts.css-houdini.org/css-properties-values-api-1/#animation-behavior), [Textual data types](https://drafts.csswg.org/css-values-4/#textual-values).

Attribute provenance extends through registered substitution, and tainted URL use invalidates the declaration at computed-value time. The literal reference avoids network/image-load timing; the assertion concerns computed background-image serialization. [Attribute security](https://drafts.csswg.org/css-values-5/#attr-security).

Calling `pause()` followed by setting currentTime does not require waiting for an outstanding pause task: setting currentTime completes that pause synchronously. Model liveness requires dependent state updates and explains that computed-style queries reflect current animation state. Asynchronous event/promise delivery does not authorize the stale style observed here. [Setting current time](https://drafts.csswg.org/web-animations-1/#setting-the-current-time-of-an-animation), [Model liveness](https://drafts.csswg.org/web-animations-1/#model-liveness).

**Verdict: REACHED** for the immediate computed-style expectation in this fixture. The test copies primitive strings from the CSSStyleDeclaration into `immediate`; it does not retain a live declaration whose values could change before the final assertion.

## Source and build association

RUN.json pins63 inputs and records stability after execution. Its pair digest exactly matches `css-animation-endpoint-paired-root-v1/PAIR.json`, which records a successful candidate binaries build, stable sources/binaries and candidate test execution. Firefox/XUL digests in RUN equal that pair's candidate binaries. The observed tree includes previous registration/map/range repairs; this is not a minimal upstream build.

The source capsule contains pre-format KeyframeEffect.cpp hash `671ba8d6...`; the runtime receipt pins `02ffed21...`. I independently applied the sole literal replacement in FORMAT-TRANSFER.json to the authenticated full source and reproduced the runtime hash exactly. It only wraps one comparison line. All other pair candidate pins are retained unchanged; the new diagnostic test is added with exact source-capsule hash `ad13944e...`.

This is a documented whitespace-equivalence transfer from the compiled endpoint source to the formatted runtime source, not a claim that a separate compilation used the formatted bytes. The review does not rehash current live binaries, which may legitimately advance after this historical run. Exact evidence hashes are in INPUTS.json; complete sources remain in their existing capsule.

I read the complete retained `EnsureBaseStyles`, `EnsureBaseStyle` and `UpdateProperties` bodies. They rebuild the map, compare via AnimationValue inequality, and request a restyle on detected base changes when endpoint properties are unchanged. That supports the diagnosis without converting a local source read into proof of every caller or invalidation route. Separate source/repair review owns those broader obligations.

## Causal limit and next gate

In this original probe, the successful `Explicit resample` check follows control/reference computed-style flushes **and** the1ms seek. It does not isolate which of those operations permits recovery. This does not weaken the captured immediate-result defect, but the claim “the seek alone fixes it” is not yet established.

Root has agreed to preserve this run and add a separate version that captures the target after control/reference flushes, compares that observation with the immediate capture, and only then seeks. Review that new result before asserting a precise seek-only recovery mechanism. A passing intermediate observation should preserve both payload and taint, not just serialization of the custom property.

Candidate acceptance still needs exact source/patch review, paired runtime against final test bytes, stable source/binary pins, relevant unchanged controls and explicit standalone dependency accounting. A narrow change must preserve ordinary payload comparison, null/missing-map handling and unrelated properties. No global PartialEq change, generalized additive/numeric taint result, or full base-map lifecycle claim follows from these eight cases.

## Replay

From this checkout run `python3 -I -S artifacts/css-animation-base-metadata-runtime-review-v1/review.py`. It only reads retained artifacts and prints a reconstruction. INPUTS.json pins the external closure; no redundant full source copies or generated build targets are included. `check.py` authenticates this review's own files. Primary specs were freshly read on2026-10-19; links identify current drafts, not frozen full-spec snapshots.
