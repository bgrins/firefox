# CSS-VALUES-4#keywords

**Pre-defined Keywords** (heading)

**SHA**: hash:525ff9eb18a45f0b497a8e73717a48325285ffcf9184e2189ab7dc81fd562ba0

## Content

In the value definition fields, **keywords** with a pre-defined meaning appear literally. Keywords are [identifiers](https://drafts.csswg.org/css-values-4#css-css-identifier) and are interpreted [ASCII case-insensitively](https://infra.spec.whatwg.org/#ascii-case-insensitive) (i.e., \[a-z\] and \[A-Z\] are equivalent).

> **Example:** For example, here is the value definition for the [border-collapse](https://drafts.csswg.org/css2/#propdef-border-collapse) property:
>
> ```
> Value: collapse | separate
> ```
>
> And here is an example of its use:
>
> ```
> table { border-collapse: separate }
> ```

#### CSS-wide keywords: [initial](https://drafts.csswg.org/css-cascade-5/#valdef-all-initial), [inherit](https://drafts.csswg.org/css-cascade-5/#valdef-all-inherit) and [unset](https://drafts.csswg.org/css-cascade-5/#valdef-all-unset)

As defined [above](https://drafts.csswg.org/css-values-4#component-types), all properties accept the **CSS-wide keywords**, which represent value computations common to all CSS properties. These keywords are normatively defined in the [CSS Cascading and Inheritance Module](https://www.w3.org/TR/css-cascade/#defaulting-keywords).

Tests

*   [multicol-inherit-002.xht](https://wpt.fyi/results/css/css-multicol/multicol-inherit-002.xht) [(live test)](http://wpt.live/css/css-multicol/multicol-inherit-002.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-multicol/multicol-inherit-002.xht)
*   [multicol-rule-color-inherit-001.xht](https://wpt.fyi/results/css/css-multicol/multicol-rule-color-inherit-001.xht) [(live test)](http://wpt.live/css/css-multicol/multicol-rule-color-inherit-001.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-multicol/multicol-rule-color-inherit-001.xht)
*   [multicol-rule-color-inherit-002.xht](https://wpt.fyi/results/css/css-multicol/multicol-rule-color-inherit-002.xht) [(live test)](http://wpt.live/css/css-multicol/multicol-rule-color-inherit-002.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-multicol/multicol-rule-color-inherit-002.xht)
*   [units-008.xht](https://wpt.fyi/results/css/CSS2/values/units-008.xht) [(live test)](http://wpt.live/css/CSS2/values/units-008.xht) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/CSS2/values/units-008.xht)

Other CSS specifications can define additional CSS-wide keywords.

## Navigation

- Parent: `textual-values` — Textual Data Types
- Next: `custom-idents` — Unprefixed Author-defined Identifiers: the <custom-ident> type
- Children: 2
  - `css-keyword` — keywords
  - `common-keywords` — CSS-wide keywords: initial, inherit and unset

## Outgoing refs (3)

- CSS-VALUES-4#css-css-identifier
- INFRA#ascii-case-insensitive
- CSS2#propdef-border-collapse

## Incoming refs (3)

- CSS-VALUES-4#component-types
- CSS-VALUES-4#contents
- CSS-VALUES-4#textual-values

### Possible effects

CSS-VALUES-4#keywords

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VALUES-4#keywords" --format markdown`
