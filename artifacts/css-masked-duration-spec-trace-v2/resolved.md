# CSSOM#resolved-values

**Resolved Values** (heading)

**SHA**: hash:379612f2d90d3b69e613483c2e2d28f64aad1f8d2cc904d7369bd722e7ed7d4a

## Content

[`getComputedStyle()`](https://drafts.csswg.org/cssom#dom-window-getcomputedstyle) was historically defined to return the "computed value" of an element or pseudo-element. However, the concept of "computed value" changed between revisions of CSS while the implementation of [`getComputedStyle()`](https://drafts.csswg.org/cssom#dom-window-getcomputedstyle) had to remain the same for compatibility with deployed scripts. To address this issue this specification introduces the concept of a **resolved value**.

The [resolved value](https://drafts.csswg.org/cssom#resolved-value) for a given longhand property can be determined as follows:

[background-color](https://drafts.csswg.org/css-backgrounds-3/#propdef-background-color) 

[border-block-end-color](https://drafts.csswg.org/css-borders-4/#propdef-border-block-end-color) 

[border-block-start-color](https://drafts.csswg.org/css-borders-4/#propdef-border-block-start-color) 

[border-bottom-color](https://drafts.csswg.org/css-borders-4/#propdef-border-bottom-color) 

[border-inline-end-color](https://drafts.csswg.org/css-borders-4/#propdef-border-inline-end-color) 

[border-inline-start-color](https://drafts.csswg.org/css-borders-4/#propdef-border-inline-start-color) 

[border-left-color](https://drafts.csswg.org/css-borders-4/#propdef-border-left-color) 

[border-right-color](https://drafts.csswg.org/css-borders-4/#propdef-border-right-color) 

[border-top-color](https://drafts.csswg.org/css-borders-4/#propdef-border-top-color) 

[box-shadow](https://drafts.csswg.org/css-borders-4/#propdef-box-shadow) 

[caret-color](https://drafts.csswg.org/css-ui-4/#propdef-caret-color) 

[color](https://drafts.csswg.org/css-color-4/#propdef-color) 

[outline-color](https://drafts.csswg.org/css-ui-4/#propdef-outline-color) 

A **resolved value special case property like [color](https://drafts.csswg.org/css-color-4/#propdef-color)** defined in another specification 

The [resolved value](https://drafts.csswg.org/cssom#resolved-value) is the [used value](https://drafts.csswg.org/css-cascade-5/#used-value).

[line-height](https://drafts.csswg.org/css2/#propdef-line-height) 

The [resolved value](https://drafts.csswg.org/cssom#resolved-value) is [normal](https://drafts.csswg.org/css-inline-3/#valdef-line-height-normal) if the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) is normal, or the [used value](https://drafts.csswg.org/css-cascade-5/#used-value) otherwise.

[block-size](https://drafts.csswg.org/css-logical-1/#propdef-block-size) 

[height](https://drafts.csswg.org/css-sizing-3/#propdef-height) 

[inline-size](https://drafts.csswg.org/css-logical-1/#propdef-inline-size) 

[margin-block-end](https://drafts.csswg.org/css-logical-1/#propdef-margin-block-end) 

[margin-block-start](https://drafts.csswg.org/css-logical-1/#propdef-margin-block-start) 

[margin-bottom](https://drafts.csswg.org/css-box-4/#propdef-margin-bottom) 

[margin-inline-end](https://drafts.csswg.org/css-logical-1/#propdef-margin-inline-end) 

[margin-inline-start](https://drafts.csswg.org/css-logical-1/#propdef-margin-inline-start) 

[margin-left](https://drafts.csswg.org/css-box-4/#propdef-margin-left) 

[margin-right](https://drafts.csswg.org/css-box-4/#propdef-margin-right) 

[margin-top](https://drafts.csswg.org/css-box-4/#propdef-margin-top) 

[padding-block-end](https://drafts.csswg.org/css-logical-1/#propdef-padding-block-end) 

[padding-block-start](https://drafts.csswg.org/css-logical-1/#propdef-padding-block-start) 

[padding-bottom](https://drafts.csswg.org/css-box-4/#propdef-padding-bottom) 

[padding-inline-end](https://drafts.csswg.org/css-logical-1/#propdef-padding-inline-end) 

[padding-inline-start](https://drafts.csswg.org/css-logical-1/#propdef-padding-inline-start) 

[padding-left](https://drafts.csswg.org/css-box-4/#propdef-padding-left) 

[padding-right](https://drafts.csswg.org/css-box-4/#propdef-padding-right) 

[padding-top](https://drafts.csswg.org/css-box-4/#propdef-padding-top) 

[width](https://drafts.csswg.org/css-sizing-3/#propdef-width) 

A **resolved value special case property like [height](https://drafts.csswg.org/css-sizing-3/#propdef-height)** defined in another specification 

If the property applies to the element or pseudo-element and the [resolved value](https://drafts.csswg.org/cssom#resolved-value) of the [display](https://drafts.csswg.org/css-display-4/#propdef-display) property is not [none](https://drafts.csswg.org/css-display-4/#valdef-display-none) or [contents](https://drafts.csswg.org/css-display-4/#valdef-display-contents), then the resolved value is the [used value](https://drafts.csswg.org/css-cascade-5/#used-value). Otherwise the resolved value is the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value).

[bottom](https://drafts.csswg.org/css-position-3/#propdef-bottom) 

[left](https://drafts.csswg.org/css-position-3/#propdef-left) 

[inset-block-end](https://drafts.csswg.org/css-position-3/#propdef-inset-block-end) 

[inset-block-start](https://drafts.csswg.org/css-position-3/#propdef-inset-block-start) 

[inset-inline-end](https://drafts.csswg.org/css-position-3/#propdef-inset-inline-end) 

[inset-inline-start](https://drafts.csswg.org/css-position-3/#propdef-inset-inline-start) 

[right](https://drafts.csswg.org/css-position-3/#propdef-right) 

[top](https://drafts.csswg.org/css-position-3/#propdef-top) 

A **resolved value special case property like [top](https://drafts.csswg.org/css-position-3/#propdef-top)** defined in another specification 

If the property applies to a positioned element and the [resolved value](https://drafts.csswg.org/cssom#resolved-value) of the [display](https://drafts.csswg.org/css-display-4/#propdef-display) property is not [none](https://drafts.csswg.org/css-display-4/#valdef-display-none) or [contents](https://drafts.csswg.org/css-display-4/#valdef-display-contents), and the property is not over-constrained, then the resolved value is the [used value](https://drafts.csswg.org/css-cascade-5/#used-value). Otherwise the resolved value is the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value).

A **resolved value special case property** defined in another specification 

As defined in the relevant specification.

Any other property 

The [resolved value](https://drafts.csswg.org/cssom#resolved-value) is the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value).

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
