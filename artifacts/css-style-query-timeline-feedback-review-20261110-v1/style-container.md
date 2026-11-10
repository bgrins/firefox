# CSS-CONDITIONAL-5#style-container

**Style Container Features** (heading)

**SHA**: hash:fb5563dd1884e6564cd915db8b3d8e218c9937747e071c989cf4bcc19b8d27e6

## Content

A **container style query** allows querying the [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value) of the [query container](https://drafts.csswg.org/css-conditional-5#query-container). It is a boolean combination of individual **style features** ([\<style-feature>](https://drafts.csswg.org/css-conditional-5#typedef-style-feature)) that each query a single, specific property of the query container. The syntax of a \<style-feature> is either the same as for a valid [declaration](https://drafts.csswg.org/css-syntax-3/#declaration)\[CSS-SYNTAX-3\], a [\<style-feature-name>](https://drafts.csswg.org/css-conditional-5#typedef-style-feature-name) or a valid **style range** ([\<style-range>](https://drafts.csswg.org/css-conditional-5#typedef-style-range)). The **[\<style-feature-name>](https://drafts.csswg.org/css-conditional-5#typedef-style-feature-name)** can be either a [supported CSS property](https://drafts.csswg.org/cssom-1/#supported-css-property) or a valid [\<custom-property-name>](https://drafts.csswg.org/css-variables-2/#typedef-custom-property-name). The **[\<style-feature-value>](https://drafts.csswg.org/css-conditional-5#typedef-style-feature-value)** production matches any valid [\<declaration-value>](https://drafts.csswg.org/css-syntax-3/#typedef-declaration-value) as long as it doesn’t contain [\<mf-lt>](https://drafts.csswg.org/mediaqueries-5/#typedef-mf-lt), [\<mf-gt>](https://drafts.csswg.org/mediaqueries-5/#typedef-mf-gt) and [\<mf-eq>](https://drafts.csswg.org/mediaqueries-5/#typedef-mf-eq) tokens.

Tests

*   [style-query-registered-custom-rem-change.html](https://wpt.fyi/results/css/css-conditional/container-queries/style-query-registered-custom-rem-change.html) [(live test)](http://wpt.live/css/css-conditional/container-queries/style-query-registered-custom-rem-change.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-conditional/container-queries/style-query-registered-custom-rem-change.html)
*   [style-query-unset-on-root.html](https://wpt.fyi/results/css/css-conditional/container-queries/style-query-unset-on-root.html) [(live test)](http://wpt.live/css/css-conditional/container-queries/style-query-unset-on-root.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-conditional/container-queries/style-query-unset-on-root.html)

A [\<style-feature-plain>](https://drafts.csswg.org/css-conditional-5#typedef-style-feature-plain) evaluates to true if the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) of the given property on the [query container](https://drafts.csswg.org/css-conditional-5#query-container) matches the given value (which is also computed with respect to the query container), and false otherwise.

A [style feature](https://drafts.csswg.org/css-conditional-5#style-features) without a value ([\<style-feature-boolean>](https://drafts.csswg.org/css-conditional-5#typedef-style-feature-boolean)) evaluates to true if the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) is different from the [initial value](https://drafts.csswg.org/css-cascade-5/#initial-value) for the given [property](https://drafts.csswg.org/css-cascade-5/#css-property).

To **evaluate a [\<style-range>](https://drafts.csswg.org/css-conditional-5#typedef-style-range)**, the following steps needs to be performed:

1.  If [\<style-range-value>](https://drafts.csswg.org/css-conditional-5#typedef-style-range-value) is a [\<custom-property-name>](https://drafts.csswg.org/css-variables-2/#typedef-custom-property-name), it needs to be substituted as if the \<custom-property-name> was wrapped inside a [var()](https://drafts.csswg.org/css-variables-2/#funcdef-var).

2.  Substitute [arbitrary substitution function](https://drafts.csswg.org/css-values-5/#arbitrary-substitution-function) within [\<style-range-value>](https://drafts.csswg.org/css-conditional-5#typedef-style-range-value).

3.  Parse [\<style-range-value>](https://drafts.csswg.org/css-conditional-5#typedef-style-range-value) to [\<number>](https://drafts.csswg.org/css-values-4/#number-value), [\<percentage>](https://drafts.csswg.org/css-values-4/#percentage-value), [\<length>](https://drafts.csswg.org/css-values-4/#length-value), [\<angle>](https://drafts.csswg.org/css-values-4/#angle-value), [\<time>](https://drafts.csswg.org/css-values-4/#time-value), [\<frequency>](https://drafts.csswg.org/css-values-4/#frequency-value) or [\<resolution>](https://drafts.csswg.org/css-values-4/#resolution-value). If this cannot be done, evaluate to false.

4.  If each [\<style-range-value>](https://drafts.csswg.org/css-conditional-5#typedef-style-range-value) from the range have the same type, compute each and evaluate the comparison; a unitless zero must be treated as being a zero-[\<length>](https://drafts.csswg.org/css-values-4/#length-value) when compared against a \<length> .

5.  Otherwise evaluate to false.

The boolean syntax and logic combining [style features](https://drafts.csswg.org/css-conditional-5#style-features) into a [style query](https://drafts.csswg.org/css-conditional-5#container-style-query) is the same as for [CSS feature queries](https://drafts.csswg.org/css-conditional-3/#css-feature-queries). (See [@supports](https://drafts.csswg.org/css-conditional-3/#at-ruledef-supports). \[css-conditional-3\])

[Style features](https://drafts.csswg.org/css-conditional-5#style-features) that query a [shorthand property](https://drafts.csswg.org/css-cascade-5/#shorthand-property) are true if the [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value) match for each of its [longhand properties](https://drafts.csswg.org/css-cascade-5/#longhand), and false otherwise.

[Cascade-dependent keywords](https://drafts.csswg.org/css-cascade-5/#cascade-dependent-keyword), such as [revert](https://drafts.csswg.org/css-cascade-5/#valdef-all-revert) and [revert-layer](https://drafts.csswg.org/css-cascade-5/#valdef-all-revert-layer), are invalid as values in a [style feature](https://drafts.csswg.org/css-conditional-5#style-features), and cause the [container style query](https://drafts.csswg.org/css-conditional-5#container-style-query) to be false.

> **Note:** Note: The remaining non-cascade-dependent [CSS-wide keywords](https://drafts.csswg.org/css-values-4/#css-wide-keywords) are [computed](https://drafts.csswg.org/css-cascade-5/#computed-value) with respect to the [query container](https://drafts.csswg.org/css-conditional-5#query-container), the same as other values.

## Navigation

- Parent: `container-features` — Container Features
- Prev: `size-container` — Size Container Features
- Next: `scroll-state-container` — Scroll State Container Features
- Children: 6
  - `container-style-query` — container style query
  - `style-features` — style features
  - `style-range` — style range
  - `typedef-style-feature-name` — <style-feature-name>
  - `typedef-style-feature-value` — <style-feature-value>
  - `evaluate-a-style-range` — evaluate a <style-range>

## Outgoing refs (27)

`webspec-index refs CSS-CONDITIONAL-5#style-container -d outgoing -l 27`

## Incoming refs (1)

- CSS-CONDITIONAL-5#contents

### Possible effects

CSS-CONDITIONAL-5#style-container

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-CONDITIONAL-5#style-container" --format markdown`
