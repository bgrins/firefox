# Pending timing versus origin eligibility

A concrete source-reachable state invalidates the general assumption that ordinary IsInEffect equals actual composition eligibility. The attached standalone probe is ready for root execution after the live transaction releases. It has not been run. This is an argument against the held eligibility candidate, not evidence of a current Firefox bug, and it does not settle the disputed transition-origin membership contract.

## Native witness

SOURCES.json pins eight native files at research HEAD 449da6d3112d164287e6a76de66c45344e4cc2a7. Searchfox discovery preceded exact Git reads; the pinned tree is read from Git objects, not from the active candidate installation.

1. Start a normal document-timeline WAAPI animation and await its ready promise. It has a resolved start time, null hold time, positive rate and no pending task. Choose a positive delay and fill:none.
2. Seek to a time just before the delay while it is still running. Animation::SilentlySetCurrentTime updates start time from the current timeline time; it does not create a hold in this state. UpdateFinishedState clears any hold for a running, nonfinished positive-rate animation.
3. Call pause. Animation::Pause sets PausePending and schedules painting. Because current time is resolved, it leaves hold time null and start time resolved. UpdateFinishedState does not change hold/start in the pending case. Setting currentTime AFTER pause would complete the pause and destroy the witness; that operation appears only in the settled-hold negative control.
4. Stay in the same JS task while wall-clock time advances across the delay boundary. DocumentTimeline::GetCurrentTimeStamp uses the refresh driver's MostRecentRefresh, not TimeStamp::Now. Thus ordinary currentTime and ordinary effect progress remain before-phase/null as long as the document timeline does not tick.
5. Force style computation. Animation::ComposeStyle sees pending, null hold and resolved start on a wallclock-tracking timeline. It temporarily sets hold time from TimeStamp::Now, calls KeyframeEffect::ComposeStyle, then restores hold time. The latter sees a resolved active sample although ordinary IsInEffect was false. This substitution is unconditional on compositor eligibility; using margin-left does not bypass it.

MakeReadyAndMaybeTrigger is called by Animation::Tick and the finite scroll-timeline update path found by the identifier audit. The document case here does not use a scroll timeline. DocumentTimeline::WillRefresh performs Tick. EnsurePaintIsScheduled only records/schedules a ready time; Pause does not synchronously call PauseAt. The probe checks pending and timeline timestamps before and after style flush rather than assuming every embedding preserves these conditions.

A numerical witness is cached timeline time R, start S=R-1920ms, playback rate 1, delay 2000ms, duration 10000ms and fill:none. Ordinary local time is 1920ms and progress is null. A composition timestamp corresponding to R+160ms gives 2080ms and a non-null progress of 0.008. Constant 20px endpoints make the sampled value exactly 20px, independent of the precise progress. The unanimated base is 80px. No transition, important declaration, pseudo, custom property, relative unit or additive operation is involved.

The held renderer candidate caches an in-effect property mask from ordinary timing and intersects normal composition with it. In this witness the mask omits margin-left even though the original renderer is about to sample it; the prototype would suppress the 20px sample. This is a source-level counterexample to a blanket equivalence premise. Browser reachability and exact observable values still require execution, with all setup checks passing.

## Probe and controls

Open standalone.html, or call `await runPendingTimingProbe(mode)` sequentially. The supported modes are:

| Mode | Timing construction | Predicted computed margin-left |
| --- | --- | --- |
| pending-cross | Pause pending; wallclock crosses delay; ordinary progress remains null |20px |
| pending-before | Pause pending, but wallclock estimate stays before delay |80px |
| running-cross | Same clock crossing without pending pause |80px |
| held-cross | Pause completed by explicit seek; real hold time persists |80px |

The source records ordinary current/start times, pending/play state, timing progress, target identity, rate, document timeline timestamp, performance time and two style reads. Setup validity is separate from style predictions. Any changed timeline time, completed pending state, altered current/start time, lost target, unexpected rate, unresolved preparation or wrong wallclock interval refuses interpretation. Each crossing blocks one task for approximately 160ms with a one-second wall-clock cap; it deliberately does not yield between pause and style read. Performance.now minus startTime is an approximate public-API clock projection, not a native TimeStamp capture; wide margins and direct state checks reduce timing ambiguity. Actual 20px with ordinary null progress is the decisive observation. A failure to reproduce with invalid setup is not evidence that the native state is impossible.

## Query helper is different

QUERY-INPUTS.json authenticates the exact active runtime capsule's copied source inputs; no live source files were read. ComposeServoAnimationRulesForMissingPseudo does not reject wallclock-pending animations. It captures one sampleTime and uses GetHoldTimeForComposition(&sampleTime) plus GetCurrentTimeForHoldTime when constructing each PreparedEffect.mTiming. It then samples those captured timings without advancing animation state. The privileged driver's wallclockPending field is diagnostic only; admission directly invokes the helper. Consequently inEffectAnimations can be 0 under ordinary timing while the helper still has a resolved prepared sample. Current fixtures with pending pauses establish some state-preservation coverage but do not prove this boundary-crossing example was reached.

The original renderer obtains its own wallclock sample inside each ComposeStyle call and temporarily mutates/restores hold time. The query helper uses one shared timestamp and owned prepared timing. Neither should be described as rejecting this state, nor should equality of their sampling instants across separate calls be assumed.

## Correct invariant and next decision

For each effect e in a composition transaction, let T(e) be the exact ComputedTiming used to compose its values, including selected hold time, timeline guard, normalized parameters, playback rate, boundary position and endpoint behavior. Under the proposed sampled-membership policy, the property-origin union must include a property's Animation-level effect precisely when that same T(e) can supply a sample. The union and the subsequent composition must consume the same T(e), not two independent wallclock queries. Current/relevant registration remains independent and must preserve future-playback/API/side effects.

Ordinary IsInEffect can replace this predicate only under an explicit equivalence premise: no alternate hold-time selection (or proof that it preserves progress nullness), matching endpoint behavior/normalization, matching unresolved-timeline treatment, and no intervening timing change. Those premises hold for the previous nonpending held fixture, not universally. Replacing IsInEffect by an ad hoc TimeStamp::Now query during cache refresh is still insufficient: a later ComposeStyle can cross a boundary after the cache was formed. A Pending fallback also needs invalidation when pending state changes and does not establish the intended policy.

The practical next implementation step is to reuse a captured composition-timing record for both membership and sampling in the query helper, where such a record already exists. A renderer repair requires an explicit transaction/cache contract that produces both origin rules from coherent timing and schedules invalidation; it must also preserve the separate all-relevant compositor eligibility union. Do not apply the held ordinary-IsInEffect candidate as a production fix. Normative origin-membership review, pending/endpoint coverage and the public CSSOM provider/debug gates remain separate.
