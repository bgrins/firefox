# CSS-MASKING-1#clip-property

**Appendix A: The deprecated clip property** (heading)

**SHA**: hash:248c9352d447ac9167bbe51fbd710ed62c2b106b9da188719f48616085e2906d

## Content

| Name:                                                                                                                                                                                                                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [\<rect()>](https://drafts.csswg.org/css-masking-1#funcdef-clip-rect) [&#124;](https://drafts.csswg.org/css-values-4/#comb-one) [auto](https://drafts.csswg.org/css2/#valdef-clip-auto)                                                                                                                                                      |
| auto                                                                                                                                                                                                                                                                                                                                         |
| Absolutely positioned elements. In SVG, it applies to [elements which establish a new viewport](https://www.w3.org/TR/SVG/coords.html#EstablishingANewSVGViewport), [pattern](https://w3c.github.io/svgwg/svg2-draft/pservers.html#elementdef-pattern) elements and [mask](https://drafts.csswg.org/css-masking-1#elementdef-mask) elements. |
| no                                                                                                                                                                                                                                                                                                                                           |
| n/a                                                                                                                                                                                                                                                                                                                                          |
| as specified                                                                                                                                                                                                                                                                                                                                 |
| per grammar                                                                                                                                                                                                                                                                                                                                  |
| by [computed value](https://drafts.csswg.org/web-animations-1/#animation-type)                                                                                                                                                                                                                                                               |
| visual                                                                                                                                                                                                                                                                                                                                       |

Tests

*   [clip-interpolation.html](https://wpt.fyi/results/css/css-masking/animations/clip-interpolation.html) [(live test)](http://wpt.live/css/css-masking/animations/clip-interpolation.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/animations/clip-interpolation.html)
*   [clip-fixed-pos-transform-descendant-001.html](https://wpt.fyi/results/css/css-masking/clip/clip-fixed-pos-transform-descendant-001.html) [(live test)](http://wpt.live/css/css-masking/clip/clip-fixed-pos-transform-descendant-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/clip/clip-fixed-pos-transform-descendant-001.html)
*   [clip-no-stacking-context.html](https://wpt.fyi/results/css/css-masking/clip/clip-no-stacking-context.html) [(live test)](http://wpt.live/css/css-masking/clip/clip-no-stacking-context.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/clip/clip-no-stacking-context.html)
*   [clip-rect-comma-001.html](https://wpt.fyi/results/css/css-masking/clip/clip-rect-comma-001.html) [(live test)](http://wpt.live/css/css-masking/clip/clip-rect-comma-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/clip/clip-rect-comma-001.html)
*   [clip-rect-comma-002.html](https://wpt.fyi/results/css/css-masking/clip/clip-rect-comma-002.html) [(live test)](http://wpt.live/css/css-masking/clip/clip-rect-comma-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/clip/clip-rect-comma-002.html)
*   [clip-rect-comma-003.html](https://wpt.fyi/results/css/css-masking/clip/clip-rect-comma-003.html) [(live test)](http://wpt.live/css/css-masking/clip/clip-rect-comma-003.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/clip/clip-rect-comma-003.html)
*   [clip-rect-comma-004.html](https://wpt.fyi/results/css/css-masking/clip/clip-rect-comma-004.html) [(live test)](http://wpt.live/css/css-masking/clip/clip-rect-comma-004.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/clip/clip-rect-comma-004.html)
*   [clip-rect-scroll.html](https://wpt.fyi/results/css/css-masking/clip/clip-rect-scroll.html) [(live test)](http://wpt.live/css/css-masking/clip/clip-rect-scroll.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/clip/clip-rect-scroll.html)
*   [clip-computed.html](https://wpt.fyi/results/css/css-masking/parsing/clip-computed.html) [(live test)](http://wpt.live/css/css-masking/parsing/clip-computed.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/parsing/clip-computed.html)
*   [clip-invalid.html](https://wpt.fyi/results/css/css-masking/parsing/clip-invalid.html) [(live test)](http://wpt.live/css/css-masking/parsing/clip-invalid.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/parsing/clip-invalid.html)
*   [clip-valid.html](https://wpt.fyi/results/css/css-masking/parsing/clip-valid.html) [(live test)](http://wpt.live/css/css-masking/parsing/clip-valid.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-masking/parsing/clip-valid.html)

With this specification the [clip](https://drafts.csswg.org/css-masking-1#propdef-clip) property is deprecated. Authors are encouraged to use the [clip-path](https://drafts.csswg.org/css-masking-1#propdef-clip-path) property instead. UAs must support the clip property.

The [clip](https://drafts.csswg.org/css-masking-1#propdef-clip) property applies only to absolutely positioned elements. In SVG, it applies to [elements which establish a new viewport](https://www.w3.org/TR/SVG/coords.html#EstablishingANewSVGViewport), [pattern](https://w3c.github.io/svgwg/svg2-draft/pservers.html#elementdef-pattern) elements and [mask](https://drafts.csswg.org/css-masking-1#elementdef-mask) elements. Values have the following meanings:

auto 

The element does not clip.

**rect()** = rect( [\<top>](https://drafts.csswg.org/css-masking-1#typedef-clip-top), [\<right>](https://drafts.csswg.org/css-masking-1#typedef-clip-right), [\<bottom>](https://drafts.csswg.org/css-masking-1#typedef-clip-bottom), [\<left>](https://drafts.csswg.org/css-masking-1#typedef-clip-left) ) 

[\<top>](https://drafts.csswg.org/css-masking-1#typedef-clip-top) and [\<bottom>](https://drafts.csswg.org/css-masking-1#typedef-clip-bottom) specify offsets from the top border edge of the box, and [\<right>](https://drafts.csswg.org/css-masking-1#typedef-clip-right), and [\<left>](https://drafts.csswg.org/css-masking-1#typedef-clip-left) specify offsets from the left border edge of the box. Authors should separate offset values with commas. User agents must support separation with commas, but may also support separation without commas (but not a combination), because a previous revision of this specification was ambiguous in this respect.

**\<top>**, **\<right>**, **\<bottom>**, and **\<left>** may either have a [\<length>](https://drafts.csswg.org/css-values-4/#length-value) value or [auto](https://drafts.csswg.org/css2/#valdef-clip-auto). Negative lengths are permitted. The value auto means that a given edge of the clipping region will be the same as the edge of the element’s generated border box (i.e., auto means the same as 0 for [\<top>](https://drafts.csswg.org/css-masking-1#typedef-clip-top) and [\<left>](https://drafts.csswg.org/css-masking-1#typedef-clip-left), the same as the [used value](https://drafts.csswg.org/css-cascade-5/#used-value) of the height plus the sum of vertical padding and border widths for [\<bottom>](https://drafts.csswg.org/css-masking-1#typedef-clip-bottom), and the same as the used value of the width plus the sum of the horizontal padding and border widths for [\<right>](https://drafts.csswg.org/css-masking-1#typedef-clip-right), such that four auto values result in the clipping region being the same as the element’s border box).

When coordinates are rounded to pixel coordinates, care should be taken that no pixels remain visible when [\<left>](https://drafts.csswg.org/css-masking-1#typedef-clip-left) and [\<right>](https://drafts.csswg.org/css-masking-1#typedef-clip-right) have the same value (or [\<top>](https://drafts.csswg.org/css-masking-1#typedef-clip-top) and [\<bottom>](https://drafts.csswg.org/css-masking-1#typedef-clip-bottom) have the same value), and conversely that no pixels within the element’s border box remain hidden when these values are [auto](https://drafts.csswg.org/css2/#valdef-clip-auto).

The [clip](https://drafts.csswg.org/css-masking-1#propdef-clip) property is a [presentation attribute](https://www.w3.org/TR/2011/REC-SVG11-20110816/intro.html#TermPresentationAttribute) for SVG elements.

> **Example:** Example: The following two rules:
>
> ```
> p#one { clip: rect(5px, 40px, 45px, 5px); }
> p#two { clip: rect(5px, 55px, 45px, 5px); }
> ```
>
> and assuming both Ps are 50 by 55 pixel, will create, respectively, the rectangular clipping regions delimited by the dashed lines in the following illustrations:
>
> ![Values for rect shape](images/clip.svg)This diagram illustrates two block boxes, one next to the other, with rectangular clipping regions of different dimensions. (See [long description](https://www.w3.org/TR/CSS2/images/longdesc/clip-desc.html).)

## Navigation

- Prev: `sec` — Security Considerations
- Next: `compute-stroke-bounding-box` — Appendix B: Compute stroke bounding box
- Children: 6
  - `propdef-clip` — clip
  - `funcdef-clip-rect` — rect()
  - `typedef-clip-top` — <top>
  - `typedef-clip-right` — <right>
  - `typedef-clip-bottom` — <bottom>
  - `typedef-clip-left` — <left>

## Outgoing refs (24)

`webspec-index refs CSS-MASKING-1#clip-property -d outgoing -l 24`

## Incoming refs (1)

- CSS-MASKING-1#contents

### Possible effects

CSS-MASKING-1#clip-property

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-MASKING-1#clip-property" --format markdown`
