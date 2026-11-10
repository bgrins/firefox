# Style-query / named-timeline feedback: source boundary

Status: bounded source investigation, not a new bug claim or convergence proof. Native basis is `3a6a6bfe2b0d3d551b2392206179f251002cfc7e`, including query handoff fix `90e0949346b5`. `SOURCES.json` authenticates 18 complete native files; `EXCERPTS.json` pins the separate Document excerpt. Primary specifications were fetched on 2026-11-10; hashes and discovery commands are retained. No live source, WPT, build, or Git mutation was performed for this capsule.

## Decision

A literal declaration selected by a style query can legally retarget an ancestor animation; animation-tainted substitution is not involved. A running, nonzero-rate animation retargeted to another finite timeline loses its resolved start/hold timing and becomes pending. The reviewed setter path does not itself restore timing. Consequently the proposed inner drain is not demonstrated to oscillate indefinitely by the legal feedback fixture. Conversely, “retargeting always waits until the next frame” is too strong: the stale-timeline pass may restore timing later in the same rendering update.

Under fixed underlying gate value, geometry, animation identity/rate, and no readiness/sampler re-entry, there can be at most the initial rebind and one rebind to the provider selected by the underlying gate. This is a conditional source deduction for this fixture. It does not establish termination for all CSS, arbitrary animation interactions, paused/seeking animations, or native re-entry. Instrument the boundary before changing the held drain.

## Primary contract

| Contract | Consequence for this experiment |
| --- | --- |
| [Scroll Animations, timeline scoping](https://drafts.csswg.org/scroll-animations-1/#timeline-scoping): a scope resolves to the last defined matching descendant timeline. | An earlier fallback and later conditional child provider may share `--t`; `timeline-scope: --t` on their ancestor permits the ancestor animation to resolve either. |
| [Web Animations 2, setting the timeline](https://drafts.csswg.org/web-animations-2/#setting-the-timeline): identical timeline object is a no-op; finite destination clears start and hold, enables auto-alignment, and running/finished state schedules pending play. | Distinguish actual timeline objects from equal source elements. Repeated same-object lookup is not repeated retargeting. |
| The same setter preserves resolved previous progress for paused animations. | Use a running, nonzero-rate CSSAnimation, with no script seek/pause/play after setup. A paused test is not the main cycle probe. |
| [Web Animations 2, pending play task](https://drafts.csswg.org/web-animations-2/#pending-play-task) allows a ready task at a microtask checkpoint, but not synchronously. | “Pending” is a scheduling boundary; it is not a proof that a whole rendering frame must elapse. |
| [Scroll Animations, frame calculation](https://drafts.csswg.org/scroll-animations-1/#frames) samples during animation update and permits one extra stale-timeline style/layout pass. Forced style reads do not run that stale pass; changes after final layout wait until the next rendering update. | Separate synchronous style drains, ordinary timeline ticks, and the rendering-stage stale sample. Same-frame recovery is compatible with a finite inner drain. |

The earlier Level 1 setter discovery is retained as a research receipt, but the finite-timeline extension in Level 2 is the applicable contract. Open CSSWG issue 13963 concerns deferring *unresolved timeline selection*; it does not turn a newly constructed concrete ScrollTimeline with an unresolved cached time into the native UnresolvedTimeline sentinel.

## Exact native path

1. `matching.rs::process_animations` skips its tasks for animation-only traversal with existing style. A normal style query rematch can instead enqueue `SCROLL_TIMELINES` when the child's literal `scroll-timeline` changes. The committed query handoff provides that normal rematch.
2. `TimelineManager` updates the provider collection. `nsAnimationManager::UpdateNamedTimelineAnimation` resolves the scoped name, returns for the same object, and calls `Animation::SetTimelineNoUpdate` for a changed concrete timeline. Its deferred-update case checks null/`IsUnresolvedTimeline()`, not whether a concrete timeline's cached time is unresolved.
3. `Animation::SetTimelineNoUpdate` clears start/hold for a finite destination and calls `PlayNoUpdate` for a formerly running/finished animation. `PlayNoUpdate` sets pending play, schedules paint, and updates timing. Neither operation calls `MakeReadyAndMaybeTrigger` or `AutoAlignStartTime` on this path.
4. `UpdateTiming` → `UpdateEffect` → `KeyframeEffect::NotifyAnimationTimingUpdated` can request a restyle when computed timing changes and update in-effect registration/cascade state. Such a request is work for the drain, not a new resolved timeline sample.
5. `ScrollTimeline::MakeNamed` creates a timeline without populating its cached current time. `ComputeTimelineData` reads that cache. The JS constructor explicitly updates it, so using `new ScrollTimeline()` would change the tested path.
6. `Animation::Tick` calls `MakeReadyAndMaybeTrigger`, which auto-aligns and tries pending completion. `ScrollTimeline::WillRefresh` updates its cache and ticks; `ScrollTimeline::UpdateIfStale` updates its cache, invokes readiness on attached animations, and posts animation updates.
7. `AnimationTimelinesController::UpdateStaleTimelines` calls the latter. The discovered Document rendering-stage caller runs deferred timeline changes, then stale updates, then another style/layout flush. `document-stale-excerpt.cpp` pins this call. `TryTriggerNow` also has a DocumentTimeline-only bulk trigger caller; that does not establish an equivalent finite-scroll-timeline drain path.

Searchfox caller receipts and the exact local copies support this boundary. They are not an exhaustive dynamic call-graph proof: native instrumentation must establish whether a sampler or ready path is re-entered during the actual `StyleDocument` invocation.

## Existing observations and their limits

`CONTEXT.json` hashes the old named-timeline README, current build receipt, and root's current feedback runtime. The older held-candidate native experiment established one upward same-call request and a newly selected pending/unresolved timeline; it did not demonstrate repeated resolved rebinding. Its candidate differs from the present committed query fix.

Root's current-browser experiment reports four passing observations, with opposed and aligned provider offsets both returning pending/unresolved fallback state throughout synchronous and 12 rAF samples; constant-query and stable-underlying controls resolve on the provider on the next sampled frame. These snapshots are consistent with more than one internal history: persistent pending state, or per-rendering-update resolution followed by a roundtrip rebind. Grouped JS observations may themselves span multiple flushing getters. This capsule neither ran that experiment nor assigns it a settled-pixel oracle.

## Next experiment

Retain the current branch semantics and add bounded diagnostic tracing first. Record style-call identity/depth, timeline-object identity, readiness entry/exit, auto-alignment, actual timing fields, cache samples, and rebind entry/exit. If a resolved sample and two opposing rebinds occur with nonzero style-call depth and no intervening rendering/stale phase, investigate the held drain. If all restoration occurs between style calls, the evidence concerns repeated rendering epochs, not an infinite inner drain. A trace cap or timeout is inconclusive and must be recorded explicitly.

See `PROBE-CONTRACT.md` for the bounded fixture and observation contract. No production repair is proposed by this report.
