# CSS-CASCADE-5#computed

**Computed Values** (heading)

**SHA**: hash:2c51fc71d5bfec21aee9acf5004344fc0b5197db31fc48a1ae5373f3fbc4670f

## Content

The **computed value** is the result of resolving the [specified value](CSS-CASCADE-5#specified-value) as defined in the “Computed Value” line of the property definition table, generally absolutizing it in preparation for [inheritance](CSS-CASCADE-5#css-inheritance).

> **Note:** Note: The [computed value](CSS-CASCADE-5#computed-value) is the value that is transferred from parent to child during [inheritance](CSS-CASCADE-5#css-inheritance). For historical reasons, it is not necessarily the value returned by the [`getComputedStyle()`](CSSOM-1#dom-window-getcomputedstyle) function, which sometimes returns [used values](CSS-CASCADE-5#used-value). \[CSSOM\] Furthermore, the computed value is an abstract data representation: their definitions reflect that data representation, not how that data is serialized. For example, serialization rules often allow omitting certain values which are implied during parsing; but those values are nonetheless part of the computed value.

> **Example:** A [specified value](CSS-CASCADE-5#specified-value) can be either absolute (i.e., not relative to another value, as in [red](CSS-COLOR-4#valdef-color-red) or 2mm) or relative (i.e., relative to another value, as in [auto](ANIMATION-TRIGGERS-1#valdef-timeline-trigger-active-range-auto), 2em). Computing a relative value generally absolutizes it:
>
> *   values with relative units ([em](CSS-VALUES-4#em), [ex](CSS-VALUES-3#ex), [vh](CSS-VALUES-4#vh), [vw](CSS-VALUES-4#vw)) must be made absolute by multiplying with the appropriate reference size
> *   certain keywords (e.g., smaller, [bolder](CSS-FONTS-4#valdef-font-weight-bolder)) must be replaced according to their definitions
> *   percentages on some properties must be multiplied by a reference value (defined by the property)
> *   valid relative URLs must be resolved to become absolute.
>
> See examples (f), (g) and (h) in the [table below](CSS-CASCADE-5#stages-examples).

> **Note:** Note: In general, the [computed value](CSS-CASCADE-5#computed-value) resolves the [specified value](CSS-CASCADE-5#specified-value) as far as possible without laying out the document or performing other expensive or hard-to-parallelize operations, such as resolving network requests or retrieving values other than from the element and its parent.

The [computed value](CSS-CASCADE-5#computed-value) exists even when the property does not apply. However, some properties may change how they determine the computed value based on whether the property [applies to](CSS-CASCADE-5#apply) the element.

## Navigation

- Parent: `value-stages` — Value Processing
- Prev: `specified` — Specified Values
- Next: `used` — Used Values
- Children: 1
  - `computed-value` — computed value

## Outgoing refs (14)

`webspec-index refs CSS-CASCADE-5#computed -d outgoing -l 14`

## Incoming refs (1)

- CSS-CASCADE-5#contents
