# WEB-ANIMATIONS-2#setting-the-timeline

**Setting the timeline of an animation** (heading)

**SHA**: hash:07b283f9ef260b80742e247ba6ed8cee8f0d3013c60bdaf43a7b2c536f52fc38

## Content

The procedure to **set the timeline of an animation**, *animation*, to *new timeline* which may be null, is as follows:

1.   Let *old timeline* be the current [timeline](https://drafts.csswg.org/web-animations-1/#timeline) of *animation*, if any.

2.   If *new timeline* is the same object as *old timeline*, abort this procedure.

3.   Let *previous play state* be *animation*’s [play state](https://www.w3.org/TR/web-animations-1/#animation-play-state).

4.   Let *previous current time* be the *animation*’s [current time](https://www.w3.org/TR/web-animations-1/#animation-current-time).

5.   Set *previous progress* based in the first condition that applies:

     If *previous current time* is unresolved:

     Set *previous progress* to unresolved.

     If [end time](https://drafts.csswg.org/web-animations-2#end-time) is zero:

     Set *previous progress* to zero.

     Otherwise

     Set *previous progress* = `*previous current time* /
     [end time](https://drafts.csswg.org/web-animations-2#end-time)`

6.   Let *from finite timeline* be true if *old timeline* is not null and not [monotonically increasing](https://drafts.csswg.org/web-animations-1/#monotonically-increasing-timeline).

7.   Let *to finite timeline* be true if *timeline* is not null and not [monotonically increasing](https://drafts.csswg.org/web-animations-1/#monotonically-increasing-timeline).

8.   Let the [timeline](https://drafts.csswg.org/web-animations-1/#timeline) of *animation* be *new timeline*.

9.   Perform the steps corresponding to the *first* matching condition from the following, if any:

     If *to finite timeline*,

     1.  [Apply any pending playback rate](https://drafts.csswg.org/web-animations-1/#apply-any-pending-playback-rate) on *animation*

     2.  set *auto align start time* to true.

     3.  Set [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) to unresolved.

     4.  Set [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) to unresolved.

     5.  If *previous play state* is "finished" or "running"

         1.  Schedule a [pending play task](https://drafts.csswg.org/web-animations-2#pending-play-task)
     6.  If *previous play state* is "paused" and *previous progress* is resolved:

         1.  Set [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) to *previous progress* \* [end time](https://drafts.csswg.org/web-animations-2#end-time).

     > **Note:** This step ensures that *previous progress* is preserved even in the case of a pause-pending animation with a resolved [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time).

     If *from finite timeline* and *previous progress* is resolved,

     Run the procedure to [set the current time](https://drafts.csswg.org/web-animations-2#set-the-current-time) to *previous progress* \* [end time](https://drafts.csswg.org/web-animations-2#end-time).

10.  If the [start time](https://www.w3.org/TR/web-animations-1/#animation-start-time) of *animation* is [resolved](https://drafts.csswg.org/web-animations-1/#unresolved), make *animation*’s [hold time](https://www.w3.org/TR/web-animations-1/#animation-hold-time) unresolved.

     > **Note:** This step ensures that the [finished play state](https://www.w3.org/TR/web-animations-1/#play-state-finished) of *animation* is not “sticky” but is re-evaluated based on its updated [current time](https://www.w3.org/TR/web-animations-1/#animation-current-time).

11.  Run the procedure to [update an animation’s finished state](https://drafts.csswg.org/web-animations-1/#update-an-animations-finished-state) for *animation* with the *did seek* flag set to false, and the *synchronously notify* flag set to false.

 Issue: If *new timeline* is null, we should ensure that [custom effects](https://drafts.csswg.org/web-animations-2#custom-effect) get called with an [unresolved](https://drafts.csswg.org/web-animations-1/#unresolved) [iteration progress](https://drafts.csswg.org/web-animations-1/#iteration-progress) (unless a subsequent change in the same script execution context makes this redundant).

## Navigation

- Parent: `animations` — Animations
- Next: `setting-the-target-effect` — Setting the target effect of an
  animation
- Children: 1
  - `animation-set-the-timeline-of-an-animation` — set the timeline of an animation

## Outgoing refs (3)

- WEB-ANIMATIONS-2#custom-effect
- WEB-ANIMATIONS-1#unresolved
- WEB-ANIMATIONS-1#iteration-progress

## Incoming refs (1)

- WEB-ANIMATIONS-2#contents

### Possible effects

WEB-ANIMATIONS-2#setting-the-timeline

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-2#setting-the-timeline" --format markdown`
