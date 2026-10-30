# Conditional repair options for deferred compositor requests

The smallest useful experiment, if the candidate trace supports the pending-without-dispatch hypothesis, is to allow an existing non-throttled entry to retry dispatch after traversal **and style refresh** have ended. Keep all inside-traversal behavior and the existing number of traversal passes unchanged. This is an unimplemented source proposal, not a concluded cause or a safe-to-land fix. The candidate trace was not inspected for this analysis.

The original's calibrated two callbacks and zero bounded witnesses are already recorded separately. The earlier uninstrumented candidate's failed fixed 2000 ms override controls motivate restoring external request progress. They do not supply a self-dependent fixed-point oracle or prove the pending-entry cause.

## What the current code actually records

`RequestRestyle` inserts a boolean false and changes it to true before calling `PostRestyleForAnimation`. The latter returns early during Servo traversal or PreTraverse. The boolean therefore also serves as “non-throttled work eligible for PreTraverse,” not solely proof that PresShell received a dispatch. A later request sees true and skips posting. `PreTraverseInSubtree` consumes eligible entries by posting explicit animation hints, preparing effects with `WillComposeStyle`, then removing the entries.

A simple change that resets the boolean to false on deferral is unsafe: `getNeededRestyleTarget` treats false as throttled and can skip it unless the flush-throttled condition holds. That would lose required second-pass animation work. Clearing the entry would lose it entirely. `HasPendingStyleUpdates` only checks whether the map is nonempty; it does not establish a scheduled root.

`StyleDocument` performs a first traversal and, if EffectCompositor PreTraverse finds work, a second traversal. It is not a fixed-point drain. `StyleNewSubtree` similarly performs a final animation-only traversal. The captured Rust `clear_state_after_traversing` clears animation restyle flags/damage on `FinalAnimationTraversal`. These facts make a final unconsumed request plausible, but neither this source trace nor the conditional Lean model proves which final-pass boundary the native candidate reaches.

## Minimal external retry experiment

Conceptually retain the existing exchange, and broaden the existing call condition only for an already-true entry:

```text
safeExternal = !IsInServoTraversal && !mIsInPreTraverse && !IsInStyleRefresh
if !skipRestyle || safeExternal:
    PostRestyleForAnimation(target, pseudo, cascade)
```

This condition belongs only in the existing non-throttled branch. It does not erase pending work, recursively traverse, automatically post on traversal exit, or add an iteration limit. The existing fresh-entry path is unchanged. A later explicit request can attempt posting even if the map still holds work from a completed traversal. `KeyframeEffect::NotifySpecifiedTimingUpdated` requests Layer, and `Animation::PostUpdate` also requests Layer; these are relevant seams for updateTiming and seek, but a Layer request is not by itself proof of an effective timing change or an external JS call.

The additional style-refresh predicate matters. `RestyleManager::DoProcessPendingRestyles` keeps `mInStyleRefresh` true across `StyleDocument`, post-traversal/frame handling, and its outer loop. `AutoSetInServoTraversal` clears the Servo flag before running post-traversal tasks. Thus outside-Servo/outside-PreTraverse is not equivalent to outside-style-refresh. `PostRestyleForAnimation` asserts that it is not in style refresh before the PresShell call. The new retry must not turn a previously coalesced request in that wider refresh scope into a dispatch. This analysis has not proved that every such request caller is reachable in the failing fixture.

The cost tradeoff is explicit: safe external requests also repost when a dispatch was already attempted. `PresShell::RestyleForAnimation` forwards to `RestyleManager::PostRestyleEvent`; for a nonzero hint, the latter increments the undisplayed-restyle generation before `Servo_NoteExplicitHints`. Duplicate requests are therefore not free even if downstream hints or roots coalesce. Retain existing restyle-count tests and measure batches of repeated updateTiming/seeks before a flush, plus literal/unchanged timings. A Layer-only retry is a narrower diagnostic variant, but it does not cover all non-throttled Standard requests and must not be presented as a general queue repair.

No synchronous loop is added by this experiment, but that is not a global termination proof. Existing outer restyle loops, future frame ticks and contextual feedback remain separate. Repeated reads must not be made to drive a new automatic drain. The safe external predicate deliberately does not promise progress for a pending entry without another eligible request or another ordinary restyle.

## More explicit state representation

A more principled design separates three states: throttled pending work, deferred non-throttled work, and work for which dispatch was attempted. PreTraverse must consider both non-throttled states eligible. A deferred request must remain deferred through additional inside-traversal requests; a safe later external request can attempt dispatch and then permit ordinary coalescing. A throttled request must not downgrade deferred/non-throttled work.

This needs consistent updates in RequestRestyle, PostRestyleForThrottledAnimations, PreTraverse eligibility/removal, and the header invariant. Direct callers of PostRestyleForAnimation also need review so dispatch status does not become stale. PresShell's void API supplies no proof that a new root was queued: name the state “dispatch attempted” unless a stronger result is exposed. Preserve the existing warning about map references being invalidated by posting; do not write through a saved table reference after a potentially mutating call. A return-status design must account for missing pseudo targets/disconnected contexts and safely reacquire any entry before a later update.

This representation can avoid redundant external posts while retaining traversal eligibility. It is a larger change than the diagnostic retry and needs a complete caller/state-transition review. The isolated protocol model can prove conditional queue properties, but it cannot establish these native call-path and root-scheduling obligations by itself.

## Options to avoid

- Looping PreTraverse/StyleDocument until the map is empty would turn self-dependent duration/font updates into a possible synchronous feedback drain.
- Posting every leftover entry after the final traversal can create perpetual work across refreshes for paused self-feedback; moving a loop to future frames does not define its semantics.
- An arbitrary traversal/iteration cap does not choose a valid duration or preserve fixed script-owned timing.
- Special-casing the test target, forcing the literal value, or weakening the callback oracle would hide the regression.

Before any publication, a repair experiment must preserve the two fixed script/literal controls, stable identity/current membership, seek out-and-back behavior, inactive-but-specified duration reactivation, ordinary ancestor-driven timing, updateTiming ownership and rejection, existing restyle counts, and current source/app restoration. Self-feedback observations remain measurements. A trace may support the queue hypothesis without resolving the CSS self-dependency policy.

`SOURCE-EXCERPTS.json` contains complete named functions extracted from full fetched upstream files and exact locally changed source captures, plus their source hashes. The local EffectCompositor base is already authenticated by the sealed logger package. ServoStyleSet/RestyleManager upstream analysis still requires exact branch applicability/preimage binding before any native patch. Initial sandbox DNS failures were resolved by read-only escalated Searchfox fetches; an old RestyleManager path returned 404 and was corrected via identifier search. No native implementation, browser/build, live-state guard, Git/index, app or canonical mutation was performed.
