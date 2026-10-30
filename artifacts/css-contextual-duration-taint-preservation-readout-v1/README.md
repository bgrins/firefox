# Animation taint and preservation baseline

The six frozen callbacks completed in all three runs. The local original build passed five and failed the tainted-variable callback; installed Firefox 158 and Chrome 156 each passed four and failed two. Both page endings were OK in each run. Root replayed the raw outputs and verified cleanup. No native candidate ran and no accepted fix count changed.

| Observation | Local original | Firefox 158 defaults | Chrome 156 defaults |
|---|---|---|---|
| Tainted duration fallback | FAIL | FAIL | FAIL |
| Literal and untainted duration controls | Both PASS | Both PASS | Both PASS |
| Fresh descendant rem widths | PASS | PASS | PASS |
| Collection destruction/recreation | PASS | PASS | PASS |
| Duration list / script ownership / auto | PASS | FAIL: auto unsupported | FAIL: script-owned opacity expected .6, observed 1 |

The tainted callback records a complete diagnostic trajectory before its assertions. The local and release Firefox trajectories are identical: composed --d is 2.5s, CSS animation-duration is 2s, 2.5s, but the fade remains 1000ms/.75 before and after the ordinary --d change 1s→2s. Chrome starts at 1000ms/.75 with CSS 2s, 1s, then updates to 2000ms/.375 with CSS 2s, 2s. Its first read and three passive frames agree. Both retain the animation/effect identities and 750ms hold time. Neither uses the literal 1500ms fallback required by the fixture's reading of current animation-taint text.

This is a shared divergence from that literal specification reading, with a separate Firefox stale-timing difference. It is not evidence that the native duration-input prototype introduced a regression. The existing CSSWG discussion distinguishes property-name taint in the specification from value taint in implementations; the role of pre-animation values needs reconciliation before changing timing policy. A generic non-animatable sink experiment is next to separate that timing context from ordinary taint propagation.

The Firefox auto failure is an explicit unsupported-feature assertion under release defaults, not a newly classified engine bug. The Chrome ownership failure occurs at the first opacity assertion and does not record later duration/membership state; a reduction is needed before attributing its cause. Passing callbacks certify assertions, not retained full trajectories or internal paths.

The local run uses the recorded branch application and WPT preferences. Installed runs use fresh profiles without CSS/WPT preference overrides and a reporting-only harness bridge; they are not enterprise-policy audits. Raw requests, page reports, served resource hashes and pinned applications were independently checked. Root terminals: local 16796/4afc92/0 with browser exit 1; Firefox 95237/2c555a/0; Chrome 29381/41f9aa/0. Root replay/checks 84184/9d6a23/0 and f9d075/0. Temporary profiles and owned processes are gone.

The isolated Lean input-selection model separately verified six theorems and rejected five false controls. It exposes old-cache coherence, honest captured input, and correct selected timing as separate premises; neither cache freshness nor cache/applied equality establishes correct taint substitution. It proves an abstraction, not native propagation or normative timing policy. Research signing remains blocked by the recorded 1Password buffer error; all outcomes remain local artifacts.
