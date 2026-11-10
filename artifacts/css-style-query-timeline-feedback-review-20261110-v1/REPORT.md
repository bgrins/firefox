# Independent review: query-selected timeline feedback

The proposed CSS creates a real dependency loop, but opposite scroll offsets do
not establish an unbounded inner style drain. Finite-timeline rebinding can clear
the animation's resolved timing and leave it pending. Until a later sampling
phase restores timing, the query sees a fixed underlying value. That is a
plausible finite barrier which the probe must distinguish from a recurrent cycle.

The four-mode root fixture is suitable for a bounded diagnostic. No blocking
contract flaw was found. Its observations need phase-aware interpretation, and it
correctly avoids asserting a guessed final state.

## Scenario and specification trace

Assume a running CSSAnimation with nonzero playback rate and unchanged identity,
two fixed scroll containers, and a stable named-timeline scope. The earlier
fallback always defines `--t`; the later provider defines it only when a style
query of the animated ancestor's custom property matches. The timeline name in
that rule is a literal, not a substitution of an animation-tainted variable.

1. Style queries compare the container's computed properties. Animation-caused
   changes in query evaluation participate in style change events. Thus using an
   animated custom property to select a literal declaration is a supported
   dependency, not the forbidden `var()` route into a nonanimatable property.
   [Style queries](https://drafts.csswg.org/css-conditional-5/#style-container),
   [animated containers](https://drafts.csswg.org/css-conditional-5/#animated-containers).
2. Current named-timeline lookup permits descendant providers and selects the
   last matching definition in the scoped flat-tree subtree. The fixture's
   explicit `timeline-scope: --t`, permanently defined earlier fallback and later
   conditional provider give a concrete lookup change. Current draft lookup is
   global by default; this review does not assume the older nearest-ancestor-only
   model. [Timeline lookup](https://drafts.csswg.org/scroll-animations-1/#timeline-scoping).
3. Web Animations 2's finite-timeline setter resets start and hold timing. For a
   running or finished animation, step 9.5.1 says:

   > Schedule a pending play task

   The paused branch instead preserves resolved prior progress; a paused probe
   would test a different contract. The captured trace finds this guarded call
   directly. [Finite-timeline setter](https://drafts.csswg.org/web-animations-2/#setting-the-timeline).
4. Without a resolved hold or start time, animation current time is unresolved.
   Auto-alignment may restore start timing when the timeline is updated after
   layout. Pending-play completion is asynchronous. These are distinct from
   merely changing the associated timeline object.
   [Current-time calculation](https://drafts.csswg.org/web-animations-1/#the-current-time-of-an-animation),
   [auto-alignment](https://drafts.csswg.org/web-animations-2/#auto-aligning-start-time),
   [pending play](https://drafts.csswg.org/web-animations-2/#playing-an-animation-section).
5. Scroll-animation sampling is tied to rendering phases. Stale timelines can
   cause one additional style/layout round, while final-round changes wait for a
   later rendering update. The stale-timeline extra round does not apply to forced
   style/layout reads. Therefore same-render-frame work and same-inner-drain work
   are not interchangeable. [Frame calculation](https://drafts.csswg.org/scroll-animations-1/#frames).

**Verdict: INCONCLUSIVE** — the specs establish legal dependencies and relevant
timing barriers, but do not establish that this fixture repeatedly obtains new
resolved samples inside Gecko's proposed inner style drain. A phase-labelled
native trace is needed to claim that particular cycle.

The failed route is the inference “new provider has a different scroll offset,
therefore the existing animation synchronously samples that offset during the
same drain.” It skips pending timing and sampling phases. Likewise, query
invalidation requirements alone do not require draining all animation/layout
feedback to a synchronous fixed point.

CSSWG issue 13963 discusses immediate timeline association versus snapshot timing
and intermediate observable values. The fresh capture is open with four comments;
it does not provide a complete normative oracle for every intermediate result.
The native source comment referring to that issue must not replace the actual
specification steps. [Issue 13963](https://github.com/w3c/csswg-drafts/issues/13963).

## Native observations supporting the barrier hypothesis

Six source files were independently checked against revision
`3a6a6bfe2b0d3d551b2392206179f251002cfc7e`; the companion source audit owns the
broader caller enumeration.

| Boundary | What the reviewed source establishes |
| --- | --- |
| `UpdateNamedTimelineAnimation` | A different available provider calls `SetTimelineNoUpdate`; an unchanged timeline object returns early. Missing/unresolved named providers can instead enter a deferred-update set. The permanent fallback is important because it avoids conflating that separate missing-name policy with the experiment. |
| `Animation::SetTimelineNoUpdate` | The finite branch clears start/hold, enables auto-alignment, and calls `PlayNoUpdate` for the running/finished case. Association change alone does not call `AutoAlignStartTime` or `MakeReadyAndMaybeTrigger`. |
| `Animation::PlayNoUpdate` | With finite timing and nonzero playback rate, normal auto-rewind does not supply a new zero hold time. The pending-auto-alignment exception keeps the operation from returning early; it becomes play-pending and schedules paint. This makes the nonzero running-state precondition material. |
| `ScrollTimeline::ComputeTimelineData` | Current-time calculation reads the cached snapshot. An existing fallback's cached scroll position is distinct from the animation's own unresolved start time after returning to it. |
| `ScrollTimeline::WillRefresh` / `UpdateIfStale` | These update timeline data and can tick or make pending animations ready. They are the important possible barrier-crossing events to label in a runtime trace. A refresh and a post-layout stale update can occur in one rendering frame without being the same style-drain invocation. |
| `Animation::MakeReadyAndMaybeTrigger` | It auto-aligns before attempting to complete pending work. A new non-null start time must be associated with this kind of operation or another identified writer, not inferred from a source pointer change. |

## Conditional finite argument

This is an inference about a restricted state machine, not a proof of native
termination. Let `b` be the fixed underlying custom value after the animation
loses its resolved contribution. Let `lookup(b)` be the deterministic provider
selected by the query when it sees `b`.

Assume that no timing refresh, auto-alignment, seek, or ready completion can
restore a resolved effect inside the considered drain; that the fallback remains
available; and that unchanged lookup results reuse the same timeline object.
After the first rebind, the query sees `b`. It can request at most one more
provider change to `lookup(b)`. That rebind still leaves the query at `b`, so the
next lookup is unchanged. There are at most two provider changes from an initially
resolved state under these assumptions.

For the root fixture's `idle` underlying value, that conditional sequence is:

```text
fallback resolved/on -> provider pending/idle -> fallback pending/idle -> stop
```

This bound is on provider rebinding in that restricted model, not on every
queued task, layout pass, allocation, or future frame. A later rendering update
can restore `on` and start another finite sequence. Conversely, observing a new
resolved sample inside the same drain invalidates the argument's central
assumption and makes the loop a different investigation.

The `aligned` mode is particularly valuable: both resolved providers would yield
`on`, yet a transient `idle` contribution can still withdraw the provider. Churn
in that mode points to pending-state discontinuity rather than opposition of the
two resolved offsets. `constant-query` and `stable-underlying` keep the provider
selected across the pending state and separate this mechanism further.

## Review of the bounded root probe

Reviewed copy: `reviewed-probe.html`; `FIXTURE.json` records the original location
and exact hash. The fixture has four modes, an established 75% fallback sample,
four synchronous observations after arming, then twelve animation-frame
observations. Baseline, identity and fixed-offset assertions are appropriate;
the absence of a guessed final-state assertion is intentional.

Useful properties of the setup:

- The main animation runs; it is neither paused nor manually sought after
  establishment. Geometry and scroll offsets stay fixed, isolating provider
  association from scroll-layout feedback.
- The literal conditional declaration avoids the missing animation-taint fix.
- `idle` differs from both animated endpoint values, revealing absence of an
  effect rather than confusing it with the `off` keyframe.
- A stable earlier fallback avoids intentional disappearance of all providers.
- Both equal-offset controls and pending-state controls are present. A larger
  tree, additional registered-property cases, or unrelated CSS features are not
  needed for this first probe.

An observation row is **not an atomic native-state snapshot**. Its first
`getComputedStyle`, animation/timeline getters, provider-style read and repeated
gate read can cross multiple forced flushes. Preserve that order in the evidence.
If the row contains different before/after gates, do not pair its earlier timing
fields with its later provider name as though they existed simultaneously.
Optional repeated source/pending/current-time fields at the end help, but only
native phase markers can identify an inner-drain recurrence conclusively.

## Root-owned bounded runtime readout

The root subsequently ran this probe in the current local browser. I read the
completed results and independently grouped its logged observations in
`RUNTIME-READOUT.json`, which pins the original log and result hashes. All four
callbacks passed and the harness completed successfully. Those assertions verify
the probe's setup and invariants, not convergence or a fixed implementation.

| Mode | Four synchronous observations | Twelve frame observations |
| --- | --- | --- |
| Opposed | `idle`, fallback, pending, null animation time/progress; provider name `none` | Same observed state in all twelve samples |
| Aligned | Same as opposed | Same as opposed |
| Constant query | `idle`, provider, pending, null animation time/progress; provider name `--t` | `on`, provider, resolved 75% progress, not pending |
| Stable underlying | `on`, provider, pending, null animation time/progress; provider name `--t` | `on`, provider, resolved 75% progress, not pending |

In the opposed/aligned rows the fallback timeline itself reports 75% while the
animation current time remains null. This directly supports distinguishing a
resolved timeline snapshot from an animation whose own timing was reset.

The identical opposed/aligned outcome makes conflicting resolved offsets
insufficient as an explanation. The controls show that a provider retained
through the pending state can become ready on a later frame. The twelve repeated
pending observations still do **not** distinguish a never-completed ready
operation from per-frame completion followed by rebinding before each read. They
also do not show a nonreturning inner drain: every synchronous observation and
the test completed. The next step is the small native phase trace below, not more
frames or a new convergence rule.

## Smallest decisive native trace

If the bounded page shows unexplained repetition, trace only this animation and
the two provider elements. Record:

- outer flush id, rendering/refresh epoch, style-drain invocation and pass index;
- named lookup result and timeline object identity, not only the source element;
- animation identity, start/hold/current time, pending state and auto-align flag;
- sampled custom value, selected literal provider name and relevant task target;
- calls that refresh a timeline snapshot, auto-align, or complete pending play.

A meaningful repeated state must include those timing and phase fields. The same
task bit, provider DOM id, or custom-property string alone is insufficient.
Separate these outcomes:

| Observation | Interpretation |
| --- | --- |
| Rebind followed by unresolved timing and a returning flush | Finite pending barrier; further frame work may still be needed. |
| Alternation only after refresh/stale-sampling phase boundaries | Repeated legitimate phase work or bounded cross-frame churn; not evidence of a nonreturning inner drain. |
| Same complete state recurs with pending work inside one drain, with no external phase advance | Concrete cycle witness worth investigating. Identify the writer that restored timing or renewed work. |
| Pass or timeout cap reached without a repeated complete state | Bounded diagnostic failure, not a proof of an infinite loop. |

Use an external timeout and a small diagnostic pass cap if an instrumented drain
is tested. Reaching that cap must be reported separately from browser assertions.
This review does not authorize treating the cap as a production fix or changing
the held font/drain work based on a dependency graph alone.

## Reproduction and limits

`PRIMARY-SOURCES.json` records four freshly fetched specification HTML files and
the issue plus comments. Their specification hashes exactly match the section
snapshots returned by webspec-index. Ten report anchors were checked with
`webspec-index exists`; the setter-to-pending trace is captured separately. The
installed webspec-index reported version 0.14.0 with 0.15.0 available; it was not
upgraded. Initial cache-access and guessed-anchor failures are retained as
diagnostics, not evidence of missing specification rules.

This reviewer changed no live native source, browser state, build, Git index or
commit, and performed no browser execution. Runtime evidence and the complete
native caller boundary remain owned by the root and source-audit capsules.
