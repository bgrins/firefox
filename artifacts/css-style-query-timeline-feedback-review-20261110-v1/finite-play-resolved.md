# WEB-ANIMATIONS-2#playing-an-animation-section

**Playing an animation** (heading)

**SHA**: hash:07b283f9ef260b80742e247ba6ed8cee8f0d3013c60bdaf43a7b2c536f52fc38

## Content

The procedure to **play an animation**, *animation*, given a flag *auto-rewind*, is as follows:

> **Note:** Note: The *auto-rewind* flag is provided for other specifications that build on this model but do not require the rewinding behavior, such as CSS Animations \[CSS-ANIMATIONS-1\].

1.   Let *aborted pause* be a boolean flag that is true if *animation* has a [pending pause task](https://drafts.csswg.org/web-animations-1/#pending-pause-task), and false otherwise.

2.   Let *has pending ready promise* be a boolean flag that is initially false.

3.   Let *has finite timeline* be true if *animation* has an associated [timeline](https://drafts.csswg.org/web-animations-1/#timeline) that is not [monotonically increasing](https://drafts.csswg.org/web-animations-1/#monotonically-increasing-timeline).

4.   Let *previous current time* be the *animation*’s [current time](https://www.w3.org/TR/web-animations-1/#animation-current-time)

5.   Let *enable seek* be true if the *auto-rewind* flag is true and *has finite timeline* is false. Otherwise, initialize to false.

6.   Perform the steps corresponding to the *first* matching condition from the following, if any:

     If *animation*’s [effective playback rate](https://drafts.csswg.org/web-animations-1/#effective-playback-rate) > 0, *enable seek* is true and *either* *animation*’s:

     *   *previous current time* is [unresolved](https://drafts.csswg.org/web-animations-1/#unresolved), or

     *   *previous current time* < zero, or

     *   *previous current time* ≥ [associated effect end](https://drafts.csswg.org/web-animations-1/#associated-effect-end),

     Set the *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) to zero.

     If *animation*’s [effective playback rate](https://drafts.csswg.org/web-animations-1/#effective-playback-rate) < 0, *enable seek* is true and *either* *animation*’s:

     *   *previous current time* is [unresolved](https://drafts.csswg.org/web-animations-1/#unresolved), or

     *   *previous current time* ≤ zero, or

     *   *previous current time* > [associated effect end](https://drafts.csswg.org/web-animations-1/#associated-effect-end),

     If [associated effect end](https://drafts.csswg.org/web-animations-1/#associated-effect-end) is positive infinity,

     [throw](https://webidl.spec.whatwg.org/#dfn-throw) an "[`InvalidStateError`](https://webidl.spec.whatwg.org/#invalidstateerror)" [`DOMException`](https://webidl.spec.whatwg.org/#idl-DOMException) and abort these steps.

     Otherwise,

     Set the *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) to the *animation*’s [associated effect end](https://drafts.csswg.org/web-animations-1/#associated-effect-end).

     If *animation*’s [effective playback rate](https://drafts.csswg.org/web-animations-1/#effective-playback-rate) = 0 and *animation*’s [current time](https://www.w3.org/TR/web-animations-1/#animation-current-time) is [unresolved](https://drafts.csswg.org/web-animations-1/#unresolved),

     Set the *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) to zero.

7.   If *has finite timeline* and *auto-rewind* is true:

     1.  Set the flag *auto align start time* to true.

     2.  Set the *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) to *previous current time*.

     > **Note:** Note: If play is called for a CSS animation during style update, the *animation*’s [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) cannot be reliably calculated until post layout since the start time is to align with the start or end of the animation range (depending on the [playback rate](https://drafts.csswg.org/web-animations-2#animation-effect-playback-rate)). In this case, the animation is said to have an **auto-aligned start time**, whereby the start time is automatically adjusted as needed to align the animation’s progress to the animation range.

8.   If *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) is [resolved](https://drafts.csswg.org/web-animations-1/#unresolved), let its [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) be unresolved.

9.   If *animation* has a [pending play task](https://drafts.csswg.org/web-animations-2#pending-play-task) or a [pending pause task](https://drafts.csswg.org/web-animations-1/#pending-pause-task),

     1.  Cancel that task.

     2.  Set *has pending ready promise* to true.
10.  If the following three conditions are *all* satisfied:

     *   *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) is [unresolved](https://drafts.csswg.org/web-animations-1/#unresolved), and

     *   *aborted pause* is false, and

     *   *animation* does *not* have a [pending playback rate](https://drafts.csswg.org/web-animations-1/#pending-playback-rate),
     abort this procedure.

11.  If *has pending ready promise* is false, let *animation*’s [current ready promise](https://drafts.csswg.org/web-animations-1/#current-ready-promise) be [a new promise](https://webidl.spec.whatwg.org/#a-new-promise) in the [relevant Realm](https://html.spec.whatwg.org/multipage/webappapis.html#concept-relevant-realm) of *animation*.

12.  Schedule a task to run as soon as *animation* is [ready](https://drafts.csswg.org/web-animations-2#ready). The task shall perform the following steps:

     1.  Assert that at least one of *animation*’s [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) or [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) is [resolved](https://drafts.csswg.org/web-animations-1/#unresolved).

     2.  Let *ready time* be the [time value](https://drafts.csswg.org/web-animations-1/#time-value) of the [timeline](https://drafts.csswg.org/web-animations-1/#timeline) associated with *animation* at the moment when *animation* became [ready](https://drafts.csswg.org/web-animations-2#ready).

     3.  Perform the steps corresponding to the first matching condition below, if any:

         If *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) is [resolved](https://drafts.csswg.org/web-animations-1/#unresolved),

         1.  [Apply any pending playback rate](https://drafts.csswg.org/web-animations-1/#apply-any-pending-playback-rate) on *animation*.

         2.  Let *new start time* be the result of evaluating `*ready time* - [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) / [playback rate](https://drafts.csswg.org/web-animations-2#animation-effect-playback-rate)` for *animation*. If the [playback rate](https://drafts.csswg.org/web-animations-2#animation-effect-playback-rate) is zero, let *new start time* be simply *ready time*.

         3.  Set the [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) of *animation* to *new start time*.

         4.  If *animation*’s [playback rate](https://drafts.csswg.org/web-animations-2#animation-effect-playback-rate) is not 0, make *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) [unresolved](https://drafts.csswg.org/web-animations-1/#unresolved).

         If *animation*’s [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) is resolved and *animation* has a [pending playback rate](https://drafts.csswg.org/web-animations-1/#pending-playback-rate),

         1.  Let *current time to match* be the result of evaluating `(*ready time* - [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time)) ×
             [playback rate](https://drafts.csswg.org/web-animations-2#animation-effect-playback-rate)` for *animation*.

         2.  [Apply any pending playback rate](https://drafts.csswg.org/web-animations-1/#apply-any-pending-playback-rate) on *animation*.

         3.  If *animation*’s [playback rate](https://drafts.csswg.org/web-animations-2#animation-effect-playback-rate) is zero, let *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) be *current time to match*.

         4.  Let *new start time* be the result of evaluating `*ready time* - *current time to match* /
             [playback rate](https://drafts.csswg.org/web-animations-2#animation-effect-playback-rate)` for *animation*. If the [playback rate](https://drafts.csswg.org/web-animations-2#animation-effect-playback-rate) is zero, let *new start time* be simply *ready time*.

         5.  Set the [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) of *animation* to *new start time*.

     4.  [Resolve](https://webidl.spec.whatwg.org/#resolve) *animation*’s [current ready promise](https://drafts.csswg.org/web-animations-1/#current-ready-promise) with *animation*.

     5.  Run the procedure to [update an animation’s finished state](https://drafts.csswg.org/web-animations-1/#update-an-animations-finished-state) for *animation* with the *did seek* flag set to false, and the *synchronously notify* flag set to false.

         > **Note:** Note that the order of the above two steps is important since it means that an animation with zero-length [associated effect](https://www.w3.org/TR/web-animations-1/#animation-associated-effect) will resolve its [current ready promise](https://drafts.csswg.org/web-animations-1/#current-ready-promise) before its [current finished promise](https://drafts.csswg.org/web-animations-1/#current-finished-promise).
     So long as the above task is scheduled but has yet to run, *animation* is described as having a **pending play task**. While the task is running, however, *animation* does *not* have a [pending play task](https://drafts.csswg.org/web-animations-2#pending-play-task).

     If a user agent determines that *animation* is immediately [ready](https://drafts.csswg.org/web-animations-2#ready), it may schedule the above task as a microtask such that it runs at the next [microtask checkpoint](https://html.spec.whatwg.org/multipage/webappapis.html#perform-a-microtask-checkpoint), but it must *not* perform the task synchronously.

     > **Note:** The above requirement to run the [pending play task](https://drafts.csswg.org/web-animations-2#pending-play-task) asynchronously ensures that code such as the following behaves consistently between implementations:
     >
     > > **Example:** ```
     > > animation.play();
     > > animation.ready.then(
     > >   () => { console.log('Playback commenced'); },
     > >   () => { console.log('Playback was canceled'); }
     > > );
     > > // Suppose some condition requires playback to be canceled...
     > > animation.cancel();
     > > // "Playback was canceled" will be printed to the console.
     > > ```
     >
     > In the above code, were the [pending play task](https://drafts.csswg.org/web-animations-2#pending-play-task) run synchronously, the [current ready promise](https://drafts.csswg.org/web-animations-1/#current-ready-promise) would not be rejected.

13.  Run the procedure to [update an animation’s finished state](https://drafts.csswg.org/web-animations-1/#update-an-animations-finished-state) for *animation* with the *did seek* flag set to false, and the *synchronously notify* flag set to false.

> **Issue:** The procedure to [play an animation](https://drafts.csswg.org/web-animations-2#play-an-animation) needs to include scheduling a task for updating [custom effects](https://drafts.csswg.org/web-animations-2#custom-effect).

##### Auto-aligning the start time

When attached to a non-monotonic timeline, the start time of the animation may be layout dependent. In this case, we defer calculation of the start time until the timeline has been updated post layout. When updating timeline current time, the [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) of any attached animation is conditionally updated. The procedure for **calculating an auto-aligned start time** is as follows:

1.  If the *auto-align start time* flag is false, abort this procedure.

2.  If the timeline is inactive, abort this procedure.

3.  If [play state](https://www.w3.org/TR/web-animations-1/#animation-play-state) is idle, abort this procedure.

4.  If [play state](https://www.w3.org/TR/web-animations-1/#animation-play-state) is paused, and [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) is resolved, abort this procedure.

5.  Let *start offset* be the resolved timeline time corresponding to the start of the [animation attachment range](https://www.w3.org/TR/scroll-animations-1/#animation-attachment-range). In the case of view timelines, it requires a calculation based on the proportion of the cover range.

6.  Let *end offset* be the resolved timeline time corresponding to the end of the [animation attachment range](https://www.w3.org/TR/scroll-animations-1/#animation-attachment-range). In the case of view timelines, it requires a calculation based on the proportion of the cover range.

7.  Set [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) to *start offset* if [effective playback rate](https://drafts.csswg.org/web-animations-1/#effective-playback-rate) ≥ 0, and *end offset* otherwise.

8.  [Apply any pending playback rate](https://drafts.csswg.org/web-animations-1/#apply-any-pending-playback-rate) on *animation*.

9.  Clear [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time).

## Navigation

- Parent: `animations` — Animations
- Prev: `setting-the-start-time-of-an-animation` — Setting the start time of an
Animation
- Next: `pausing-an-animation-section` — Pausing an animation
- Children: 4
  - `play-an-animation` — play an animation
  - `animation-auto-aligned-start-time` — auto-aligned start
time
  - `pending-play-task` — pending play task
  - `auto-aligning-start-time` — Auto-aligning the start time

## Outgoing refs (28)

`webspec-index refs WEB-ANIMATIONS-2#playing-an-animation-section -d outgoing -l 28`

## Incoming refs (1)

- WEB-ANIMATIONS-2#contents

### Possible effects

WEB-ANIMATIONS-2#playing-an-animation-section

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-2#playing-an-animation-section" --format markdown`
