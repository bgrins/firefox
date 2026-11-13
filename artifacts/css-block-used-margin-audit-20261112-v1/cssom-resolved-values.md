# CSSOM#resolved-values

**Resolved Values** (heading)

**SHA**: hash:8dc3488fb459e8695d13423686790d285f3fed477bd84fa0e49b7e4aa310923d

## Content

[`getComputedStyle()`](CSSOM#dom-window-getcomputedstyle) was historically defined to return the "computed value" of an element or pseudo-element. However, the concept of "computed value" changed between revisions of CSS while the implementation of [`getComputedStyle()`](CSSOM#dom-window-getcomputedstyle) had to remain the same for compatibility with deployed scripts. To address this issue this specification introduces the concept of a **resolved value**.

The [resolved value](CSSOM#resolved-value) for a given longhand property can be determined as follows:

[background-color](CSS-BACKGROUNDS-3#propdef-background-color) 

[border-block-end-color](CSS-BORDERS-4#propdef-border-block-end-color) 

[border-block-start-color](CSS-BORDERS-4#propdef-border-block-start-color) 

[border-bottom-color](CSS-BORDERS-4#propdef-border-bottom-color) 

[border-inline-end-color](CSS-BORDERS-4#propdef-border-inline-end-color) 

[border-inline-start-color](CSS-BORDERS-4#propdef-border-inline-start-color) 

[border-left-color](CSS-BORDERS-4#propdef-border-left-color) 

[border-right-color](CSS-BORDERS-4#propdef-border-right-color) 

[border-top-color](CSS-BORDERS-4#propdef-border-top-color) 

[box-shadow](CSS-BORDERS-4#propdef-box-shadow) 

[caret-color](CSS-UI-4#propdef-caret-color) 

[color](CSS-COLOR-4#propdef-color) 

[outline-color](CSS-UI-4#propdef-outline-color) 

A **resolved value special case property like [color](CSS-COLOR-4#propdef-color)** defined in another specification 

The [resolved value](CSSOM#resolved-value) is the [used value](CSS-CASCADE-5#used-value).

[line-height](CSS2#propdef-line-height) 

The [resolved value](CSSOM#resolved-value) is [normal](CSS-INLINE-3#valdef-line-height-normal) if the [computed value](CSS-CASCADE-5#computed-value) is normal, or the [used value](CSS-CASCADE-5#used-value) otherwise.

[block-size](CSS-LOGICAL-1#propdef-block-size) 

[height](CSS-SIZING-3#propdef-height) 

[inline-size](CSS-LOGICAL-1#propdef-inline-size) 

[margin-block-end](CSS-LOGICAL-1#propdef-margin-block-end) 

[margin-block-start](CSS-LOGICAL-1#propdef-margin-block-start) 

[margin-bottom](CSS-BOX-4#propdef-margin-bottom) 

[margin-inline-end](CSS-LOGICAL-1#propdef-margin-inline-end) 

[margin-inline-start](CSS-LOGICAL-1#propdef-margin-inline-start) 

[margin-left](CSS-BOX-4#propdef-margin-left) 

[margin-right](CSS-BOX-4#propdef-margin-right) 

[margin-top](CSS-BOX-4#propdef-margin-top) 

[padding-block-end](CSS-LOGICAL-1#propdef-padding-block-end) 

[padding-block-start](CSS-LOGICAL-1#propdef-padding-block-start) 

[padding-bottom](CSS-BOX-4#propdef-padding-bottom) 

[padding-inline-end](CSS-LOGICAL-1#propdef-padding-inline-end) 

[padding-inline-start](CSS-LOGICAL-1#propdef-padding-inline-start) 

[padding-left](CSS-BOX-4#propdef-padding-left) 

[padding-right](CSS-BOX-4#propdef-padding-right) 

[padding-top](CSS-BOX-4#propdef-padding-top) 

[width](CSS-SIZING-3#propdef-width) 

A **resolved value special case property like [height](CSS-SIZING-3#propdef-height)** defined in another specification 

If the property applies to the element or pseudo-element and the [resolved value](CSSOM#resolved-value) of the [display](CSS-DISPLAY-4#propdef-display) property is not [none](CSS-DISPLAY-4#valdef-display-none) or [contents](CSS-DISPLAY-4#valdef-display-contents), then the resolved value is the [used value](CSS-CASCADE-5#used-value). Otherwise the resolved value is the [computed value](CSS-CASCADE-5#computed-value).

[bottom](CSS-POSITION-3#propdef-bottom) 

[left](CSS-POSITION-3#propdef-left) 

[inset-block-end](CSS-POSITION-3#propdef-inset-block-end) 

[inset-block-start](CSS-POSITION-3#propdef-inset-block-start) 

[inset-inline-end](CSS-POSITION-3#propdef-inset-inline-end) 

[inset-inline-start](CSS-POSITION-3#propdef-inset-inline-start) 

[right](CSS-POSITION-3#propdef-right) 

[top](CSS-POSITION-3#propdef-top) 

A **resolved value special case property like [top](CSS-POSITION-3#propdef-top)** defined in another specification 

If the property applies to a positioned element and the [resolved value](CSSOM#resolved-value) of the [display](CSS-DISPLAY-4#propdef-display) property is not [none](CSS-DISPLAY-4#valdef-display-none) or [contents](CSS-DISPLAY-4#valdef-display-contents), and the property is not over-constrained, then the resolved value is the [used value](CSS-CASCADE-5#used-value). Otherwise the resolved value is the [computed value](CSS-CASCADE-5#computed-value).

A **resolved value special case property** defined in another specification 

As defined in the relevant specification.

Any other property 

The [resolved value](CSSOM#resolved-value) is the [computed value](CSS-CASCADE-5#computed-value).

Tests

*   [computed-style-001.html](https://wpt.fyi/results/css/cssom/computed-style-001.html) [(live test)](http://wpt.live/css/cssom/computed-style-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/cssom/computed-style-001.html)
*   [computed-style-002.html](https://wpt.fyi/results/css/cssom/computed-style-002.html) [(live test)](http://wpt.live/css/cssom/computed-style-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/cssom/computed-style-002.html)
*   [computed-style-003.html](https://wpt.fyi/results/css/cssom/computed-style-003.html) [(live test)](http://wpt.live/css/cssom/computed-style-003.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/cssom/computed-style-003.html)
*   [computed-style-004.html](https://wpt.fyi/results/css/cssom/computed-style-004.html) [(live test)](http://wpt.live/css/cssom/computed-style-004.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/cssom/computed-style-004.html)
*   [computed-style-005.html](https://wpt.fyi/results/css/cssom/computed-style-005.html) [(live test)](http://wpt.live/css/cssom/computed-style-005.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/cssom/computed-style-005.html)
*   [resolved-border-width.html](https://wpt.fyi/results/css/cssom/resolved-border-width.html) [(live test)](http://wpt.live/css/cssom/resolved-border-width.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/cssom/resolved-border-width.html)

## Navigation

- Prev: `utility-apis` — Utility APIs
- Next: `iana-considerations` — IANA Considerations
- Children: 5
  - `resolved-value` — resolved value
  - `resolved-value-special-case-property-like-color` — resolved value special case property like color
  - `resolved-value-special-case-property-like-height` — resolved value special case property like height
  - `resolved-value-special-case-property-like-top` — resolved value special case property like top
  - `resolved-value-special-case-property` — resolved value special case property

## Outgoing refs (50)

`webspec-index refs CSSOM#resolved-values -d outgoing -l 50`

## Incoming refs (1)

- CSSOM#contents

### Possible effects

CSSOM#resolved-values

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSSOM#resolved-values" --format markdown`
