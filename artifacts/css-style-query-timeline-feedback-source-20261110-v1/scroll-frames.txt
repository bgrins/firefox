# SCROLL-ANIMATIONS-1#frames

**Frame Calculation Details** (heading)

**SHA**: hash:ad85f897511e9ba33b2f23988fb363daafb993574d37c7fd11491ee2ec00a7c9

## Content

### HTML Processing Model: Event loop

The ability for scrolling to drive the progress of an animation, gives rise to the possibility of **layout cycles**, where a change to a scroll offset causes an animation’s effect to update, which in turn causes a new change to the scroll offset.

To avoid such [layout cycles](https://drafts.csswg.org/scroll-animations-1#layout-cycles), animations with a [scroll progress timeline](https://drafts.csswg.org/scroll-animations-1#scroll-progress-timelines) update their current time once during step 7.10 of the [HTML Processing Model](https://html.spec.whatwg.org/multipage/webappapis.html#processing-model-8) event loop, as step 1 of [update animations and send events](https://drafts.csswg.org/web-animations-1/#update-animations-and-send-events).

During step 7.14.1 of the [HTML Processing Model](https://html.spec.whatwg.org/multipage/webappapis.html#processing-model-8), any created [scroll progress timelines](https://drafts.csswg.org/scroll-animations-1#scroll-progress-timelines) or [view progress timelines](https://drafts.csswg.org/scroll-animations-1#view-progress-timelines) are collected into a **stale timelines** set. After step 7.14 if any timelines' [named timeline ranges](https://drafts.csswg.org/scroll-animations-1#named-timeline-range) have changed, these timelines are added to the [stale timelines](https://drafts.csswg.org/scroll-animations-1#stale-timelines) set. If there are any stale timelines, they now update their current time and associated ranges, the set of stale timelines is cleared and we run an additional step to recalculate styles and update layout.

> **Note:** Note: We check for layout changes after dispatching any [`ResizeObserver`](https://drafts.csswg.org/resize-observer-1/#resizeobserver)s intentionally to take programmatically sized elements into account.

> **Note:** Note: As we only gather stale timelines during the first style and layout calculation, this can only directly cause one additional style recalculation. Other APIs which require another update should be checked in the same step and be updated at the same time.

> **Note:** Note: Without this additional round of style and layout, [initially stale](https://drafts.csswg.org/scroll-animations-1#stale-timelines) timelines would remain stale (i.e. they would not have a current time) for the remainder of the frame where the timeline was created. This means that animations linked to such a timeline would not produce any [effect value](https://drafts.csswg.org/web-animations-1/#effect-value) for that frame, which could lead to an undesirable initial "flash" in the rendered output.

> **Note:** Note: This section has no effect on forced style and layout calculations triggered by [`getComputedStyle()`](https://drafts.csswg.org/cssom-1/#dom-window-getcomputedstyle) or similar. In other words, [initially stale](https://drafts.csswg.org/scroll-animations-1#stale-timelines) timelines are visible as such through those APIs.

If the final style and layout update would result in a change in the time or scope (see [timeline-scope](https://drafts.csswg.org/scroll-animations-1#propdef-timeline-scope)) of any [scroll progress timelines](https://drafts.csswg.org/scroll-animations-1#scroll-progress-timelines) or [view progress timelines](https://drafts.csswg.org/scroll-animations-1#view-progress-timelines), they will not be re-sampled to reflect the new state until the next update of the rendering.

Nothing in this section is intended to require that scrolling block on layout or script. If a user agent normally composites frames where scrolling has occurred but the consequences of scrolling have not been fully propagated in layout or script (for example, `scroll` event listeners have not yet run), the user agent may likewise choose not to sample scroll-driven animations for that composited frame. In such cases, the rendered scroll offset and the state of a scroll-driven animation may be inconsistent in the composited frame.

When updating timeline current time, the [start time](https://drafts.csswg.org/web-animations-1/#animation-start-time) of any attached animation is conditionally updated. For each attached animation, run the procedure for [calculating an auto-aligned start time](https://drafts.csswg.org/web-animations-2/#calculating-an-auto-aligned-start-time).

## Navigation

- Prev: `scroll-driven-attachment` — Attaching Animations to Scroll-driven Timelines
- Next: `privacy-considerations` — Privacy Considerations
- Children: 1
  - `event-loop` — HTML Processing Model: Event loop

## Incoming refs (1)

- SCROLL-ANIMATIONS-1#contents

### Possible effects

SCROLL-ANIMATIONS-1#frames

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "SCROLL-ANIMATIONS-1#frames" --format markdown`
