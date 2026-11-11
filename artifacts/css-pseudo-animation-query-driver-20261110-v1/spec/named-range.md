# SCROLL-ANIMATIONS-1#named-range-keyframes

**Named Timeline Range Keyframe Selectors** (heading)

**SHA**: hash:ad85f897511e9ba33b2f23988fb363daafb993574d37c7fd11491ee2ec00a7c9

## Content

[Named timeline range](SCROLL-ANIMATIONS-1#named-timeline-range) names and percentages can be used to attach keyframes to specific progress points within the named timeline range. The CSS [@keyframes](CSS-ANIMATIONS-1#at-ruledef-keyframes) rule is extended thus:

```
<keyframe-selector> = from | to | <percentage [0,100]> | <timeline-range-name> <percentage>
```

where [\<timeline-range-name>](SCROLL-ANIMATIONS-1#typedef-timeline-range-name) is the [CSS identifier](CSS-VALUES-4#css-css-identifier) that represents a chosen predefined [named timeline range](SCROLL-ANIMATIONS-1#named-timeline-range), and the [\<percentage>](CSS-VALUES-4#percentage-value) after it represents the percentage progress between the start and end of that named timeline range.

Keyframes are attached to the specified point in the timeline. If the timeline does not have a corresponding [named timeline range](SCROLL-ANIMATIONS-1#named-timeline-range), then any keyframes attached to points on that named timeline range are ignored. It is possible that these attachment points are outside the [active interval](WEB-ANIMATIONS-1#active-interval) of the animation; in these cases the automatic from (0%) and [to](CSS-SHAPES-1#valdef-shape-to) (100%) keyframes are only generated for properties that don’t have keyframes at or earlier than 0% or at or after 100% (respectively).

> **Example:** In this example the range information is included directly in the [@keyframes](CSS-ANIMATIONS-1#at-ruledef-keyframes) rule:
>
> ```
> @keyframes animate-in-and-out {
>   entry 0%  {
>     opacity: 0; transform: translateY(100%);
>   }
>   entry 100%  {
>     opacity: 1; transform: translateY(0);
>   }
>
>   exit 0% {
>     opacity: 1; transform: translateY(0);
>   }
>   exit 100% {
>     opacity: 0; transform: translateY(-100%);
>   }
> }
>
> .scroller > * {
>   animation: linear animate-in-and-out;
>   animation-timeline: view();
> }
> ```
>
> It has the same outcome as the following snippet which uses two distinct sets of keyframes combined with [animation-range](SCROLL-ANIMATIONS-1#propdef-animation-range)
>
> ```
> @keyframes animate-in {
>   0% { opacity: 0; transform: translateY(100%); }
>   100% { opacity: 1; transform: translateY(0); }
> }
>
> @keyframes animate-out {
>   0% { opacity: 1; transform: translateY(0); }
>   100% { opacity: 0; transform: translateY(-100%); }
> }
>
> .scroller > * {
>   animation: animate-in linear forwards,
>         animate-out linear forwards;
>   animation-timeline: view();
>   animation-range: entry, exit;
> }
> ```

## Navigation

- Parent: `timeline-ranges` — Appendix A: Timeline Ranges
- Prev: `named-ranges` — Named Timeline Ranges
- Next: `named-range-animation-declaration` — Attaching Animations to Timeline Ranges

## Outgoing refs (10)

`webspec-index refs SCROLL-ANIMATIONS-1#named-range-keyframes -d outgoing -l 10`

## Incoming refs (5)

`webspec-index refs SCROLL-ANIMATIONS-1#named-range-keyframes -d incoming -l 5`

### Possible effects

SCROLL-ANIMATIONS-1#named-range-keyframes

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "SCROLL-ANIMATIONS-1#named-range-keyframes" --format markdown`
