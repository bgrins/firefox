# WEB-ANIMATIONS-2#auto-aligning-start-time

**Auto-aligning the start time** (heading)

**SHA**: hash:07b283f9ef260b80742e247ba6ed8cee8f0d3013c60bdaf43a7b2c536f52fc38

## Content

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

- Parent: `playing-an-animation-section` — Playing an animation
- Children: 1
  - `animation-calculating-an-auto-aligned-start-time` — calculating an auto-aligned start time

## Outgoing refs (1)

- WEB-ANIMATIONS-1#animation-start-time

## Incoming refs (1)

- WEB-ANIMATIONS-2#contents

### Possible effects

WEB-ANIMATIONS-2#auto-aligning-start-time

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-2#auto-aligning-start-time" --format markdown`
