# CSS-VALUES-4#font-relative-lengths

**Font-relative Lengths: the em, rem, ex, rex, cap, rcap, ch, rch, ic, ric, lh, rlh units** (heading)

**SHA**: hash:1c4ce22ba37b4ced4cb6360ea3d4657eb0f52ba7406d99b28f0f1a2e574ed34d

## Content

The **font-relative lengths** refer to the font metrics either of the element on which they are used (for the **local font-relative lengths**) or of the root element (for the **root font-relative lengths**).

![The word 'Sphinx' annotated with various font metrics: ascender height, to the top of the h's serif; cap height, to the visually approximate top of the S; the x height, to the visually approximate top of the x; the baseline, along the bottom of S, h, i, n, and x; and the descender height, to the bottom fo the p.](images/Typography_Line_Terms.svg)

Common typographic metrics 

**em** 

Equal to the computed value of the [font-size](CSS-FONTS-4#propdef-font-size) property of the element on which it is used.

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

Equal to the computed value of the [em](CSS-VALUES-4#em) unit on the root element.

Tests

*   [calc-rem-lang.html](https://wpt.fyi/results/css/css-values/calc-rem-lang.html) [(live test)](http://wpt.live/css/css-values/calc-rem-lang.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/calc-rem-lang.html)

**ex** 

Equal to the used x-height of the [first available font](CSS3-FONTS#first-available-font) \[CSS3-FONTS\]. The x-height is so called because it is often equal to the height of the lowercase "x". However, an [ex](CSS-VALUES-4#ex) is defined even for fonts that do not contain an "x". The x-height of a font can be found in different ways. Some fonts contain reliable metrics for the x-height. If reliable font metrics are not available, [UAs](CSS-2023#user-agent) may determine the x-height from the height of a lowercase glyph. One possible heuristic is to look at how far the glyph for the lowercase "o" extends below the baseline, and subtract that value from the top of its bounding box. In the cases where it is impossible or impractical to determine the x-height, a value of 0.5em must be assumed.

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

Equal to the value of the [ex](CSS-VALUES-4#ex) unit on the root element.

**cap** 

Equal to the used cap-height of the [first available font](CSS3-FONTS#first-available-font) \[CSS3-FONTS\]. The cap-height is so called because it is approximately equal to the height of a capital Latin letter. However, a [cap](CSS-VALUES-4#cap) is defined even for fonts that do not contain Latin letters. The cap-height of a font can be found in different ways. Some fonts contain reliable metrics for the cap-height. If reliable font metrics are not available, [UAs](CSS-2023#user-agent) may determine the cap-height from the height of an uppercase glyph. One possible heuristic is to look at how far the glyph for the uppercase “O” extends below the baseline, and subtract that value from the top of its bounding box. In the cases where it is impossible or impractical to determine the cap-height, the font’s ascent must be used.

**rcap** 

Equal to the value of the [cap](CSS-VALUES-4#cap) unit on the root element.

**ch** 

Represents the typical [advance measure](CSS-VALUES-4#length-advance-measure) of European alphanumeric characters, and measured as the used advance measure of the “0” (ZERO, U+0030) glyph in the font used to render it. (The **advance measure** of a glyph is its advance width or height, whichever is in the inline axis of the element.)

> **Note:** Note: This measurement is an approximation (and in monospace fonts, an exact measure) of a single narrow glyph’s [advance measure](CSS-VALUES-4#length-advance-measure), thus allowing measurements based on an expected glyph count.

> **Note:** Note: The advance measure of a glyph depends on writing-mode and text-orientation as well as font settings, text-transform, and any other properties that affect glyph selection or orientation.

In the cases where it is impossible or impractical to determine the measure of the “0” glyph, it must be assumed to be 0.5em wide by 1em tall. Thus, the [ch](CSS-VALUES-4#ch) unit falls back to 0.5em in the general case, and to 1em when it would be typeset upright (i.e. [writing-mode](CSS-WRITING-MODES-4#propdef-writing-mode) is [vertical-rl](CSS-WRITING-MODES-4#valdef-writing-mode-vertical-rl) or [vertical-lr](CSS-WRITING-MODES-4#valdef-writing-mode-vertical-lr), and [text-orientation](CSS-WRITING-MODES-4#propdef-text-orientation) is [upright](CSS-WRITING-MODES-4#valdef-text-orientation-upright)).

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

Equal to the value of the [ch](CSS-VALUES-4#ch) unit on the root element.

**ic** 

Represents the typical [advance measure](CSS-VALUES-4#length-advance-measure) of CJK letters, and measured as the used advance measure of the “水” (CJK water ideograph, U+6C34) glyph found in the font used to render it.

> **Note:** Note: This measurement is a typically an exact measure (in the few fonts with proportional fullwidth glyphs, an approximation) of a single [fullwidth](http://unicode.org/reports/tr11/#Definitions) glyph’s [advance measure](CSS-VALUES-4#length-advance-measure), thus allowing measurements based on an expected glyph count.

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

Equal to the value of the [ic](CSS-VALUES-4#ic) unit on the root element.

**lh** 

Equal to the computed value of the [line-height](CSS2#propdef-line-height) property of the element on which it is used, converting [normal](CSS-INLINE-3#valdef-line-height-normal) to an absolute length by using only the metrics of the [first available font](CSS3-FONTS#first-available-font).

Tests

*   [lh-rlh-on-root-001.html](https://wpt.fyi/results/css/css-values/lh-rlh-on-root-001.html) [(live test)](http://wpt.live/css/css-values/lh-rlh-on-root-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/lh-rlh-on-root-001.html)
*   [lh-unit-001.html](https://wpt.fyi/results/css/css-values/lh-unit-001.html) [(live test)](http://wpt.live/css/css-values/lh-unit-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/lh-unit-001.html)
*   [lh-unit-002.html](https://wpt.fyi/results/css/css-values/lh-unit-002.html) [(live test)](http://wpt.live/css/css-values/lh-unit-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/lh-unit-002.html)

**rlh** 

Equal to the value of the [lh](CSS-VALUES-4#lh) unit on the root element.

> **Note:** Note: Setting the [height](CSS-SIZING-3#propdef-height) of an element using either the [lh](CSS-VALUES-4#lh) or the [rlh](CSS-VALUES-4#rlh) units does not enable authors to control the actual number of lines in that element. These units only enable length calculations based on the theoretical size of an ideal empty line; the size of actual lines boxes may differ based on their content. In cases where an author wants to limit the number of actual lines in an element, the [max-lines](CSS-OVERFLOW-4#propdef-max-lines) property can be used instead.

Tests

*   [lh-rlh-on-root-001.html](https://wpt.fyi/results/css/css-values/lh-rlh-on-root-001.html) [(live test)](http://wpt.live/css/css-values/lh-rlh-on-root-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-values/lh-rlh-on-root-001.html)

Properties that affect the font size or font metrics of an element are **font-affecting properties**. When used in the value of any [font-affecting property](CSS-VALUES-4#font-affecting-property) on the element they refer to, the [font-relative lengths](CSS-VALUES-4#font-relative-length) resolve against the computed metrics of the parent element—​or against the computed metrics corresponding to the initial values of the [font](CSS-FONTS-4#propdef-font) and [line-height](CSS2#propdef-line-height) properties, if the element has no parent. Similarly, when [lh](CSS-VALUES-4#lh) or [rlh](CSS-VALUES-4#rlh) units are used in the value of the line-height property or font-affecting properties on the element they refer to, they resolve against the computed line-height and font metrics of the parent element—​or the computed metrics corresponding to the initial values of the font and line-height properties, if the element has no parent. (The other font-relative lengths continue to resolve against the element’s own metrics when used in line-height.)

> **Note:** Note: Most properties defined in \[css-fonts-4\] are [font-affecting properties](CSS-VALUES-4#font-affecting-property), as is [math-style](MATHML-CORE#propdef-math-style) and [math-depth](MATHML-CORE#propdef-math-depth). (This isn’t necessarily an exhaustive list.)

When used outside the context of an element (such as in [media queries](MEDIAQUERIES-5#media-query)), the [font-relative lengths](CSS-VALUES-4#font-relative-length) units refer to the metrics corresponding to the initial values of the [font](CSS-FONTS-4#propdef-font) and [line-height](CSS2#propdef-line-height) properties. Similarly, when specified in a document with no root element, the [root font-relative lengths](CSS-VALUES-4#root-font-relative-lengths) are resolved assuming the initial values of the font and line-height properties.

> **Note:** Note: Font-relative units such as [ch](CSS-VALUES-4#ch) and [ic](CSS-VALUES-4#ic) can trigger font downloads, if a required font is not yet loaded.

The [font-relative lengths](CSS-VALUES-4#font-relative-length) are calculated in the absence of shaping.

Some user-agents allow users to apply additional restrictions to font sizes in a document, such as setting minimum font sizes to ensure readability. Such restrictions must be applied to the [used value](CSS-CASCADE-5#used-value) of the affected properties only; they *must not* affect the resolution of [font-relative lengths](CSS-VALUES-4#font-relative-length) used in properties. However, in other contexts (such as in [media queries](MEDIAQUERIES-5#media-query)), to the extent that they would impact the used font metrics, such restrictions *do* affect the resolution of font-relative lengths.

> **Note:** Note: In general, respecting a user’s preferences, like minimum font sizes, is desirable; it’s useful for a media query like (min-width: 40em) to use the actual font size the document will be displayed in. However, having these preferences affect font-relative lengths *in properties on an element* was found to not be Web-compatible; too many pages expect these units to be exact multiples of the specified [font-size](CSS-FONTS-4#propdef-font-size), rather than the *actual* font-size after applying user preferences.

Some user-agents apply restrictions to the [line-height](CSS2#propdef-line-height) values on form controls. These must have no effect on the [lh](CSS-VALUES-4#lh) and [rlh](CSS-VALUES-4#rlh) units. The effect on their descendants, however, is [implementation-defined](INFRA#implementation-defined).

## Navigation

- Parent: `relative-lengths` — Relative Lengths
- Next: `viewport-relative-lengths` — Viewport-percentage Lengths: the *vw, *vh, *vi, *vb, *vmin, *vmax units
- Children: 17
  - `font-relative-length` — font-relative lengths
  - `local-font-relative-lengths` — local font-relative lengths
  - `root-font-relative-lengths` — root font-relative lengths
  - `em` — em
  - `rem` — rem
  - `ex` — ex
  - `rex` — rex
  - `cap` — cap
  - `rcap` — rcap
  - `ch` — ch
  - `length-advance-measure` — advance measure
  - `rch` — rch
  - `ic` — ic
  - `ric` — ric
  - `lh` — lh
  - `rlh` — rlh
  - `font-affecting-property` — font-affecting properties

## Outgoing refs (34)

`webspec-index refs CSS-VALUES-4#font-relative-lengths -d outgoing -l 34`

## Incoming refs (1)

- CSS-VALUES-4#contents

### Possible effects

CSS-VALUES-4#font-relative-lengths

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VALUES-4#font-relative-lengths" --format markdown`
