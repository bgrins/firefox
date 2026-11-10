# Named timeline diagnostic hooks

Ten native files are pinned at b6f9b206df9c22b1ed2f41b1690614ec308a8471.
The semantic patch is byte-identical to the previous initial-admission
capsule's combined drain candidate. The two added files,
nsAnimationManager.cpp and KeyframeEffect.cpp, have identical base and
semantic bytes. Only diagnostic candidate copies differ.

The Rust role helpers additionally recognize provider, outside and fallback.
Existing queue/execution/return records identify the provider's mask and the
outside target separately. Cross-target requests are intentional here; the
previous analyzer's same-target restriction must not be reused unchanged.

UpdateNamedTimelineAnimation records only the fixed name --t, after matching
the scoped name and finding its target. Lookup records expose old/new timeline
addresses and kinds, availability of deferred updates, and the equal/defer/
rebind decision. A deferred record follows actual insertion into the deferred
set. Rebind entry/return bracket the single SetTimelineNoUpdate call; return
includes its boolean result and actual current timeline. Animation pointers
use the Animation base at both logging sites; documents use the nsINode base.

Timeline kind is null, unresolved, view, scroll or other. A concrete scroll
timeline may still have unresolved current time. These fields do not imply
resolved timing, effect eligibility or a restyle request.

The timing-eligible record is inside the existing successful
NotifyAnimationTimingUpdated condition, after its existing CanThrottle call
and before RequestRestyle. timing_changed=1 reflects the original single
HasComputedTimingChanged evaluation; that method is not evaluated again.
The record includes property count, chosen request type, effect/animation
identity and full target/pseudo identity. An actual EffectCompositor request
must still be joined: eligibility alone does not prove the request helper
ultimately admits a request. Absence does not identify which gate failed.

Previous caps and transport remain. Each added C++ file has the same 4096-event
cap convention. Whole-line writes reduce fragmentation without guaranteeing
interprocess atomicity. Malformed or capped traces affecting the measurement
must fail closed.

instrument.py authenticates the prior capsule, reconstructs it from pinned
Git blobs and patches, then instruments temporary copies. prepare.py replays
this capsule from its own patches and verifies all 30 source hashes. Both
reject optimized/non-isolated Python before mutation. Deterministic replay,
exact native-patch application and invocation controls are retained in
INSTRUMENTATION-CHECKS.json. No live source, index, build or browser was changed
by this preparation.

Searchfox discovery used revision 5a3f6397e61554eda92b0ec63ddd0ff752a22da2
for the named-timeline updater, AnimationTimeline kind methods, nsAtom::Equals,
OwningAnimationTarget and the timing notification guard. Source authority is
the local revision and source-role hashes, not the separately indexed bodies.
