# CSS-COLOR-4#transparency

**Transparency: the opacity property** (heading)

**SHA**: hash:a33157517dbdcf631045765186c288594710c1381b7b44a3fc3c7a2d9dce3c0a

## Content

Opacity can be thought of as a postprocessing operation. Conceptually, after the element (including its descendants) is rendered into an RGBA offscreen image, the opacity setting specifies how to blend the offscreen rendering into the current composite rendering. See [simple alpha compositing](https://drafts.csswg.org/css-color-4#alpha) for details.

| Name:                                                                                  |
| -------------------------------------------------------------------------------------- |
| [\<opacity-value>](https://drafts.csswg.org/css-color-4#typedef-opacity-opacity-value) |
| 1                                                                                      |
| [all elements](https://www.w3.org/TR/css-pseudo/#generated-content)                    |
| no                                                                                     |
| map to the range \[0,1\]                                                               |
| specified number, clamped to the range \[0,1\]                                         |
| per grammar                                                                            |
| by computed value type                                                                 |

Tests

*   [clip-opacity-out-of-flow.html](https://wpt.fyi/results/css/css-color/clip-opacity-out-of-flow.html) [(live test)](http://wpt.live/css/css-color/clip-opacity-out-of-flow.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/clip-opacity-out-of-flow.html)
*   [t32-opacity-basic-0.0-a.xht](https://wpt.fyi/results/css/css-color/t32-opacity-basic-0.0-a.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-basic-0.0-a.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-basic-0.0-a.xht)
*   [t32-opacity-basic-0.6-a.xht](https://wpt.fyi/results/css/css-color/t32-opacity-basic-0.6-a.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-basic-0.6-a.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-basic-0.6-a.xht)
*   [t32-opacity-basic-1.0-a.xht](https://wpt.fyi/results/css/css-color/t32-opacity-basic-1.0-a.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-basic-1.0-a.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-basic-1.0-a.xht)
*   [t32-opacity-clamping-0.0-b.xht](https://wpt.fyi/results/css/css-color/t32-opacity-clamping-0.0-b.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-clamping-0.0-b.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-clamping-0.0-b.xht)
*   [t32-opacity-clamping-1.0-b.xht](https://wpt.fyi/results/css/css-color/t32-opacity-clamping-1.0-b.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-clamping-1.0-b.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-clamping-1.0-b.xht)
*   [t32-opacity-offscreen-b.xht](https://wpt.fyi/results/css/css-color/t32-opacity-offscreen-b.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-offscreen-b.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-offscreen-b.xht)
*   [t32-opacity-offscreen-multiple-boxes-1-c.xht](https://wpt.fyi/results/css/css-color/t32-opacity-offscreen-multiple-boxes-1-c.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-offscreen-multiple-boxes-1-c.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-offscreen-multiple-boxes-1-c.xht)
*   [t32-opacity-offscreen-multiple-boxes-2-c.xht](https://wpt.fyi/results/css/css-color/t32-opacity-offscreen-multiple-boxes-2-c.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-offscreen-multiple-boxes-2-c.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-offscreen-multiple-boxes-2-c.xht)
*   [t32-opacity-offscreen-with-alpha-c.xht](https://wpt.fyi/results/css/css-color/t32-opacity-offscreen-with-alpha-c.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-offscreen-with-alpha-c.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-offscreen-with-alpha-c.xht)
*   [t32-opacity-zorder-c.xht](https://wpt.fyi/results/css/css-color/t32-opacity-zorder-c.xht) [(live test)](http://wpt.live/css/css-color/t32-opacity-zorder-c.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/t32-opacity-zorder-c.xht)
*   [opacity-computed.html](https://wpt.fyi/results/css/css-color/parsing/opacity-computed.html) [(live test)](http://wpt.live/css/css-color/parsing/opacity-computed.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/parsing/opacity-computed.html)
*   [opacity-valid.html](https://wpt.fyi/results/css/css-color/parsing/opacity-valid.html) [(live test)](http://wpt.live/css/css-color/parsing/opacity-valid.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/parsing/opacity-valid.html)
*   [opacity-invalid.html](https://wpt.fyi/results/css/css-color/parsing/opacity-invalid.html) [(live test)](http://wpt.live/css/css-color/parsing/opacity-invalid.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/parsing/opacity-invalid.html)
*   [composited-filters-under-opacity.html](https://wpt.fyi/results/css/css-color/composited-filters-under-opacity.html) [(live test)](http://wpt.live/css/css-color/composited-filters-under-opacity.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/composited-filters-under-opacity.html)
*   [filters-under-will-change-opacity.html](https://wpt.fyi/results/css/css-color/filters-under-will-change-opacity.html) [(live test)](http://wpt.live/css/css-color/filters-under-will-change-opacity.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/filters-under-will-change-opacity.html)
*   [color-composition.html](https://wpt.fyi/results/css/css-color/animation/color-composition.html) [(live test)](http://wpt.live/css/css-color/animation/color-composition.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/animation/color-composition.html)
*   [opacity-interpolation.html](https://wpt.fyi/results/css/css-color/animation/opacity-interpolation.html) [(live test)](http://wpt.live/css/css-color/animation/opacity-interpolation.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/animation/opacity-interpolation.html)
*   [canvas-change-opacity.html](https://wpt.fyi/results/css/css-color/canvas-change-opacity.html) [(live test)](http://wpt.live/css/css-color/canvas-change-opacity.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/canvas-change-opacity.html)
*   [opacity-animation-ending-correctly-001.html](https://wpt.fyi/results/css/css-color/animation/opacity-animation-ending-correctly-001.html) [(live test)](http://wpt.live/css/css-color/animation/opacity-animation-ending-correctly-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/animation/opacity-animation-ending-correctly-001.html)
*   [opacity-animation-ending-correctly-002.html](https://wpt.fyi/results/css/css-color/animation/opacity-animation-ending-correctly-002.html) [(live test)](http://wpt.live/css/css-color/animation/opacity-animation-ending-correctly-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/animation/opacity-animation-ending-correctly-002.html)

**[\<opacity-value>](https://drafts.csswg.org/css-color-4#typedef-opacity-opacity-value)** 

The opacity to be applied to the element. The resulting opacity is applied to the entire element, rather than a particular color.Opacity values outside the range \[0,1\] are not invalid, and are preserved in specified values, but are clamped to the range \[0, 1\] in computed values.

Tests

*   [inline-opacity-float-child.html](https://wpt.fyi/results/css/css-color/inline-opacity-float-child.html) [(live test)](http://wpt.live/css/css-color/inline-opacity-float-child.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/inline-opacity-float-child.html)

Opacity in CSS is represented using the [\<opacity-value>](https://drafts.csswg.org/css-color-4#typedef-opacity-opacity-value) syntax, for example in the [opacity](https://drafts.csswg.org/css-color-4#propdef-opacity) property.

```
<opacity-value> = <number> | <percentage>
```

Represented as a [\<number>](https://drafts.csswg.org/css-values-4/#number-value), the useful range of the value is 0 (representing full transparency) to 1 (representing full opacity). It can also be written as a [\<percentage>](https://drafts.csswg.org/css-values-4/#percentage-value), which [computes to](https://drafts.csswg.org/css-cascade-5/#computed-value) the equivalent \<number> (0% to 0, 100% to 1).

The [opacity](https://drafts.csswg.org/css-color-4#propdef-opacity) property applies the specified opacity to the element *as a whole*, including its contents, rather than applying it to each descendant individually. This means that, for example, an opaque child occluding part of the element’s background will continue to do so even when opacity is less than 1, but the element and child as a whole will show the underlying page through themselves.

It also means that the glyphs corresponding to all characters in the element are treated *as a whole*; any overlapping portions do not increase the opacity.

Tests

*   [opacity-overlapping-letters.html](https://wpt.fyi/results/css/css-color/opacity-overlapping-letters.html) [(live test)](http://wpt.live/css/css-color/opacity-overlapping-letters.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/opacity-overlapping-letters.html)

![overlapping glyphs rendered correctly, and incorrectly](images/joining-and-transparency.svg)

Correct and incorrect rendering of text with an [opacity](https://drafts.csswg.org/css-color-4#propdef-opacity) value of less than one, whose glyphs overlap. 

If separate opacity for each glyph is desired, it can be achieved by using a color value which includes alpha, rather than setting the [opacity](https://drafts.csswg.org/css-color-4#propdef-opacity) property.

If a box has [opacity](https://drafts.csswg.org/css-color-4#propdef-opacity) less than 1, it forms a [stacking context](https://drafts.csswg.org/css2/#stacking-context) for its children. (This prevents its contents from interleaving in the z-axis with content outside it.)

Tests

*   [body-opacity-0-to-1-stacking-context.html](https://wpt.fyi/results/css/css-color/body-opacity-0-to-1-stacking-context.html) [(live test)](http://wpt.live/css/css-color/body-opacity-0-to-1-stacking-context.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-color/body-opacity-0-to-1-stacking-context.html)

Furthermore, if the [z-index](https://drafts.csswg.org/css2/#propdef-z-index) property applies to the box, the [auto](https://drafts.csswg.org/css2/#valdef-z-index-auto) value is treated as 0 for the element; it is otherwise painted on the same layer within its parent stacking context as positioned elements with stack level 0 (as if it were a positioned element with z-index:0).

See [section 9.9](https://www.w3.org/TR/CSS21/visuren.html#layers) and [Appendix E](https://www.w3.org/TR/CSS21/zindex.html) of \[CSS2\] for more information on stacking contexts.

These rules about z-order do not apply to SVG elements, since SVG has its own [rendering model](https://www.w3.org/TR/SVG11/render.html) (\[SVG11\], Chapter 3).

The value of the [opacity](https://drafts.csswg.org/css-color-4#propdef-opacity) property does *not* affect hit testing.

## Navigation

- Parent: `applying-color` — Applying Color in CSS
- Prev: `the-color-property` — Foreground Color: the color property
- Next: `tagged-images` — Color Space of Tagged Images
- Children: 2
  - `propdef-opacity` — opacity
  - `typedef-opacity-opacity-value` — <opacity-value>

## Outgoing refs (20)

`webspec-index refs CSS-COLOR-4#transparency -d outgoing -l 20`

## Incoming refs (1)

- CSS-COLOR-4#contents

### Possible effects

CSS-COLOR-4#transparency

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-COLOR-4#transparency" --format markdown`
