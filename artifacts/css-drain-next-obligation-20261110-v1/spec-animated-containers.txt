# CSS-CONDITIONAL-5#animated-containers

**Animated Containers** (heading)

**SHA**: hash:fb5563dd1884e6564cd915db8b3d8e218c9937747e071c989cf4bcc19b8d27e6

## Content

A change in the evaluation of a [container query](https://drafts.csswg.org/css-conditional-5#container-query) must be part of a [style change event](https://drafts.csswg.org/css-transitions-1/#style-change-event), even when the change occurred because of [animation effects](https://drafts.csswg.org/web-animations-1/#effect-value).

> **Example:** A transition on a sibling element can indirectly affect the size of a container, triggering [style change events](https://drafts.csswg.org/css-transitions-1/#style-change-event) whenever container queries change their evaluation as a result:
>
> ```
> main {
>   display: flex;
>   width: 300px;
> }
>
> #container {
>   container-type: inline-size;
>   flex: 1;
> }
>
> /* Resolved width is initially 200px, but changes as the transition
>    on #sibling progresses. */
> #inner {
>   transition: 1s background-color;
>   background-color: tomato;
> }
>
> /* When this container query starts (or stops) applying, a transition
>    must start on background-color on #inner. */
> @container (width <= 150px) {
>   #inner {
>   background-color: skyblue;
>   }
> }
>
> #sibling {
>   width: 100px;
>   transition: width 1s;
> }
>
> #sibling:hover {
>   width: 200px;
> }
> ```
>
> ```
> <main>
>   <div id=container>
>   <div id=inner>Inner</div>
>   </div>
>   <div id=sibling>Sibling</div>
> </main>
> ```

Changes in [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value) caused by [container query length](https://drafts.csswg.org/css-conditional-5#container-query-length) units must also be part of a [style change event](https://drafts.csswg.org/css-transitions-1/#style-change-event).

## Navigation

- Parent: `container-queries` — Container Queries
- Prev: `container-rule` — Container Queries: the @container rule

## Outgoing refs (5)

`webspec-index refs CSS-CONDITIONAL-5#animated-containers -d outgoing -l 5`

## Incoming refs (1)

- CSS-CONDITIONAL-5#contents

### Possible effects

CSS-CONDITIONAL-5#animated-containers

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-CONDITIONAL-5#animated-containers" --format markdown`
