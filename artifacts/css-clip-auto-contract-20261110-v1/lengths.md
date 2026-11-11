# CSS-VALUES-4#lengths

**Distance Units: the <length> type** (heading)

**SHA**: hash:525ff9eb18a45f0b497a8e73717a48325285ffcf9184e2189ab7dc81fd562ba0

## Content

Lengths refer to distance measurements and are denoted by **\<length>** in the property definitions. A length is a [dimension](https://drafts.csswg.org/css-values-4#dimension).

For zero lengths the unit identifier is optional (i.e. can be syntactically represented as the [\<number>](https://drafts.csswg.org/css-values-4#number-value) 0). However, if a 0 could be parsed as either a \<number> or a [\<length>](https://drafts.csswg.org/css-values-4#length-value) in a property (such as [line-height](https://drafts.csswg.org/css2/#propdef-line-height)), it must parse as a \<number>.

Properties may restrict the length value to some range. If the value is outside the allowed range, the declaration is invalid and must be [ignored](https://www.w3.org/TR/CSS2/conform.html#ignore).

Tests

*   [min-width-001.xht](https://wpt.fyi/results/css/mediaqueries/min-width-001.xht) [(live test)](http://wpt.live/css/mediaqueries/min-width-001.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/mediaqueries/min-width-001.xht)
*   [numbers-units-005.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-005.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-005.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-005.xht)
*   [numbers-units-006.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-006.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-006.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-006.xht)

While some properties allow negative length values, this may complicate the formatting and there may be implementation-specific limits. If a negative length value is allowed but cannot be supported, it must be converted to the nearest value that can be supported.

In cases where the [used](https://drafts.csswg.org/css-cascade-5/#used-value) length cannot be supported, user agents must approximate it in the [actual](https://drafts.csswg.org/css-cascade-5/#actual-value) value.

There are two types of length units: [relative](https://drafts.csswg.org/css-values-4#relative-length) and [absolute](https://drafts.csswg.org/css-values-4#absolute-length). The [specified value](https://drafts.csswg.org/css-cascade-5/#specified-value) of a length (**specified length**) is represented by its quantity and its unit. The [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) of a length (**computed length**) is the [specified length](https://drafts.csswg.org/css-values-4#specified-length) resolved to an absolute length, and its unit is not distinguished: it can be represented by any absolute length unit (but will be serialized using its [canonical unit](https://drafts.csswg.org/css-values-4#canonical-unit), [px](https://drafts.csswg.org/css-values-4#px)).

Tests

*   [calc-unit-analysis.html](https://wpt.fyi/results/css/css-values/calc-unit-analysis.html) [(live test)](http://wpt.live/css/css-values/calc-unit-analysis.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/calc-unit-analysis.html)
*   [shape-outside-circle-002.html](https://wpt.fyi/results/css/css-shapes/shape-outside/values/shape-outside-circle-002.html) [(live test)](http://wpt.live/css/css-shapes/shape-outside/values/shape-outside-circle-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-shapes/shape-outside/values/shape-outside-circle-002.html)
*   [shape-outside-circle-004.html](https://wpt.fyi/results/css/css-shapes/shape-outside/values/shape-outside-circle-004.html) [(live test)](http://wpt.live/css/css-shapes/shape-outside/values/shape-outside-circle-004.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-shapes/shape-outside/values/shape-outside-circle-004.html)
*   [shape-outside-ellipse-002.html](https://wpt.fyi/results/css/css-shapes/shape-outside/values/shape-outside-ellipse-002.html) [(live test)](http://wpt.live/css/css-shapes/shape-outside/values/shape-outside-ellipse-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-shapes/shape-outside/values/shape-outside-ellipse-002.html)
*   [shape-outside-ellipse-004.html](https://wpt.fyi/results/css/css-shapes/shape-outside/values/shape-outside-ellipse-004.html) [(live test)](http://wpt.live/css/css-shapes/shape-outside/values/shape-outside-ellipse-004.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-shapes/shape-outside/values/shape-outside-ellipse-004.html)
*   [shape-outside-inset-003.html](https://wpt.fyi/results/css/css-shapes/shape-outside/values/shape-outside-inset-003.html) [(live test)](http://wpt.live/css/css-shapes/shape-outside/values/shape-outside-inset-003.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-shapes/shape-outside/values/shape-outside-inset-003.html)
*   [shape-outside-polygon-004.html](https://wpt.fyi/results/css/css-shapes/shape-outside/values/shape-outside-polygon-004.html) [(live test)](http://wpt.live/css/css-shapes/shape-outside/values/shape-outside-polygon-004.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-shapes/shape-outside/values/shape-outside-polygon-004.html)

While the exact supported precision of numeric values, and how they are rounded to match that precision, is generally [implementation-defined](https://infra.spec.whatwg.org/#implementation-defined), [\<length>](https://drafts.csswg.org/css-values-4#length-value)s in [border-width](https://drafts.csswg.org/css-borders-4/#propdef-border-width) and a few other properties are rounded in a specific fashion to ensure reasonable visual display. (This algorithm is called by individual properties explicitly.)

To **snap a length as a line width** given a [\<length>](https://drafts.csswg.org/css-values-4#length-value) *len*:

1.  If *len* is an integer number of [device pixels](https://drafts.csswg.org/css-values-4#device-pixel), do nothing.

2.  If the absolute value of *len* is greater than zero, but less than 1 [device pixel](https://drafts.csswg.org/css-values-4#device-pixel), round it away from zero to 1 or -1 device pixel.

3.  If the absolute value of *len* is greater than 1 [device pixel](https://drafts.csswg.org/css-values-4#device-pixel), round it towards zero to the nearest integer number of device pixels.

### Relative Lengths

**Relative length units** specify a length relative to another length. Style sheets that use relative units can more easily scale from one output environment to another.

The relative units are:

Informative Summary of Relative Units
| unit                                               | relative to                                                                                                                                                                                         |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [em](https://drafts.csswg.org/css-values-4#em)     | font size of the element                                                                                                                                                                            |
| [ex](https://drafts.csswg.org/css-values-4#ex)     | x-height of the element’s font                                                                                                                                                                      |
| [cap](https://drafts.csswg.org/css-values-4#cap)   | cap height (the nominal height of capital letters) of the element’s font                                                                                                                            |
| [ch](https://drafts.csswg.org/css-values-4#ch)     | typical [character advance](https://drafts.csswg.org/css-values-4#length-advance-measure) of a narrow glyph in the element’s font, as represented by the “0” (ZERO, U+0030) glyph                   |
| [ic](https://drafts.csswg.org/css-values-4#ic)     | typical [character advance](https://drafts.csswg.org/css-values-4#length-advance-measure) of a fullwidth glyph in the element’s font, as represented by the “水” (CJK water ideograph, U+6C34) glyph |
| [rem](https://drafts.csswg.org/css-values-4#rem)   | font size of the root element                                                                                                                                                                       |
| [lh](https://drafts.csswg.org/css-values-4#lh)     | line height of the element                                                                                                                                                                          |
| [rlh](https://drafts.csswg.org/css-values-4#rlh)   | line height of the root element                                                                                                                                                                     |
| [vw](https://drafts.csswg.org/css-values-4#vw)     | 1% of viewport’s width                                                                                                                                                                              |
| [vh](https://drafts.csswg.org/css-values-4#vh)     | 1% of viewport’s height                                                                                                                                                                             |
| [vi](https://drafts.csswg.org/css-values-4#vi)     | 1% of viewport’s size in the root element’s [inline axis](https://drafts.csswg.org/css-writing-modes-4/#inline-axis)                                                                                |
| [vb](https://drafts.csswg.org/css-values-4#vb)     | 1% of viewport’s size in the root element’s [block axis](https://drafts.csswg.org/css-writing-modes-4/#block-axis)                                                                                  |
| [vmin](https://drafts.csswg.org/css-values-4#vmin) | 1% of viewport’s smaller dimension                                                                                                                                                                  |
| [vmax](https://drafts.csswg.org/css-values-4#vmax) | 1% of viewport’s larger dimension                                                                                                                                                                   |

Child elements do not inherit the relative values as specified for their parent; they inherit the [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value).

#### Font-relative Lengths: the [em](https://drafts.csswg.org/css-values-4#em), [rem](https://drafts.csswg.org/css-values-4#rem), [ex](https://drafts.csswg.org/css-values-4#ex), [rex](https://drafts.csswg.org/css-values-4#rex), [cap](https://drafts.csswg.org/css-values-4#cap), [rcap](https://drafts.csswg.org/css-values-4#rcap), [ch](https://drafts.csswg.org/css-values-4#ch), [rch](https://drafts.csswg.org/css-values-4#rch), [ic](https://drafts.csswg.org/css-values-4#ic), [ric](https://drafts.csswg.org/css-values-4#ric), [lh](https://drafts.csswg.org/css-values-4#lh), [rlh](https://drafts.csswg.org/css-values-4#rlh) units

The **font-relative lengths** refer to the font metrics either of the element on which they are used (for the **local font-relative lengths**) or of the root element (for the **root font-relative lengths**).

![The word 'Sphinx' annotated with various font metrics: ascender height, to the top of the h's serif; cap height, to the visually approximate top of the S; the x height, to the visually approximate top of the x; the baseline, along the bottom of S, h, i, n, and x; and the descender height, to the bottom fo the p.](images/Typography_Line_Terms.svg)

Common typographic metrics 

**em** 

Equal to the computed value of the [font-size](https://drafts.csswg.org/css-fonts-4/#propdef-font-size) property of the element on which it is used.

> **Example:** The rule:
>
> ```
> h1 { line-height: 1.2em }
> ```
>
> means that the line height of `h1` elements will be 20% greater than the font size of `h1` element. On the other hand:
>
> ```
> h1 { font-size: 1.2em }
> ```
>
> means that the font size of `h1` elements will be 20% greater than the computed font size inherited by `h1` elements.

**rem** 

Equal to the computed value of the [em](https://drafts.csswg.org/css-values-4#em) unit on the root element.

Tests

*   [calc-rem-lang.html](https://wpt.fyi/results/css/css-values/calc-rem-lang.html) [(live test)](http://wpt.live/css/css-values/calc-rem-lang.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/calc-rem-lang.html)

**ex** 

Equal to the used x-height of the [first available font](https://www.w3.org/TR/css3-fonts/#first-available-font) \[CSS3-FONTS\]. The x-height is so called because it is often equal to the height of the lowercase "x". However, an [ex](https://drafts.csswg.org/css-values-4#ex) is defined even for fonts that do not contain an "x". The x-height of a font can be found in different ways. Some fonts contain reliable metrics for the x-height. If reliable font metrics are not available, [UAs](https://drafts.csswg.org/css-2023/#user-agent) may determine the x-height from the height of a lowercase glyph. One possible heuristic is to look at how far the glyph for the lowercase "o" extends below the baseline, and subtract that value from the top of its bounding box. In the cases where it is impossible or impractical to determine the x-height, a value of 0.5em must be assumed.

Tests

*   [ex-unit-001.html](https://wpt.fyi/results/css/css-values/ex-unit-001.html) [(live test)](http://wpt.live/css/css-values/ex-unit-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ex-unit-001.html)
*   [ex-unit-002.html](https://wpt.fyi/results/css/css-values/ex-unit-002.html) [(live test)](http://wpt.live/css/css-values/ex-unit-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ex-unit-002.html)
*   [ex-unit-003.html](https://wpt.fyi/results/css/css-values/ex-unit-003.html) [(live test)](http://wpt.live/css/css-values/ex-unit-003.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ex-unit-003.html)
*   [numbers-units-007.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-007.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-007.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-007.xht)
*   [numbers-units-009.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-009.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-009.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-009.xht)
*   [numbers-units-010.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-010.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-010.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-010.xht)
*   [numbers-units-011.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-011.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-011.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-011.xht)
*   [numbers-units-012.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-012.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-012.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-012.xht)
*   [numbers-units-013.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-013.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-013.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-013.xht)
*   [numbers-units-015.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-015.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-015.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-015.xht)
*   [numbers-units-019.xht](https://wpt.fyi/results/css/CSS2/values/numbers-units-019.xht) [(live test)](http://wpt.live/css/CSS2/values/numbers-units-019.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/numbers-units-019.xht)
*   [units-001.xht](https://wpt.fyi/results/css/CSS2/values/units-001.xht) [(live test)](http://wpt.live/css/CSS2/values/units-001.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-001.xht)
*   [units-002.xht](https://wpt.fyi/results/css/CSS2/values/units-002.xht) [(live test)](http://wpt.live/css/CSS2/values/units-002.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-002.xht)
*   [units-003.xht](https://wpt.fyi/results/css/CSS2/values/units-003.xht) [(live test)](http://wpt.live/css/CSS2/values/units-003.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-003.xht)
*   [units-004.xht](https://wpt.fyi/results/css/CSS2/values/units-004.xht) [(live test)](http://wpt.live/css/CSS2/values/units-004.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-004.xht)
*   [units-005.xht](https://wpt.fyi/results/css/CSS2/values/units-005.xht) [(live test)](http://wpt.live/css/CSS2/values/units-005.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-005.xht)
*   [calc-ch-ex-lang.html](https://wpt.fyi/results/css/css-values/calc-ch-ex-lang.html) [(live test)](http://wpt.live/css/css-values/calc-ch-ex-lang.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/calc-ch-ex-lang.html)

**rex** 

Equal to the value of the [ex](https://drafts.csswg.org/css-values-4#ex) unit on the root element.

**cap** 

Equal to the used cap-height of the [first available font](https://www.w3.org/TR/css3-fonts/#first-available-font) \[CSS3-FONTS\]. The cap-height is so called because it is approximately equal to the height of a capital Latin letter. However, a [cap](https://drafts.csswg.org/css-values-4#cap) is defined even for fonts that do not contain Latin letters. The cap-height of a font can be found in different ways. Some fonts contain reliable metrics for the cap-height. If reliable font metrics are not available, [UAs](https://drafts.csswg.org/css-2023/#user-agent) may determine the cap-height from the height of an uppercase glyph. One possible heuristic is to look at how far the glyph for the uppercase “O” extends below the baseline, and subtract that value from the top of its bounding box. In the cases where it is impossible or impractical to determine the cap-height, the font’s ascent must be used.

**rcap** 

Equal to the value of the [cap](https://drafts.csswg.org/css-values-4#cap) unit on the root element.

**ch** 

Represents the typical [advance measure](https://drafts.csswg.org/css-values-4#length-advance-measure) of European alphanumeric characters, and measured as the used advance measure of the “0” (ZERO, U+0030) glyph in the font used to render it. (The **advance measure** of a glyph is its advance width or height, whichever is in the inline axis of the element.)

> **Note:** Note: This measurement is an approximation (and in monospace fonts, an exact measure) of a single narrow glyph’s [advance measure](https://drafts.csswg.org/css-values-4#length-advance-measure), thus allowing measurements based on an expected glyph count.

> **Note:** Note: The advance measure of a glyph depends on writing-mode and text-orientation as well as font settings, text-transform, and any other properties that affect glyph selection or orientation.

In the cases where it is impossible or impractical to determine the measure of the “0” glyph, it must be assumed to be 0.5em wide by 1em tall. Thus, the [ch](https://drafts.csswg.org/css-values-4#ch) unit falls back to 0.5em in the general case, and to 1em when it would be typeset upright (i.e. [writing-mode](https://drafts.csswg.org/css-writing-modes-4/#propdef-writing-mode) is [vertical-rl](https://drafts.csswg.org/css-writing-modes-4/#valdef-writing-mode-vertical-rl) or [vertical-lr](https://drafts.csswg.org/css-writing-modes-4/#valdef-writing-mode-vertical-lr), and [text-orientation](https://drafts.csswg.org/css-writing-modes-4/#propdef-text-orientation) is [upright](https://drafts.csswg.org/css-writing-modes-4/#valdef-text-orientation-upright)).

Tests

*   [ch-unit-001.html](https://wpt.fyi/results/css/css-values/ch-unit-001.html) [(live test)](http://wpt.live/css/css-values/ch-unit-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-001.html)
*   [ch-unit-002.html](https://wpt.fyi/results/css/css-values/ch-unit-002.html) [(live test)](http://wpt.live/css/css-values/ch-unit-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-002.html)
*   [ch-unit-003.html](https://wpt.fyi/results/css/css-values/ch-unit-003.html) [(live test)](http://wpt.live/css/css-values/ch-unit-003.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-003.html)
*   [ch-unit-004.html](https://wpt.fyi/results/css/css-values/ch-unit-004.html) [(live test)](http://wpt.live/css/css-values/ch-unit-004.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-004.html)
*   [ch-unit-008.html](https://wpt.fyi/results/css/css-values/ch-unit-008.html) [(live test)](http://wpt.live/css/css-values/ch-unit-008.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-008.html)
*   [ch-unit-009.html](https://wpt.fyi/results/css/css-values/ch-unit-009.html) [(live test)](http://wpt.live/css/css-values/ch-unit-009.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-009.html)
*   [ch-unit-010.html](https://wpt.fyi/results/css/css-values/ch-unit-010.html) [(live test)](http://wpt.live/css/css-values/ch-unit-010.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-010.html)
*   [ch-unit-011.html](https://wpt.fyi/results/css/css-values/ch-unit-011.html) [(live test)](http://wpt.live/css/css-values/ch-unit-011.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-011.html)
*   [ch-unit-012.html](https://wpt.fyi/results/css/css-values/ch-unit-012.html) [(live test)](http://wpt.live/css/css-values/ch-unit-012.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-012.html)
*   [ch-unit-016.html](https://wpt.fyi/results/css/css-values/ch-unit-016.html) [(live test)](http://wpt.live/css/css-values/ch-unit-016.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-016.html)
*   [ch-unit-017.html](https://wpt.fyi/results/css/css-values/ch-unit-017.html) [(live test)](http://wpt.live/css/css-values/ch-unit-017.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ch-unit-017.html)
*   [line-break-ch-unit.html](https://wpt.fyi/results/css/css-values/line-break-ch-unit.html) [(live test)](http://wpt.live/css/css-values/line-break-ch-unit.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/line-break-ch-unit.html)
*   [calc-ch-ex-lang.html](https://wpt.fyi/results/css/css-values/calc-ch-ex-lang.html) [(live test)](http://wpt.live/css/css-values/calc-ch-ex-lang.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/calc-ch-ex-lang.html)

**rch** 

Equal to the value of the [ch](https://drafts.csswg.org/css-values-4#ch) unit on the root element.

**ic** 

Represents the typical [advance measure](https://drafts.csswg.org/css-values-4#length-advance-measure) of CJK letters, and measured as the used advance measure of the “水” (CJK water ideograph, U+6C34) glyph found in the font used to render it.

> **Note:** Note: This measurement is a typically an exact measure (in the few fonts with proportional fullwidth glyphs, an approximation) of a single [fullwidth](http://unicode.org/reports/tr11/#Definitions) glyph’s [advance measure](https://drafts.csswg.org/css-values-4#length-advance-measure), thus allowing measurements based on an expected glyph count.

In the cases where it is impossible or impractical to determine the ideographic advance measure, it must be assumed to be 1em.

Tests

*   [ic-unit-001.html](https://wpt.fyi/results/css/css-values/ic-unit-001.html) [(live test)](http://wpt.live/css/css-values/ic-unit-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ic-unit-001.html)
*   [ic-unit-002.html](https://wpt.fyi/results/css/css-values/ic-unit-002.html) [(live test)](http://wpt.live/css/css-values/ic-unit-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ic-unit-002.html)
*   [ic-unit-003.html](https://wpt.fyi/results/css/css-values/ic-unit-003.html) [(live test)](http://wpt.live/css/css-values/ic-unit-003.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ic-unit-003.html)
*   [ic-unit-004.html](https://wpt.fyi/results/css/css-values/ic-unit-004.html) [(live test)](http://wpt.live/css/css-values/ic-unit-004.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ic-unit-004.html)
*   [ic-unit-008.html](https://wpt.fyi/results/css/css-values/ic-unit-008.html) [(live test)](http://wpt.live/css/css-values/ic-unit-008.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ic-unit-008.html)
*   [ic-unit-009.html](https://wpt.fyi/results/css/css-values/ic-unit-009.html) [(live test)](http://wpt.live/css/css-values/ic-unit-009.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ic-unit-009.html)
*   [ic-unit-010.html](https://wpt.fyi/results/css/css-values/ic-unit-010.html) [(live test)](http://wpt.live/css/css-values/ic-unit-010.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ic-unit-010.html)
*   [ic-unit-011.html](https://wpt.fyi/results/css/css-values/ic-unit-011.html) [(live test)](http://wpt.live/css/css-values/ic-unit-011.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ic-unit-011.html)
*   [ic-unit-012.html](https://wpt.fyi/results/css/css-values/ic-unit-012.html) [(live test)](http://wpt.live/css/css-values/ic-unit-012.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/ic-unit-012.html)

**ric** 

Equal to the value of the [ic](https://drafts.csswg.org/css-values-4#ic) unit on the root element.

**lh** 

Equal to the computed value of the [line-height](https://drafts.csswg.org/css2/#propdef-line-height) property of the element on which it is used, converting [normal](https://drafts.csswg.org/css-inline-3/#valdef-line-height-normal) to an absolute length by using only the metrics of the [first available font](https://www.w3.org/TR/css3-fonts/#first-available-font).

Tests

*   [lh-rlh-on-root-001.html](https://wpt.fyi/results/css/css-values/lh-rlh-on-root-001.html) [(live test)](http://wpt.live/css/css-values/lh-rlh-on-root-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/lh-rlh-on-root-001.html)
*   [lh-unit-001.html](https://wpt.fyi/results/css/css-values/lh-unit-001.html) [(live test)](http://wpt.live/css/css-values/lh-unit-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/lh-unit-001.html)
*   [lh-unit-002.html](https://wpt.fyi/results/css/css-values/lh-unit-002.html) [(live test)](http://wpt.live/css/css-values/lh-unit-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/lh-unit-002.html)

**rlh** 

Equal to the value of the [lh](https://drafts.csswg.org/css-values-4#lh) unit on the root element.

> **Note:** Note: Setting the [height](https://drafts.csswg.org/css-sizing-3/#propdef-height) of an element using either the [lh](https://drafts.csswg.org/css-values-4#lh) or the [rlh](https://drafts.csswg.org/css-values-4#rlh) units does not enable authors to control the actual number of lines in that element. These units only enable length calculations based on the theoretical size of an ideal empty line; the size of actual lines boxes may differ based on their content. In cases where an author wants to limit the number of actual lines in an element, the [max-lines](https://drafts.csswg.org/css-overflow-4/#propdef-max-lines) property can be used instead.

Tests

*   [lh-rlh-on-root-001.html](https://wpt.fyi/results/css/css-values/lh-rlh-on-root-001.html) [(live test)](http://wpt.live/css/css-values/lh-rlh-on-root-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/lh-rlh-on-root-001.html)

Properties that affect the font size or font metrics of an element are **font-affecting properties**. When used in the value of any [font-affecting property](https://drafts.csswg.org/css-values-4#font-affecting-property) on the element they refer to, the [font-relative lengths](https://drafts.csswg.org/css-values-4#font-relative-length) resolve against the computed metrics of the parent element—​or against the computed metrics corresponding to the initial values of the [font](https://drafts.csswg.org/css-fonts-4/#propdef-font) and [line-height](https://drafts.csswg.org/css2/#propdef-line-height) properties, if the element has no parent. Similarly, when [lh](https://drafts.csswg.org/css-values-4#lh) or [rlh](https://drafts.csswg.org/css-values-4#rlh) units are used in the value of the line-height property or font-affecting properties on the element they refer to, they resolve against the computed line-height and font metrics of the parent element—​or the computed metrics corresponding to the initial values of the font and line-height properties, if the element has no parent. (The other font-relative lengths continue to resolve against the element’s own metrics when used in line-height.)

> **Note:** Note: Most properties defined in \[css-fonts-4\] are [font-affecting properties](https://drafts.csswg.org/css-values-4#font-affecting-property), as is [math-style](https://w3c.github.io/mathml-core/#propdef-math-style) and [math-depth](https://w3c.github.io/mathml-core/#propdef-math-depth). (This isn’t necessarily an exhaustive list.)

When used outside the context of an element (such as in [media queries](https://drafts.csswg.org/mediaqueries-5/#media-query)), the [font-relative lengths](https://drafts.csswg.org/css-values-4#font-relative-length) units refer to the metrics corresponding to the initial values of the [font](https://drafts.csswg.org/css-fonts-4/#propdef-font) and [line-height](https://drafts.csswg.org/css2/#propdef-line-height) properties. Similarly, when specified in a document with no root element, the [root font-relative lengths](https://drafts.csswg.org/css-values-4#root-font-relative-lengths) are resolved assuming the initial values of the font and line-height properties.

> **Note:** Note: Font-relative units such as [ch](https://drafts.csswg.org/css-values-4#ch) and [ic](https://drafts.csswg.org/css-values-4#ic) can trigger font downloads, if a required font is not yet loaded.

The [font-relative lengths](https://drafts.csswg.org/css-values-4#font-relative-length) are calculated in the absence of shaping.

Some user-agents allow users to apply additional restrictions to font sizes in a document, such as setting minimum font sizes to ensure readability. Such restrictions must be applied to the [used value](https://drafts.csswg.org/css-cascade-5/#used-value) of the affected properties only; they *must not* affect the resolution of [font-relative lengths](https://drafts.csswg.org/css-values-4#font-relative-length) used in properties. However, in other contexts (such as in [media queries](https://drafts.csswg.org/mediaqueries-5/#media-query)), to the extent that they would impact the used font metrics, such restrictions *do* affect the resolution of font-relative lengths.

> **Note:** Note: In general, respecting a user’s preferences, like minimum font sizes, is desirable; it’s useful for a media query like (min-width: 40em) to use the actual font size the document will be displayed in. However, having these preferences affect font-relative lengths *in properties on an element* was found to not be Web-compatible; too many pages expect these units to be exact multiples of the specified [font-size](https://drafts.csswg.org/css-fonts-4/#propdef-font-size), rather than the *actual* font-size after applying user preferences.

Some user-agents apply restrictions to the [line-height](https://drafts.csswg.org/css2/#propdef-line-height) values on form controls. These must have no effect on the [lh](https://drafts.csswg.org/css-values-4#lh) and [rlh](https://drafts.csswg.org/css-values-4#rlh) units. The effect on their descendants, however, is [implementation-defined](https://infra.spec.whatwg.org/#implementation-defined).

#### Viewport-percentage Lengths: the \*vw, \*vh, \*vi, \*vb, \*vmin, \*vmax units

The **viewport-percentage lengths** are relative to the size of the [initial containing block](https://www.w3.org/TR/CSS2/visudet.html#containing-block-details)—​which is itself based on the size of either the viewport (for [continuous media](https://drafts.csswg.org/mediaqueries-5/#continuous-media)) or the [page area](https://drafts.csswg.org/css-page-3/#page-area) (for [paged media](https://drafts.csswg.org/mediaqueries-5/#paged-media)). When the height or width of the initial containing block is changed, they are scaled accordingly.

##### The Large, Small, and Dynamic Viewport Sizes

There are four variants of the [viewport-percentage length](https://drafts.csswg.org/css-values-4#viewport-percentage-lengths) units, corresponding to three (possibly identical) notions of the viewport size.

large viewport 

The **large viewport-percentage units** (lv\*) and **default viewport-percentage units** (v\*) are defined with respect to the **large viewport size**: the viewport sized assuming any [UA](https://drafts.csswg.org/css-2023/#user-agent) interfaces that are dynamically expanded and retracted to be retracted. This allows authors to size content such that it is guaranteed to fill the viewport, noting that such content might be hidden behind such interfaces when they are expanded.The sizes of the [large viewport-percentage units](https://drafts.csswg.org/css-values-4#large-viewport-percentage-units) are fixed (and therefore stable) unless the viewport itself is resized.

> **Example:** For example, on phones, where screen real-estate is at a premium, browsers will often hide part or all of the title and address bar once the user starts scrolling the page. The [large viewport-percentage units](https://drafts.csswg.org/css-values-4#large-viewport-percentage-units) are sized relative to this larger everything-retracted space, so content using these units will fill the entire visible page when these UI elements are hidden. However, when these retractable elements are shown, they can obscure content that is sized or positioned using these units.

small viewport 

The **small viewport-percentage units** (sv\*) are defined with respect to the **small viewport size**: the viewport sized assuming any [UA](https://drafts.csswg.org/css-2023/#user-agent) interfaces that are dynamically expanded and retracted to be expanded. This allows authors to size content such that it can fit within the viewport even when such interfaces are present, noting that such content might not fill the viewport when such interfaces are retracted.The sizes of the [small viewport-percentage units](https://drafts.csswg.org/css-values-4#small-viewport-percentage-units) are fixed (and therefore stable) unless the viewport itself is resized.

> **Example:** An element that is sized as [height: 100svh](https://drafts.csswg.org/css-sizing-3/#propdef-height), for example, will fill the screen perfectly, without any of its content being obscured, when all the dynamic UI elements of the UA are shown.Once those UI elements start being hidden, however, there will be extra space around the element. The [small viewport-percentage units](https://drafts.csswg.org/css-values-4#small-viewport-percentage-units) units are thus “safer” in general, but might not produce the most attractive layout once the user starts interacting with the page.

dynamic viewport 

The **dynamic viewport-percentage units** (dv\*) are defined with respect to the **dynamic viewport size**: the viewport sized with dynamic consideration of any [UA](https://drafts.csswg.org/css-2023/#user-agent) interfaces that are dynamically expanded and retracted. This allows authors to size content such that it can exactly fit within the viewport whether or not such interfaces are present.The sizes of the [dynamic viewport-percentage units](https://drafts.csswg.org/css-values-4#dynamic-viewport-percentage-units) *are not stable* even while the viewport itself is unchanged. Using these units can cause content to resize e.g. while the user scrolls the page. Depending on usage, this can be disturbing to the user and/or costly in terms of performance.

The UA is not required to animate the [dynamic viewport-percentage units](https://drafts.csswg.org/css-values-4#dynamic-viewport-percentage-units) while expanding and retracting any relevant interfaces, and may instead calculate the units as if the relevant interface was fully expanded or retracted during the UI animation. (It is recommended that UAs assume the fully-retracted size for this duration.)

Whether the expansion/retraction of a particular interface (A) changes the sizes of all of the [viewport-percentage lengths](https://drafts.csswg.org/css-values-4#viewport-percentage-lengths) (and the [initial containing block](https://drafts.csswg.org/css-display-4/#initial-containing-block)) simultaneously or (B) contributes to the differences between the [large viewport size](https://drafts.csswg.org/css-values-4#large-viewport-size) and [small viewport size](https://drafts.csswg.org/css-values-4#small-viewport-size) is largely UA-dependent. However:

*   Changes in interface that happen as a result of scrolling or other frequent page interactions that would disturb the user if they resulted in substantial layout changes must be categorized as the latter (B).

*   Changes in interface that have a sufficiently steady state that re-laying out the document into the adjusted space would be beneficial to the user must be categorized as the former (A).

*   Additionally, UAs may have some dynamically-shown interfaces that intentionally overlay content and do not cause any shifts in layout—​and therefore have no effect on any of the [viewport-percentage lengths](https://drafts.csswg.org/css-values-4#viewport-percentage-lengths). (Typically on-screen keyboards will fit into this category.)

In all cases, if the value of [overflow](https://drafts.csswg.org/css-overflow-3/#propdef-overflow) or [scrollbar-gutter](https://drafts.csswg.org/css-overflow-3/#propdef-scrollbar-gutter) on the [root element](https://drafts.csswg.org/css-display-4/#root-element) in either axis would cause scrollbars to appear (or space to be reserved for them) unconditionally (for example, overflow: scroll, but not overflow: auto), the [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value) of the [viewport-percentage lengths](https://drafts.csswg.org/css-values-4#viewport-percentage-lengths) in that axis are reduced in accordance with the [initial containing block](https://drafts.csswg.org/css-display-4/#initial-containing-block). Otherwise, and always in the case of [media queries](https://drafts.csswg.org/mediaqueries-5/#media-query), the viewport-percentage lengths are sized assuming that scrollbars do not exist (even if this diverges from the initial containing block).

> **Note:** Note: The value of [overflow](https://drafts.csswg.org/css-overflow-3/#propdef-overflow) on [the body element](https://html.spec.whatwg.org/multipage/dom.html#the-body-element-2) can sometimes affect the presence of scrollbars on the [root element](https://drafts.csswg.org/css-display-4/#root-element). This *does not* affect the size of viewport units, however.

##### The Various Viewport-relative Units

The [viewport-percentage length](https://drafts.csswg.org/css-values-4#viewport-percentage-lengths) units are:

**vw** 

**svw** 

**lvw** 

**dvw** 

Equal to 1% of the width of the [large viewport size](https://drafts.csswg.org/css-values-4#large-viewport-size), [small viewport size](https://drafts.csswg.org/css-values-4#small-viewport-size), large viewport size, and [dynamic viewport size](https://drafts.csswg.org/css-values-4#dynamic-viewport-size), respectively.

> **Example:** In the example below, if the width of the viewport is 200mm, the font size of `h1` elements will be 16mm (i.e. (8×200mm)/100).
>
> ```
> h1 { font-size: 8vw }
> ```

**vh** 

**svh** 

**lvh** 

**dvh** 

Equal to 1% of the height of the [large viewport size](https://drafts.csswg.org/css-values-4#large-viewport-size), [small viewport size](https://drafts.csswg.org/css-values-4#small-viewport-size), large viewport size, and [dynamic viewport size](https://drafts.csswg.org/css-values-4#dynamic-viewport-size), respectively.

**vi** 

**svi** 

**lvi** 

**dvi** 

Equal to 1% of the size of the [large viewport size](https://drafts.csswg.org/css-values-4#large-viewport-size), [small viewport size](https://drafts.csswg.org/css-values-4#small-viewport-size), large viewport size, and [dynamic viewport size](https://drafts.csswg.org/css-values-4#dynamic-viewport-size) (respectively) in the box’s [inline axis](https://drafts.csswg.org/css-writing-modes-4/#inline-axis).

**vb** 

**svb** 

**lvb** 

**dvb** 

Equal to 1% of the size of the initial containing block [large viewport size](https://drafts.csswg.org/css-values-4#large-viewport-size), [small viewport size](https://drafts.csswg.org/css-values-4#small-viewport-size), large viewport size, and [dynamic viewport size](https://drafts.csswg.org/css-values-4#dynamic-viewport-size) (respectively) in the box’s [block axis](https://drafts.csswg.org/css-writing-modes-4/#block-axis).

**vmin** 

**svmin** 

**lvmin** 

**dvmin** 

Equal to the smaller of \*vw or \*vh.

**vmax** 

**svmax** 

**lvmax** 

**dvmax** 

Equal to the larger of \*vw or \*vh.

Tests

*   [vh-calc-support-pct.html](https://wpt.fyi/results/css/css-values/vh-calc-support-pct.html) [(live test)](http://wpt.live/css/css-values/vh-calc-support-pct.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-calc-support-pct.html)
*   [vh-calc-support.html](https://wpt.fyi/results/css/css-values/vh-calc-support.html) [(live test)](http://wpt.live/css/css-values/vh-calc-support.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-calc-support.html)
*   [vh-em-inherit.html](https://wpt.fyi/results/css/css-values/vh-em-inherit.html) [(live test)](http://wpt.live/css/css-values/vh-em-inherit.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-em-inherit.html)
*   [vh-inherit.html](https://wpt.fyi/results/css/css-values/vh-inherit.html) [(live test)](http://wpt.live/css/css-values/vh-inherit.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-inherit.html)
*   [vh-interpolate-pct.html](https://wpt.fyi/results/css/css-values/vh-interpolate-pct.html) [(live test)](http://wpt.live/css/css-values/vh-interpolate-pct.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-interpolate-pct.html)
*   [vh-interpolate-px.html](https://wpt.fyi/results/css/css-values/vh-interpolate-px.html) [(live test)](http://wpt.live/css/css-values/vh-interpolate-px.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-interpolate-px.html)
*   [vh-interpolate-vh.html](https://wpt.fyi/results/css/css-values/vh-interpolate-vh.html) [(live test)](http://wpt.live/css/css-values/vh-interpolate-vh.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-interpolate-vh.html)
*   [vh-support.html](https://wpt.fyi/results/css/css-values/vh-support.html) [(live test)](http://wpt.live/css/css-values/vh-support.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-support.html)
*   [vh-support-margin.html](https://wpt.fyi/results/css/css-values/vh-support-margin.html) [(live test)](http://wpt.live/css/css-values/vh-support-margin.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-support-margin.html)
*   [vh-support-transform-origin.html](https://wpt.fyi/results/css/css-values/vh-support-transform-origin.html) [(live test)](http://wpt.live/css/css-values/vh-support-transform-origin.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-support-transform-origin.html)
*   [vh-support-transform-translate.html](https://wpt.fyi/results/css/css-values/vh-support-transform-translate.html) [(live test)](http://wpt.live/css/css-values/vh-support-transform-translate.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-support-transform-translate.html)
*   [vh-zero-support.html](https://wpt.fyi/results/css/css-values/vh-zero-support.html) [(live test)](http://wpt.live/css/css-values/vh-zero-support.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/vh-zero-support.html)
*   [viewport-relative-lengths-scaled-viewport.html](https://wpt.fyi/results/css/css-values/viewport-relative-lengths-scaled-viewport.html) [(live test)](http://wpt.live/css/css-values/viewport-relative-lengths-scaled-viewport.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/viewport-relative-lengths-scaled-viewport.html)
*   [viewport-unit-011.html](https://wpt.fyi/results/css/css-values/viewport-unit-011.html) [(live test)](http://wpt.live/css/css-values/viewport-unit-011.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/viewport-unit-011.html)
*   [viewport-units-css2-001.html](https://wpt.fyi/results/css/css-values/viewport-units-css2-001.html) [(live test)](http://wpt.live/css/css-values/viewport-units-css2-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/viewport-units-css2-001.html)

> **Note:** Note: The original (unprefixed) viewport units [were defined](https://www.w3.org/TR/css-values-3/#viewport-relative-lengths) relative to the [initial containing block](https://drafts.csswg.org/css-display-4/#initial-containing-block), which in [continuous media](https://drafts.csswg.org/mediaqueries-5/#continuous-media) always matched the (singular) viewport size. The dynamism of browser chrome shifting in and out during scrolling was invented later, and following Safari’s lead, most UAs mapped these units to the larger size. Defining it this way is prettier in many cases, but can also block critical content (such as toolbars, headers, and footers) in others. It’s therefore not entirely clear whether this was the best mapping, and thus earlier editions of this specifications allowed UAs to choose the mapping of these default units. However at this point the mapping to the [large viewport-percentage units](https://drafts.csswg.org/css-values-4#large-viewport-percentage-units) is presumed to be required for Web compatibility.

In situations where there is no element or it hasn’t yet been styled (such as when evaluating [media queries](https://drafts.csswg.org/mediaqueries-5/#media-query)), the \*vi and \*vb units use the initial value of the [writing-mode](https://drafts.csswg.org/css-writing-modes-4/#propdef-writing-mode) property to determine which axis they correspond to.

### Absolute Lengths: the [cm](https://drafts.csswg.org/css-values-4#cm), [mm](https://drafts.csswg.org/css-values-4#mm), [Q](https://drafts.csswg.org/css-values-4#Q), [in](https://drafts.csswg.org/css-values-4#in), [pt](https://drafts.csswg.org/css-values-4#pt), [pc](https://drafts.csswg.org/css-values-4#pc), [px](https://drafts.csswg.org/css-values-4#px) units

The **absolute length units** are fixed in relation to each other and [anchored](https://drafts.csswg.org/css-values-4#anchor-unit) to some physical measurement. They are mainly useful when the output environment is known. The absolute units consist of the **physical units** ([in](https://drafts.csswg.org/css-values-4#in), [cm](https://drafts.csswg.org/css-values-4#cm), [mm](https://drafts.csswg.org/css-values-4#mm), [pt](https://drafts.csswg.org/css-values-4#pt), [pc](https://drafts.csswg.org/css-values-4#pc), [Q](https://drafts.csswg.org/css-values-4#Q)) and the **visual angle unit (pixel unit)** ([px](https://drafts.csswg.org/css-values-4#px)):

| unit                | name                | equivalence |
| ------------------- | ------------------- | ----------- |
| centimeters         | 1cm = 96px/2.54     |             |
| millimeters         | 1mm = 1/10th of 1cm |             |
| quarter-millimeters | 1Q = 1/40th of 1cm  |             |
| inches              | 1in = 2.54cm = 96px |             |
| picas               | 1pc = 1/6th of 1in  |             |
| points              | 1pt = 1/72nd of 1in |             |
| pixels              | 1px = 1/96th of 1in |             |

> **Example:** ```
> h1 { margin: 0.5in }      /* inches  */
> h2 { line-height: 3cm }   /* centimeters */
> h3 { word-spacing: 4mm }  /* millimeters */
> h3 { letter-spacing: 1Q } /* quarter-millimeters */
> h4 { font-size: 12pt }    /* points */
> h4 { font-size: 1pc }     /* picas */
> p  { font-size: 12px }    /* px */
> ```

> **Note:** Note: Lengths in publishing contexts are sometimes written like `2p3`, indicating a length of 2 picas and 3 points. These can be written in CSS as calc(2pc + 3pt) (see [§ 10.1 Basic Arithmetic: calc()](https://drafts.csswg.org/css-values-4#calc-func)).

All of the absolute length units are [compatible](https://drafts.csswg.org/css-values-4#compatible-units), and [px](https://drafts.csswg.org/css-values-4#px) is their [canonical unit](https://drafts.csswg.org/css-values-4#canonical-unit).

For a CSS device, these dimensions are **anchored** either

1.  by relating the [physical units](https://drafts.csswg.org/css-values-4#physical-unit) to their physical measurements, or
2.  by relating the [pixel unit](https://drafts.csswg.org/css-values-4#visual-angle-unit) to the [reference pixel](https://drafts.csswg.org/css-values-4#reference-pixel).

For print media at typical viewing distances, the [anchor unit](https://drafts.csswg.org/css-values-4#anchor-unit) should be one of the [physical units](https://drafts.csswg.org/css-values-4#physical-unit) (inches, centimeters, etc). For screen media (including high-resolution devices), low-resolution devices, and devices with unusual viewing distances, it is recommended instead that the anchor unit be the [pixel unit](https://drafts.csswg.org/css-values-4#visual-angle-unit). For such devices it is recommended that the pixel unit refer to the whole number of [device pixels](https://drafts.csswg.org/css-values-4#device-pixel) that best approximates the reference pixel.

> **Note:** Note: If the [anchor unit](https://drafts.csswg.org/css-values-4#anchor-unit) is the [pixel unit](https://drafts.csswg.org/css-values-4#visual-angle-unit), the [physical units](https://drafts.csswg.org/css-values-4#physical-unit) might not match their physical measurements. Alternatively if the anchor unit is a physical unit, the pixel unit might not map to a whole number of [device pixels](https://drafts.csswg.org/css-values-4#device-pixel).

> **Note:** Note: This definition of the [pixel unit](https://drafts.csswg.org/css-values-4#visual-angle-unit) and the [physical units](https://drafts.csswg.org/css-values-4#physical-unit) differs from the earlier editions of CSS1 and CSS2. In particular, in previous versions of CSS the pixel unit and the physical units were not related by a fixed ratio: the physical units were always tied to their physical measurements while the pixel unit would vary to most closely match the reference pixel. (This unfortunate change was made because too much existing content relies on the assumption of 96dpi, and breaking that assumption broke the content.)

> **Note:** Note: Units are [ASCII case-insensitive](https://infra.spec.whatwg.org/#ascii-case-insensitive) and serialize as lowercase, for example 1Q serializes as 1q.

Tests

*   [absolute-length-units-001.html](https://wpt.fyi/results/css/css-values/absolute-length-units-001.html) [(live test)](http://wpt.live/css/css-values/absolute-length-units-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/absolute-length-units-001.html)
*   [q-unit-case-insensitivity-001.html](https://wpt.fyi/results/css/css-values/q-unit-case-insensitivity-001.html) [(live test)](http://wpt.live/css/css-values/q-unit-case-insensitivity-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/q-unit-case-insensitivity-001.html)
*   [q-unit-case-insensitivity-002.html](https://wpt.fyi/results/css/css-values/q-unit-case-insensitivity-002.html) [(live test)](http://wpt.live/css/css-values/q-unit-case-insensitivity-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/q-unit-case-insensitivity-002.html)
*   [units-001.xht](https://wpt.fyi/results/css/CSS2/values/units-001.xht) [(live test)](http://wpt.live/css/CSS2/values/units-001.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-001.xht)
*   [units-006.xht](https://wpt.fyi/results/css/CSS2/values/units-006.xht) [(live test)](http://wpt.live/css/CSS2/values/units-006.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-006.xht)
*   [units-008.xht](https://wpt.fyi/results/css/CSS2/values/units-008.xht) [(live test)](http://wpt.live/css/CSS2/values/units-008.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-008.xht)
*   [units-009.xht](https://wpt.fyi/results/css/CSS2/values/units-009.xht) [(live test)](http://wpt.live/css/CSS2/values/units-009.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-009.xht)

The **reference pixel** is the visual angle of one pixel on a device with a [device pixel](https://drafts.csswg.org/css-values-4#device-pixel) density of 96dpi and a distance from the reader of an arm’s length. For a nominal arm’s length of 28 inches, the visual angle is therefore about 0.0213 degrees. For reading at arm’s length, 1px thus corresponds to about 0.26 mm (1/96 inch).

The image below illustrates the effect of viewing distance on the size of a reference pixel: a reading distance of 71 cm (28 inches) results in a reference pixel of 0.26 mm, while a reading distance of 3.5 m (12 feet) results in a reference pixel of 1.3 mm.

![This diagram illustrates how the definition of a pixel
depends on the users distance from the viewing surface
(paper or screen).
The image depicts the user looking at two planes,
one 28 inches (71 cm) from the user,
the second 140 inches (3.5 m) from the user.
An expanding cone is projected from the user's eye onto each plane.
Where the cone strikes the first plane,
the projected pixel is 0.26 mm high.
Where the cone strikes the second plane,
the projected pixel is 1.4 mm high.](images/pixel1.png)

Showing that pixels must become larger if the viewing distance increases 

This second image illustrates the effect of a device’s resolution on the pixel unit: an area of 1px by 1px is covered by a single dot in a low-resolution device (e.g. a typical computer display), while the same area is covered by 16 dots in a higher resolution device (such as a printer).

![This diagram illustrates the relationship between
the reference pixel and device pixels (called “dots” below).
The image depicts
a high resolution (large dot density) laser printer output on the left
and a low resolution monitor screen on the right.
For the laser printer, one square reference pixel is implemented by 16 dots.
For the monitor screen, one square reference pixel is implemented by a single dot.](images/pixel2.png)

Showing that more device pixels (dots) are needed to cover a 1px by 1px area on a high-resolution device than on a lower-resolution one (of the same approximate viewing distance) 

Tests

*   [absolute-length-units-001.html](https://wpt.fyi/results/css/css-values/absolute-length-units-001.html) [(live test)](http://wpt.live/css/css-values/absolute-length-units-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/absolute-length-units-001.html)

A **device pixel** is the smallest unit of area on the device output capable of displaying its full range of colors. For typical color screens, it’s a square or somewhat rectangular region containing a red, green, and blue subpixel. Many non-traditional outputs exist that can blur this definition, such as by displaying some colors at higher resolutions. Such devices still expose some equivalent notion of "device pixel", however.

## Navigation

- Prev: `numeric-types` — Numeric Data Types
- Next: `other-units` — Other Quantities
- Children: 6
  - `length-value` — <length>
  - `specified-length` — specified length
  - `computed-length` — computed length
  - `snap-as-a-line-width` — snap a length as a line width
  - `relative-lengths` — Relative Lengths
  - `absolute-lengths` — Absolute Lengths: the cm, mm, Q, in, pt, pc, px units

## Outgoing refs (16)

`webspec-index refs CSS-VALUES-4#lengths -d outgoing -l 16`

## Incoming refs (3)

- CSS-VALUES-4#contents
- CSS-WRITING-MODES-3#principal-flow
- CSS-WRITING-MODES-4#principal-flow

### Possible effects

CSS-VALUES-4#lengths

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VALUES-4#lengths" --format markdown`
