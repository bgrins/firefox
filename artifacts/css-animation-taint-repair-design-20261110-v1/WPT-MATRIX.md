# Proposed regression and policy matrix

This is a test design, not a record of newly executed tests. Only rows R1, R2,
R4 and I1 were observed in the existing four-callback calibration. I1's later
timeline assertions were unreachable after its animation-name failure.

Use WPT `testharness.js` computed-style assertions. Keep each destination in a
separate callback. A helper should independently establish the source custom
value, the driving CSS animation's identity, its paused state and a progress of
0.5 before asserting the destination. Distinct fallback tokens ensure success is
not confused with the destination's initial value. Isolate names between tests;
reusing a property name mentioned in unrelated keyframes would contaminate tests
under a name-based policy.

## Required regression cases

These cases use an actively sampled CSS keyframe declaration that wins the
cascade on the consumer element, avoiding inactive-rule and losing-value policy
differences. R5 and later are proposed follow-up, not reproduced results.

| ID | Setup | Required result / purpose |
| --- | --- | --- |
| R1 | Unregistered `--name: --live` from active paused keyframes; `scroll-timeline-name: var(--name, --fallback)`. | `--fallback`; observed failure was `--live`. |
| R2 | Same source, independent `timeline-scope` assertion. | `--fallback`; observed failure was `--live`. |
| R3 | Same active source; omit `var()` fallback in a nonanimatable destination. | Guaranteed-invalid substitution yields the destination's invalid-at-computed-value-time behavior; do not accept the primary. Pair with a literal destination control so unsupported syntax cannot pass. |
| R4 | A never-keyframed, distinct custom property with the same token value. | Primary accepted in both destinations; observed passing control. |
| R5 | Active numeric or length custom-property source, consumed by an animatable property such as `margin-left`. | Sampled value remains usable. Use matching units and a different fallback value. This detects an overbroad rejection of all tainted substitutions. |
| R6 | `--alias: var(--animated)` on the consumer; then the nonanimatable destination uses `--alias`. Repeat with two aliases. | Destination fallback selected; resolved aliases must retain infection. |
| R7 | Tainted primary with a clean custom property as fallback; nested invalid/tainted fallback followed by a clean literal fallback. | The first valid permitted fallback wins. This checks the guard enters fallback processing instead of invalidating the entire declaration. |
| R8 | Identical token payload for an animated source and a never-keyframed source on parent/child or sibling styles; alias switches which source it references. | Computed destination changes between primary and fallback despite equal source text. Check both directions; detects map deduplication and metadata-only invalidation loss. |
| R9 | Repeat direct destination and alias cases for registered `syntax: '*'` and `syntax: '<custom-ident>'` properties with compatible dashed identifiers. | Same tainted-reference fallback behavior; include clean registered controls. No registered-property exemption has been established. |
| R10 | Registered `<number>` source interpolating 0.25 to 0.75 at progress 0.5; `opacity: var(--n, 0.9)` and `animation-iteration-count: 1, var(--n, 3)` with a literal first driving animation and independent second animation. | Opacity is 0.5 and the second iteration count falls back to 3, while the first driver's fixed count remains 1. This exercises typed interpolation, parsed/serialized paths and a grammar-compatible nonanimatable sink without changing the driver. |
| R11 | Direct shorthand consumption, e.g. `scroll-timeline: var(--animated-shorthand, --fallback block)`, versus equivalent longhands. | Correct fallback for the nonanimatable shorthand; no pending-shorthand cache bypass. Verify parsed computed longhands and preserve destination metadata. |
| R12 | Same-element animation-name control with a literal first driver slot and variable second slot: `animation-name: set-name, var(--name, fallback-animation)`. | The literal driver remains active and the second slot falls back. Keep timing/play-state lists explicit and verify driver existence so removing the source animation cannot masquerade as a pass. |
| R13 | Both attribute-tainted and animation-tainted custom values, with separate clean controls. | Existing attribute URL restrictions survive; animation fallback does not clear attribute taint on the selected result. Reuse the branch's existing attribute-taint suite rather than inventing new fetch-based security claims. |

R8's source toggle should change an alias between two distinct sources while the
animated source remains active. Toggling whether a name is mentioned in a removed
keyframes rule would mix the equality test with the unsettled name-lifetime gate.

## Policy-discriminating cases

Keep these separate from the minimum calibration and label expected results by
the adopted policy. They are needed before declaring the entire feature repaired.

| ID | Setup | Decision exposed |
| --- | --- | --- |
| I1 | Parent active animation, child `animation-name: var(--name, fallback-animation)`. | Current taint-preserving expectation is fallback; existing calibration observed `--live`. Issue 13933 proposes a different inheritance rule. |
| I2 | Parent source with ordinary inheritance, explicit `inherit`, child local clean override and grandchild consumption; include registered `inherits: false` and explicit `inherit`. | Exact inheritance boundary and whether overrides clear name-based or value-based taint. Do not equate `inherits: false` with an animation-taint exemption. |
| P1 | Keyframes rule mentions `--name` but no element uses it. An ordinary declaration supplies the same name. | Name-taint versus sampled-value acquisition. |
| P2 | Active animation supplies `--name`, but a clean `--name: --clean !important` wins. | Current property-name reading versus Blink's documented selected-value behavior. |
| P3 | Animation cancelled, removed, finished with/without fill, replaced, or keyframes CSSOM edited while source text remains equal. | Taint lifetime, publication removal and invalidation; outcomes depend on the selected acquisition policy. |
| P4 | `--alias: var(--clean, var(--animated))`, with valid clean primary and unused tainted fallback. | Reference-based infection versus selected-result propagation. This is not interchangeable with attribute-taint rules. |
| P5 | CSS animation versus `Element.animate()` producing the same custom value. | Whether and when Web Animations effects acquire taint; an animation cascade level alone does not distinguish them. |
| P6 | Registered custom-property transition, including discrete transition permission where applicable. | Transition acquisition; keep issue 11102's policy and destination wording explicit. |
| P7 | Same property name in different elements, shadow trees and keyframes scopes; dynamically insert/remove the owning stylesheet. | Scope and invalidation of a proposed tainted-name registry. |
| P8 | CSS-wide keyword endpoints, implicit underlying endpoints, additive/accumulated effects and multiple iteration composition. | Whether origin or participating values determine taint, and how non-value/underlying endpoints preserve it. |

Avoid sleep-based animation sampling. Use deterministic paused CSS animations and
style flushes for static tests, and the appropriate animation-ready/frame helpers
for dynamic tests. Run the focused new WPT plus existing custom-property
animation, registered-property, fallback/cycle, pending-shorthand and attribute-
taint regressions. No compilation is needed to author or run HTML-only tests
against an already-built browser; a native repair requires a rebuilt browser.
