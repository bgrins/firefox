# Bounded compositor trace proposal

This is a diagnostic overlay proposal, not a native fix or an executed trace. Only `dom/animation/EffectCompositor.cpp` changes. Both experiment arms should use the identical logger: one with the accepted `matching.rs` base and one with guarded duration proposal V2. Fresh source identities, app/build lineage and canonical bindings belong to the root-owned execution recipe; this package grants no execution.

The captured compositor base is a committed branch implementation that differs from origin/main. Narrow HEAD-to-working-file comparison was empty. Complete local `RequestRestyle`, `PostRestyleForAnimation` and `PreTraverseInSubtree` bodies match the successfully fetched Searchfox bodies modulo whitespace. `LOCAL-BRANCH-DELTA.patch` records unrelated existing branch changes; this overlay preserves them. No native file was edited. The first sandbox fetch failed DNS; read-only escalated fetches succeeded. Captured upstream files establish actual complete source, not truncated query output.

Enable only in the WPT child with `MOZ_DURATION_RESTYLE_TRACE=1`. Output goes to stderr, beginning `DURATION_RESTYLE_TRACE`. The helper permits only the ten initial IDs in the sealed trace fixture: `duration-feedback-{coupled,zero-start}-{passive,seek,outline,override,literal}`. It runs on the main thread and reads only the ID attribute; it does not flush style or modify the DOM. The fixture changes only initial IDs before acquisition, with no phase markers. Logging and extra hash lookups can perturb timing, so compare both instrumented arms and retain ordinary fixture records.

Each event has process ID, process-local sequence (1–4096), ID suffix, element pointer, pseudo type and identifier pointer, stage, cascade, request type, table-entry presence and bit, Servo/pre-traverse flags, root pointer, traversal flags, and optional effect/animation pointers. Unknown values are `-1`; absent pointers use the platform `%p` representation. The process-wide cap emits exactly one explicit `DURATION_RESTYLE_TRACE pid=N cap-exhausted limit=4096` marker before suppressing further events. A cap marker or missing sequence invalidates later absence inferences. Do not combine sequence order across processes.

| Stage | Meaning |
| --- | --- |
| `request-before` | Presence before lookup; bit before exchange (false for newly inserted absence). |
| `request-set`, `request-coalesced` | The existing exchange returned false or true; recorded bit is now true. |
| `request-throttled` | Throttled request preserves the bit and asks for a throttled flush. |
| `post-deferred` | Existing Servo/pre-traverse branch returns without calling PresShell. |
| `post-dispatch` | Immediately before the existing `PresShell::RestyleForAnimation` call; not a proof of later composition. |
| `pre-skip-throttled`, `pre-skip-no-shell`, `pre-skip-subtree` | Existing eligibility filter rejects this target. |
| `pre-selected` | Eligibility succeeds; this helper runs in both passes, so this is not consumption. Cascade is unknown here. |
| `pre-post-hint` | Immediately before the existing animation restyle hint call. |
| `pre-will-compose` | Immediately before `WillComposeStyle`; preparation, not a completed composition. |
| `pre-remove-wrong-document`, `pre-remove-no-effects`, `pre-remove-consumed`, `pre-clear` | Immediately before the corresponding existing removal/clear. |

Captured header values are Throttled=0, Standard=1, Layer=2; Animations=0 and Transitions=1. All removal logs precede the operation to avoid reading keys after removal. There is no post-call dereference of the `restyleEntry` reference. Full-document clear adds only a logging iteration before the existing clear. No original branch, mutation, return, hint or call is removed or reordered relative to other original operations.

The useful witness is a false-to-true request followed by `post-deferred`, then a later outside-Servo Layer request with the same target/pseudo/cascade and an already-true bit, followed by `request-coalesced`, without intervening posting or consumption in an intact trace interval. That would support the pending-versus-posted model premise. It would not establish an effective timing change, prove native causality, or identify which traversal was final. A later hint/consumption breaks this witness. Request types alone do not identify a specific JS call; correlate serial fixture roles and captured interventions conservatively.

This first trace does not instrument cycle-collection unlink/destruction, every caller, actual composition, timing values, or style traversal passes. It has no compositor instance ID. Use only stable fixture target lifetimes, do not join across document adoption or pointer reuse, and do not infer global absence of all possible queue drains. `PostRestyleForThrottledAnimations` remains unchanged; its calls still pass through the instrumented posting function. Whether the final traversal can leave a live unposted entry remains an experimental question.

The prior calibrated original passed both callbacks. The guarded-duration candidate failed both fixed 2000 ms override controls despite matching effect timing and current membership; its source/app restoration succeeded. Those observations motivate instrumentation but do not prove this cause or a feedback cycle. The sealed protocol model is conditional on exit without a drain; this proposal does not upgrade it to native refinement or acceptance evidence.

`python3 check.py` checks exact patch application in an owned temporary directory, ten-ID/cap/env structure, exact original-source recovery after removing diagnostic additions, two deliberately changed behavioral negatives, and complete upstream/local function agreement. Actual static run `a7878d/0` passed. Native compilation and browser execution have not occurred. No canonical state, Git index, app or native source changed.
