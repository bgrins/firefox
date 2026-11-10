# CSS-CONDITIONAL-5#style-container

**Style Container Features** (heading)

**SHA**: hash:fb5563dd1884e6564cd915db8b3d8e218c9937747e071c989cf4bcc19b8d27e6

## Content

A **container style query** allows querying the [computed values](CSS-CASCADE-5#computed-value) of the [query container](CSS-CONDITIONAL-5#query-container). It is a boolean combination of individual **style features** ([\<style-feature>](CSS-CONDITIONAL-5#typedef-style-feature)) that each query a single, specific property of the query container. The syntax of a \<style-feature> is either the same as for a valid [declaration](CSS-SYNTAX-3#declaration)\[CSS-SYNTAX-3\], a [\<style-feature-name>](CSS-CONDITIONAL-5#typedef-style-feature-name) or a valid **style range** ([\<style-range>](CSS-CONDITIONAL-5#typedef-style-range)). The **[\<style-feature-name>](CSS-CONDITIONAL-5#typedef-style-feature-name)** can be either a [supported CSS property](CSSOM-1#supported-css-property) or a valid [\<custom-property-name>](CSS-VARIABLES-2#typedef-custom-property-name). The **[\<style-feature-value>](CSS-CONDITIONAL-5#typedef-style-feature-value)** production matches any valid [\<declaration-value>](CSS-SYNTAX-3#typedef-declaration-value) as long as it doesn’t contain [\<mf-lt>](MEDIAQUERIES-5#typedef-mf-lt), [\<mf-gt>](MEDIAQUERIES-5#typedef-mf-gt) and [\<mf-eq>](MEDIAQUERIES-5#typedef-mf-eq) tokens.

Tests

*   [style-query-registered-custom-rem-change.html](https://wpt.fyi/results/css/css-conditional/container-queries/style-query-registered-custom-rem-change.html) [(live test)](http://wpt.live/css/css-conditional/container-queries/style-query-registered-custom-rem-change.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-conditional/container-queries/style-query-registered-custom-rem-change.html)
*   [style-query-unset-on-root.html](https://wpt.fyi/results/css/css-conditional/container-queries/style-query-unset-on-root.html) [(live test)](http://wpt.live/css/css-conditional/container-queries/style-query-unset-on-root.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-conditional/container-queries/style-query-unset-on-root.html)

A [\<style-feature-plain>](CSS-CONDITIONAL-5#typedef-style-feature-plain) evaluates to true if the [computed value](CSS-CASCADE-5#computed-value) of the given property on the [query container](CSS-CONDITIONAL-5#query-container) matches the given value (which is also computed with respect to the query container), and false otherwise.

A [style feature](CSS-CONDITIONAL-5#style-features) without a value ([\<style-feature-boolean>](CSS-CONDITIONAL-5#typedef-style-feature-boolean)) evaluates to true if the [computed value](CSS-CASCADE-5#computed-value) is different from the [initial value](CSS-CASCADE-5#initial-value) for the given [property](CSS-CASCADE-5#css-property).

To **evaluate a [\<style-range>](CSS-CONDITIONAL-5#typedef-style-range)**, the following steps needs to be performed:

1.  If [\<style-range-value>](CSS-CONDITIONAL-5#typedef-style-range-value) is a [\<custom-property-name>](CSS-VARIABLES-2#typedef-custom-property-name), it needs to be substituted as if the \<custom-property-name> was wrapped inside a [var()](CSS-VARIABLES-2#funcdef-var).

2.  Substitute [arbitrary substitution function](CSS-VALUES-5#arbitrary-substitution-function) within [\<style-range-value>](CSS-CONDITIONAL-5#typedef-style-range-value).

3.  Parse [\<style-range-value>](CSS-CONDITIONAL-5#typedef-style-range-value) to [\<number>](CSS-VALUES-4#number-value), [\<percentage>](CSS-VALUES-4#percentage-value), [\<length>](CSS-VALUES-4#length-value), [\<angle>](CSS-VALUES-4#angle-value), [\<time>](CSS-VALUES-4#time-value), [\<frequency>](CSS-VALUES-4#frequency-value) or [\<resolution>](CSS-VALUES-4#resolution-value). If this cannot be done, evaluate to false.

4.  If each [\<style-range-value>](CSS-CONDITIONAL-5#typedef-style-range-value) from the range have the same type, compute each and evaluate the comparison; a unitless zero must be treated as being a zero-[\<length>](CSS-VALUES-4#length-value) when compared against a \<length> .

5.  Otherwise evaluate to false.

The boolean syntax and logic combining [style features](CSS-CONDITIONAL-5#style-features) into a [style query](CSS-CONDITIONAL-5#container-style-query) is the same as for [CSS feature queries](CSS-CONDITIONAL-3#css-feature-queries). (See [@supports](CSS-CONDITIONAL-3#at-ruledef-supports). \[css-conditional-3\])

[Style features](CSS-CONDITIONAL-5#style-features) that query a [shorthand property](CSS-CASCADE-5#shorthand-property) are true if the [computed values](CSS-CASCADE-5#computed-value) match for each of its [longhand properties](CSS-CASCADE-5#longhand), and false otherwise.

[Cascade-dependent keywords](CSS-CASCADE-5#cascade-dependent-keyword), such as [revert](CSS-CASCADE-5#valdef-all-revert) and [revert-layer](CSS-CASCADE-5#valdef-all-revert-layer), are invalid as values in a [style feature](CSS-CONDITIONAL-5#style-features), and cause the [container style query](CSS-CONDITIONAL-5#container-style-query) to be false.

> **Note:** Note: The remaining non-cascade-dependent [CSS-wide keywords](CSS-VALUES-4#css-wide-keywords) are [computed](CSS-CASCADE-5#computed-value) with respect to the [query container](CSS-CONDITIONAL-5#query-container), the same as other values.

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
