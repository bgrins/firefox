# Named timeline runtime review

The experiment reaches a concrete non-descendant producer edge. Initial
styling of the newly revealed provider executes a scroll-timeline update,
rebinds an existing ancestor's animation, passes its timing-change eligibility
gate, and requests an animation restyle on that ancestor. The request is
delivered in the next StyleDocument drain iteration before the primary getter
returns. This is finite initial work, not a recurring initialization cycle.

| Mode | Provider admission | Task | Timeline decision | Delivery |
| --- | --- | --- | --- | --- |
| smil-scroll | AnimationOnly, initial, call 13 / iteration 0 | 32: ScrollTimelines | Distinct concrete scroll timeline, changed=true | One Standard Animations request; outside installed in iteration 1 |
| normal-scroll | Ordinary initial styling, call 29 / iteration 0 | 32: ScrollTimelines | Distinct concrete scroll timeline, changed=true | One Standard Animations request; outside installed in iteration 1 |
| smil-scope-only | AnimationOnly, initial, call 47 / iteration 0 | 128: TimelineScopes | Same timeline; equal lookup | No request or drain selection |

TASK-MASK-SOURCES.json pins the enum values and the affected-name versus global
map-dispatch branches at the build's source revision. Fixed-role attribution
identifies provider and outside as distinct nodes in each tested document.
The fixture establishes outside as the ancestor of the hidden host/provider;
ancestry is not inferred from pointer values.

The two positive paths join the actual queued task, installation, callback
execution, named lookup, rebind entry, timing eligibility, compositor request,
rebind return and callback return. Timing eligibility records one property,
timing_changed=1, and Standard request type 1. The animation identity is the
same across lookup, rebinding and eligibility. The effect identity also joins
eligibility to the later will-compose record. No second timing-change getter
was introduced by instrumentation.

The ledger retains the full compositor/target/pseudo/pseudo-identifier/cascade
key through actual hint insertion, selection removal, animation admission and
style installation. It verifies pretraverse queue counts and call boundaries.
These intervals contain exactly one request and one delivered cohort apiece;
extra requests are rejected as unsupported/unaccounted rather than ignored.
This capsule does not generalize the ledger to arbitrary renewal patterns.

The SMIL request is raw row 14745 and the outside installation is row 14815;
the ordinary control uses rows 15471 and 15491. Both first and repeated fonts
are 10px, versus the calibrated 20px baseline. The new timeline is a concrete
scroll object, but the subsequent observation still has unresolved progress
and pending=true. Thus 10px is an observed intermediate font value, not a claim
that the newly bound animation has reached a settled timeline sample. The
scope-only control remains on the active fallback at 20px.

All three WPT callbacks pass, with harness OK. The runtime explicitly enables
scroll-driven animations and disables CSS display animations. The recorded
transaction and independent root audit restore source and browser state.

No malformed tagged records or caps occur anywhere in the trace. Events from
other processes interleave with the measured intervals: 141 in smil-scroll,
18 in normal-scroll, and zero in the scope control. The analyzer filters by
the provider's independently identified process/document before reconstructing
call state. The tested PID is 79982. C++ records lack thread IDs; their
synchronous call association relies on inspected source plus bracketing,
while Rust admission/installation and execution/return thread joins are
explicitly checked.

analyze.py authenticates and reuses the earlier parser/classifier by SHA-256;
its named-timeline and cross-target joins are local to this capsule. The
33 negative controls mutate the real trace and must fail with their specific
expected ValueError. KeyError, IndexError or an unrelated validation error
fails the harness. The controls cover task/call/document/thread identities,
timeline identity/results, actual eligibility, effect/pseudo/type joins,
missing returns/requests/installations, scope equality, extra requests,
malformed records and caps.

The result rules out assuming that every producer edge descends the element
tree. It does not rule out a richer progress measure that accounts for finite
initial provider creation and subsequent rebinding. No infinite renewal,
general termination proof, native-to-Lean refinement, newly discovered bug,
or release-browser performance result is established.
