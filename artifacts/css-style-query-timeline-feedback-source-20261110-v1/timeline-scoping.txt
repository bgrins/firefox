# SCROLL-ANIMATIONS-1#timeline-scoping

**Named Timeline Scoping and Lookup** (heading)

**SHA**: hash:ad85f897511e9ba33b2f23988fb363daafb993574d37c7fd11491ee2ec00a7c9

## Content

Timeline names are global by default: An element referring to a named [scroll progress timeline](https://drafts.csswg.org/scroll-animations-1#scroll-progress-timelines) or [view progress timeline](https://drafts.csswg.org/scroll-animations-1#view-progress-timelines) can find a [target timeline](https://drafts.csswg.org/scroll-animations-1#target-timeline) defined on itself, defined on an element *before* itself in tree order, or defined on an element *after* itself in tree order.

The **target timeline** for a given element *element* referencing a timeline name *name* is:

If *element* defines a timeline matching *name*, 

That timeline.

Otherwise, if *name* is [scoped](https://drafts.csswg.org/scroll-animations-1#timeline-scope) by *element*, or if *element* is the [document element](https://dom.spec.whatwg.org/#document-element), 

The last defined timeline matching *name* among *element*’s [flat tree](https://drafts.csswg.org/css-shadow-1/#flat-tree) descendants in flat tree order, or, if no such timeline exists, an [inactive timeline](https://drafts.csswg.org/web-animations-1/#inactive-timeline).

Otherwise, 

The [target timeline](https://drafts.csswg.org/scroll-animations-1#target-timeline) for *element*’s [flat tree](https://drafts.csswg.org/css-shadow-1/#flat-tree) parent referencing *name*.

An element may only define one timeline per name: In case of a name conflict, names declared later in the naming property ([scroll-timeline-name](https://drafts.csswg.org/scroll-animations-1#propdef-scroll-timeline-name), [view-timeline-name](https://drafts.csswg.org/scroll-animations-1#propdef-view-timeline-name)) take precedence, and [scroll progress timelines](https://drafts.csswg.org/scroll-animations-1#scroll-progress-timelines) take precedence over [view progress timelines](https://drafts.csswg.org/scroll-animations-1#view-progress-timelines).

> **Example:** The element `#foo` defines a single [scroll progress timeline](https://drafts.csswg.org/scroll-animations-1#scroll-progress-timelines) in the block direction named `--t`, and no [view progress timeline](https://drafts.csswg.org/scroll-animations-1#view-progress-timelines) at all.
>
> ```
> #foo {
>   scroll-timeline: --t inline, --t block;
>   view-timeline: --t;
> }
> ```

> **Example:** An element can refer to timelines bound to elements that are siblings, cousins, or even descendants. For example, the following creates an animation on an element that is linked to a [scroll progress timeline](https://drafts.csswg.org/scroll-animations-1#scroll-progress-timelines) defined by the subsequent sibling.
>
> ```
> <style>
>   @keyframes anim {
>     from { color: red; }
>     to { color: green; }
>   }
>
>   .root {
>     /* declares the scope of a '--scroller' timeline to reach all descendants */
>     timeline-scope: --scroller;
>   }
>
>   .root .animation {
>     animation: anim;
>     /* references the '--scroller' timeline for driving the progress of 'anim' */
>     animation-timeline: --scroller;
>   }
>
>   .root .animation + .scroller {
>     /* attaches a scroll progress timeline to the timeline named '--scroller' */
>     scroll-timeline: --scroller;
>   }
> </style>
> &hellip;
> <section class="root">
>   <div class="animation">Animating Box</div>
>   <div class="scroller">Scrollable Box</div>
> </section>
> ```

## Navigation

- Parent: `scroll-driven-attachment` — Attaching Animations to Scroll-driven Timelines
- Prev: `finite-attachment` — Finite Timeline Calculations
- Next: `events` — Animation Events
- Children: 1
  - `target-timeline` — target timeline

## Outgoing refs (9)

`webspec-index refs SCROLL-ANIMATIONS-1#timeline-scoping -d outgoing -l 9`

## Incoming refs (5)

`webspec-index refs SCROLL-ANIMATIONS-1#timeline-scoping -d incoming -l 5`

### Possible effects

SCROLL-ANIMATIONS-1#timeline-scoping

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "SCROLL-ANIMATIONS-1#timeline-scoping" --format markdown`
