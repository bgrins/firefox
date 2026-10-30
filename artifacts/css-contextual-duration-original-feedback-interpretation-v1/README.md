# Original feedback observations and the model boundary

The completed original does **not** establish the feedback model's synchronized seed. Its zero-start samples map to `(computed=1500, applied=1000)`, whereas the proved cycle starts from `low=(1000,1000)` or `high=(1500,1500)`. Matching the applied 1000ms value alone is insufficient.

The sealed runtime is css-contextual-duration-broader-original-runtime-2, FILES492edf9f5cb288ecf6c2c16b8935aea5fc9a909bcfb28be04cb636165e610522, actual root terminal89331/dcda0d/0. The selected-record check d36ae4/0 authenticates ten runtime files, phase/raw/assessment hashes, all three owner-bound envelopes and their eight samples. Raw test rows/endings equal the saved assessment: three completion PASS rows and one OK ending. Root's saved terminal reports full replay and state/application preservation; this review did not rerun the full-state verifier or browser.

| Record | All eight computed font/duration samples | Applied effect duration/time/progress | Other observation |
| --- | --- | --- | --- |
| self font, from16px | 28px / 1.75s | 1000ms / 750ms / .75 | Underlying opacity1 |
| coupled font and opacity, from16px | 28px / 1.75s | Both retained handles:1000ms / 750ms / .75 | Opacity .75 |
| zero-start self font, from0px | 24px / 1.5s | 1000ms / 750ms / .75 | Underlying opacity1 |

Every recorded handle is paused. Repeated font/duration reads equal the first reads, and all eight sample records within each case are equal. The fixture records the initially acquired handles; it does not repeat getAnimations membership/identity assertions at every sample. Stable acquisition, effect association and native ownership throughout the run must not be inferred solely from completion PASS. Its source contains no updateTiming call, so CSS ownership is a fixture/source inference rather than a directly logged native flag.

## Supported arithmetic, conditional transition

The zero-start values support the one-way arithmetic edge at applied1000ms: progress750/1000=.75, font32×.75=24px, and duration24/16×1s=1.5s. The positive active-phase premise holds for that measured effect. The16→32 cases analogously give16+16×.75=28px and1.75s. The coupled opacity .75 agrees with the second effect's retained1000ms duration. These are finite observations consistent with the model's arithmetic; they do not establish a native refinement.

What is missing is the modeled dispatch/update/resample edge. No sample reports applied1500ms, font16px or a return to applied1000ms after such an update. No pre-seek or acquisition snapshot records a synchronized `(1000,1000)` state. The first measurement is already `(1500,1000)` after the fixture sets currentTime750ms and waits for a frame. Candidate setup starts fresh and may reach different states; it cannot inherit the original's unobserved initial synchronization as evidence.

## Checked stale-state boundary

ObservedBoundary.lean imports exact sealed copies of DurationScheduling and DurationFeedback. It defines the measured projection as `(1500,1000,CSS)`. The existing feedbackEvent computes1500000/1000=1500ms. Because scopedStep compares old computed duration1500 with that same next input1500, its dispatch predicate is false and the applied duration remains1000. Thus this **abstract stale state is fixed**, is not synchronized and is neither cycle entry.

Actual isolated proof run: launch216d82, session2753, terminale69843/0. Two declarations were checked and axiom-audited (none; propext respectively). A false claim `observed=low` was rejected with the intended decide-proved-false diagnostic. The pinned Lean executable and both dependency source hashes were verified; imported packages are unchanged and temporary compilation scratch was removed. This supplements the existing model with a boundary check, not a new browser observation or canonical coverage claim.

There is no contradiction with the existing arbitrary-iteration two-cycle theorem: that theorem requires a start in the synchronized low/high pair, which the observed projection does not satisfy. Nor does fixed-input idempotence or this stale-state fixedness prove correct synchronization. The original can remain observably stable precisely because applied timing is stale. A hypothetical equality-only repair starting from this stale state without a subsequent computed-input change could also miss it; the upcoming candidate is initialized from a fresh page, so its actual acquisition sequence must be observed rather than equated with that hypothetical start.

## Upcoming candidate interpretation

Retain every candidate sample and compare computed and applied duration separately, together with time, progress, font and repeat reads. If a sample is synchronized at1000ms or1500ms, the model's seed premise is then supported for that sampled projection, but native resampling/dispatch equivalence still remains conditional. Alternating sampled outputs would be evidence of sampled instability, not by itself an infinite internal loop. A finite stable sequence would not prove global convergence or absence of unobserved intermediate work. Missing records, watchdog termination or a crash are distinct operational findings; do not translate them into the model's mathematical cycle without tracing the cause.

The original's eight completed frames do not show a hang, a two-cycle or numeric correctness of the self-dependent specification. Feedback PASS means acquisition, bounded completion and acknowledged transport only. No candidate execution is analyzed here, no iteration cap is proposed, and no native bug, accepted fix or coverage count changes.
