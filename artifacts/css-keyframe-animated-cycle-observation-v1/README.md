# Local animated-cycle observations

Open `observe.html` later in a browser and press **Run observations** once. Reload for another run. It has no WPT, network, external script, or server dependency. The complete JSON is displayed and exposed as `window.cycleObservationResult`; `window.runCycleObservations()` is the equivalent manual entry point. No browser run or live fixture installation has occurred.

The ordered `ROSTER.json` contains 52 independent targets: 13 scenarios × two effect-creation orders × two computed-value read orders. An uninterrupted run records 108 samples (32 cyclic observations, 76 numeric controls), plus registration, base and cancellation calibrations. All three properties are non-inherited registered `<number>` values: initials x=10, y=20, z=3; literal underlying values are x=77, y=88, z=99. The unregistered `--cycle-wrong` is red; `--cycle-missing` is absent.

The first family samples x=[var(y),100], y=[200,var(x)] halfway, both fresh and acyclic→cyclic→acyclic. The second samples x=[10,20,var(x)] at .25→.75→.25, both fresh and all-literal→cyclic→all-literal. The third checks invalid and fallback endpoints independently of cycles. Literal reference stacks give (55,110) and (10,20), but neither pair is an allowed-answer list for cycles.

All animations are constructed idle with replace composition, linear easing and 1000ms duration. Synchronously setting `currentTime` establishes a held/paused sample; that state, absence of pending tasks, progress and iteration are checked after the two value reads. No awaited ready task, animation frame, computed-timing getter or authored-keyframe getter precedes the first read after each seek. Creation/setKeyframes may itself perform internal work: “first” means the first requested computed-value read after that seek, not proof of the first engine computation. Each read order queries x/y before the independent literal z sentinel. There is no await or DOM write between first and repeated reads.

Every trial retains authored keyframes and timing details, then cancels both effects and checks return to literal base values and empty animation lists before removing its target. History phases reuse the same effects and replace both frame lists in the selected creation order. Fresh trials use a new target and new effects, after a literal base-style calibration. Authored retention is not introspection of computed endpoints.

## Numeric controls

[WA property computation](https://drafts.csswg.org/web-animations-1/#computing-property-values), [var replacement](https://drafts.csswg.org/css-variables-1/#replace-a-var-function), and the [registered computed-value rules](https://drafts.css-houdini.org/css-properties-values-api-1/#calculation-of-computed-values) support these acyclic controls:

| Control | Halfway x/y |
|---|---|
| y=[200,400]; x=[var(y),100], current y=300 | 200 / 300 |
| Literal x=[300,100], y=[200,400] | 200 / 300 |
| Invalid red or missing variable without fallback; x initial=10, other endpoint=100 | 55 / 200 |
| Missing variable with fallback30, other endpoint100 | 65 / 200 |
| Present wrong-type red with fallback30: fallback is not selected; x defaults to10 | 55 / 200 |

The literal three-frame x=[10,20,30] yields15/25/15 at .25/.75/.25; y yields250/350/250. The unrelated literal z yields 2+4t. Invalid authored custom-property tokens are retained and checked: registered syntax/defaulting is computed-value behavior, not silent keyframe removal. The existing ten-case endpoint diagnostic remains unchanged.

## Interpretation

`kind: observation` never judges the cyclic x/y numbers: `cyclic_numeric_oracle` is null and `cyclic_values_judged` is false. Its `calibration_pass` checks only timing/authored retention and the independent z sentinel. A changed sentinel is retained as an observation of broader effect behavior, not proof that a cyclic number violates the specification. Calibration failure, including an acyclic control failure, leaves the cyclic records available but prevents treating that run as a calibrated experiment.

`status: complete` means all 108 planned sample records were emitted, not conformance or acceptance. `all_calibrations_pass` is separate. Exceptions remain visible, cause calibration failure, and missing samples cause incomplete status. Cleanup results are included. Browser crashes or a hung synchronous engine may prevent publication of a final result; partial displayed JSON alone does not prove cleanup or absence of infrastructure failures.

The [sealed oracle trace](../css-keyframe-animated-cycle-oracle-review-v1/TRACE.md) remains INCONCLUSIVE about which endpoint/final-property computation owns a cycle mark and how unselected keyframe computation affects it. This page supplies observations for that question; it assigns no cycle-specific expected number, new bug count, or acceptance credit.

## Inert validation

`node artifacts/css-keyframe-animated-cycle-observation-v1/check.mjs` syntax-checks the script, derives the roster/counts, checks pure control arithmetic and retention rejection, and invokes the real sample-record function against inert API stubs. The classification checks deliberately accept arbitrary cyclic x/y strings while rejecting a bad sentinel or wrong acyclic number. They also require both value reads to precede timing introspection. These are record-format/control-algorithm checks, not execution of registration, CSS defaulting, Web Animations, or a browser. The frontend skill and performance guidance were read; this is an isolated research page, not shipped Firefox UI. No WPT lint or native compilation is claimed.
