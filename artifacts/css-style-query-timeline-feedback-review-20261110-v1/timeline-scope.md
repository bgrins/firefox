# SCROLL-ANIMATIONS-1#timeline-scope

**Declaring a Named Timeline’s Scope: the timeline-scope property** (heading)

**SHA**: hash:ad85f897511e9ba33b2f23988fb363daafb993574d37c7fd11491ee2ec00a7c9

## Content

| Name:                                                                                                                                                                                                                                                                             |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| none [&#124;](CSS-VALUES-4#comb-one) all &#124; [\<dashed-ident>](CSS-VALUES-4#typedef-dashed-ident)[#](CSS-VALUES-4#mult-comma)                                                                    |
| none                                                                                                                                                                                                                                                                              |
| [all elements](CSS-PSEUDO#generated-content)                                                                                                                                                                                                               |
| no                                                                                                                                                                                                                                                                                |
| n/a                                                                                                                                                                                                                                                                               |
| the keyword [none](SCROLL-ANIMATIONS-1#valdef-timeline-scope-none), the keyword [all](SCROLL-ANIMATIONS-1#valdef-timeline-scope-all), or a list of [CSS identifiers](CSS-VALUES-4#css-css-identifier) |
| per grammar                                                                                                                                                                                                                                                                       |
| not animatable                                                                                                                                                                                                                                                                    |

Values have the following meanings:

**none** 

No changes in timeline name scope.

**all** 

Specifies that all timeline names defined by this element or its [flat tree](CSS-SHADOW-1#flat-tree) descendants—​whose scope is not already limited by a descendant using [timeline-scope](SCROLL-ANIMATIONS-1#propdef-timeline-scope)—​to be in scope only for this element’s flat tree descendants; and limits descendants to only match timeline names to elements within this subtree.

**[\<dashed-ident>](CSS-VALUES-4#typedef-dashed-ident)** 

Specifies that a matching timeline name defined by this element or its [flat tree](CSS-SHADOW-1#flat-tree) descendants—​whose scope is not already limited by a descendant using [timeline-scope](SCROLL-ANIMATIONS-1#propdef-timeline-scope)—​to be in scope only for this element’s flat tree descendants; and limits descendants to only match timeline names to elements within this subtree.

> **Note:** Note: This property cannot affect or invalidate any timeline name lookups within the subtree of a descendant element that declares the same name. See [Declaring a Named Timeline’s Scope: the timeline-scope property](SCROLL-ANIMATIONS-1#timeline-scope).

> **Example:** Say you have multiple instances of a component, each defining a timeline and some element using that timeline:
>
> ```
> <div>
>   <div class="component">
>     <div style="view-timeline: --t /*...*/;"></div>
>     <div style="animation-timeline: --t;"></div>
>   </div>
>   <div class="component">
>     <div style="view-timeline: --t /*...*/;"></div>
>     <div style="animation-timeline: --t;"></div>
>   </div>
> </div>
> ```
>
> Both instances of `animation-timeline:--t` will [target](SCROLL-ANIMATIONS-1#target-timeline) the *same* timeline, i.e. the last one seen in [flat tree](CSS-SHADOW-1#flat-tree) order, globally.
>
> If we instead want each instance of `animation-timeline:--t` to [target](SCROLL-ANIMATIONS-1#target-timeline) the "locally defined" `--t`, we can do the following:
>
> ```
> <style>
>   .component {
>     timeline-scope: --t;
>   }
> </style>
> ```
>
> Now, any lookup of `--t` taking place within a component will only see timelines defined inside that component.

## Navigation

- Parent: `timeline-name-scope` — Appendix B: Timeline Name Scope
- Children: 4
  - `propdef-timeline-scope` — timeline-scope
  - `valdef-timeline-scope-none` — none
  - `valdef-timeline-scope-all` — all
  - `valdef-timeline-scope-dashed-ident` — <dashed-ident>

## Outgoing refs (19)

`webspec-index refs SCROLL-ANIMATIONS-1#timeline-scope -d outgoing -l 19`

## Incoming refs (4)

- CSS-ANIMATIONS-2#animation-timeline
- SCROLL-ANIMATIONS-1#contents
- SCROLL-ANIMATIONS-1#timeline-scope
- SCROLL-ANIMATIONS-1#timeline-scoping

### Possible effects

SCROLL-ANIMATIONS-1#timeline-scope

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "SCROLL-ANIMATIONS-1#timeline-scope" --format markdown`
