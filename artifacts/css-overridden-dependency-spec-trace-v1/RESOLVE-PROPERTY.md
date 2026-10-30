# CSS-VALUES-5#resolve-property

**Resolving in Properties** (heading)

**SHA**: hash:6b2a51b0538dade54a602cc25535750a94d9cd637a495ddd6e0e82124deef42a

## Content

Unless otherwise specified, [arbitrary substitution functions](CSS-VALUES-5#arbitrary-substitution-function) can be used in place of any part of any property’s value (including within other [functional notations](CSS-VALUES-4#functional-notation)); and are not valid in any other context.

> **Issue:** Should any of these functions be valid in contexts outside of properties?

Tests

*   [variable-external-font-face-01.html](https://wpt.fyi/results/css/css-variables/variable-external-font-face-01.html) [(live test)](http://wpt.live/css/css-variables/variable-external-font-face-01.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-external-font-face-01.html)
*   [variable-font-face-01.html](https://wpt.fyi/results/css/css-variables/variable-font-face-01.html) [(live test)](http://wpt.live/css/css-variables/variable-font-face-01.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-font-face-01.html)
*   [variable-font-face-02.html](https://wpt.fyi/results/css/css-variables/variable-font-face-02.html) [(live test)](http://wpt.live/css/css-variables/variable-font-face-02.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-font-face-02.html)

> **Example:** For example, the following code incorrectly attempts to use a variable as a property name:
>
> ```
> .foo {
>   --side: margin-top;
>   var(--side): 20px;
> }
> ```
>
> This is *not* equivalent to setting [margin-top: 20px;](CSS-BOX-4#propdef-margin-top). Instead, the second declaration is simply thrown away as a syntax error for having an invalid property name.

If a property value contains one or more [arbitrary substitution functions](CSS-VALUES-5#arbitrary-substitution-function), and all of those functions are themselves syntactically valid according to their [argument grammar](CSS-VALUES-5#argument-grammar)s, the entire value’s grammar must be assumed to be valid at parse time.

Tests

*   [variable-reference-18.html](https://wpt.fyi/results/css/css-variables/variable-reference-18.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-18.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-18.html)
*   [variable-reference-19.html](https://wpt.fyi/results/css/css-variables/variable-reference-19.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-19.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-19.html)
*   [variable-reference-30.html](https://wpt.fyi/results/css/css-variables/variable-reference-30.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-30.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-30.html)

[Arbitrary substitution functions](CSS-VALUES-5#arbitrary-substitution-function) are [substituted](CSS-VALUES-5#substitute-arbitrary-substitution-function) during style [computation](CSS-CASCADE-5#computed-value), before any other value transformations or introspection can occur. If a property, after [property replacement](CSS-VALUES-5#property-replacement), does not match its declared grammar, the declaration is [invalid at computed-value time](CSS-VALUES-5#invalid-at-computed-value-time).

> **Note:** Note: Since [arbitrary substitution functions](CSS-VALUES-5#arbitrary-substitution-function) resolve at [computed value](CSS-CASCADE-5#computed-value) time, if the resulting value after substitution is invalid, the property falls back (essentially) to [unset](CSS-CASCADE-5#valdef-all-unset) behavior, rather than falling back to an earlier value in the [cascade](CSS-CASCADE-6#cascade) the way declarations invalid at parse time do. See [Invalid Substitution](CSS-VALUES-5#invalid-substitution).

Tests

*   [variable-declaration-16.html](https://wpt.fyi/results/css/css-variables/variable-declaration-16.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-16.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-16.html)
*   [variable-declaration-17.html](https://wpt.fyi/results/css/css-variables/variable-declaration-17.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-17.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-17.html)
*   [variable-declaration-18.html](https://wpt.fyi/results/css/css-variables/variable-declaration-18.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-18.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-18.html)
*   [variable-declaration-19.html](https://wpt.fyi/results/css/css-variables/variable-declaration-19.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-19.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-19.html)
*   [variable-declaration-21.html](https://wpt.fyi/results/css/css-variables/variable-declaration-21.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-21.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-21.html)
*   [variable-transitions-transition-property-all-before-value.html](https://wpt.fyi/results/css/css-variables/variable-transitions-transition-property-all-before-value.html) [(live test)](http://wpt.live/css/css-variables/variable-transitions-transition-property-all-before-value.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-transitions-transition-property-all-before-value.html)
*   [variable-transitions-value-before-transition-property-all.html](https://wpt.fyi/results/css/css-variables/variable-transitions-value-before-transition-property-all.html) [(live test)](http://wpt.live/css/css-variables/variable-transitions-value-before-transition-property-all.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-transitions-value-before-transition-property-all.html)

If a property value, after [property replacement](CSS-VALUES-5#property-replacement), contains only a single [CSS-wide keyword](CSS-VALUES-4#css-wide-keywords) (and possibly whitespace/comments), its value is determined as if that keyword were its [specified value](CSS-CASCADE-5#specified-value) all along.

Tests

*   [whitespace-in-fallback-crash.html](https://wpt.fyi/results/css/css-variables/whitespace-in-fallback-crash.html) [(live test)](http://wpt.live/css/css-variables/whitespace-in-fallback-crash.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/whitespace-in-fallback-crash.html)
*   [wide-keyword-fallback-001.html](https://wpt.fyi/results/css/css-variables/wide-keyword-fallback-001.html) [(live test)](http://wpt.live/css/css-variables/wide-keyword-fallback-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/wide-keyword-fallback-001.html)
*   [wide-keyword-fallback-002.html](https://wpt.fyi/results/css/css-variables/wide-keyword-fallback-002.html) [(live test)](http://wpt.live/css/css-variables/wide-keyword-fallback-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/wide-keyword-fallback-002.html)

> **Example:** For example, the following usage is fine from a syntax standpoint, but results in nonsense when the variable is substituted in:
>
> ```
> :root { --looks-valid: 20px; }
> p { background-color: var(--looks-valid); }
> ```
>
> Since 20px is an invalid value for [background-color](CSS-BACKGROUNDS-3#propdef-background-color), the property becomes [invalid at computed-value time](CSS-VALUES-5#invalid-at-computed-value-time), and instead resolves to [transparent](CSS-COLOR-4#valdef-color-transparent) (the [initial value](CSS-CASCADE-5#initial-value) for background-color).
>
> If the property was one that’s inherited by default, such as [color](CSS-COLOR-4#propdef-color), it would compute to the inherited value rather than the initial value.

> **Example:** While a [var()](CSS-VARIABLES-2#funcdef-var) function can’t get a [CSS-wide keyword](CSS-VALUES-4#css-wide-keywords) from the [custom property](CSS-VARIABLES-2#custom-property) itself—​if you tried to specify that, like --foo: initial;, it would just trigger [explicit defaulting](CSS-CASCADE-4#defaulting-keywords) for the custom property—​it can have a CSS-wide keyword in its fallback:
>
> ```
> p { color: var(--does-not-exist, initial); }
> ```
>
> In the above code, if the --does-not-exist property didn’t exist or is [invalid at computed-value time](CSS-VALUES-5#invalid-at-computed-value-time), the [var()](CSS-VARIABLES-2#funcdef-var) will instead substitute in the [initial](CSS-CASCADE-5#valdef-all-initial) keyword, making the property behave as if it was originally [color: initial](CSS-COLOR-4#propdef-color). This will make it take on the document’s initial color value, rather than defaulting to inheritance, as it would if there were no fallback.

To **replace substitution functions in a property** *prop*:

1.  [Substitute arbitrary substitution functions](CSS-VALUES-5#substitute-arbitrary-substitution-function) in *prop*’s value, given «"property", *prop*’s name» as the [substitution context](CSS-VALUES-5#substitution-context). Let *result* be the returned [component value](CSS-SYNTAX-3#component-value) sequence.

2.  If *result* contains the [guaranteed-invalid value](CSS-VARIABLES-2#guaranteed-invalid-value), *prop* is [invalid at computed-value time](CSS-VALUES-5#invalid-at-computed-value-time); return.

3.  [Parse](CSS-SYNTAX-3#css-parse-something-according-to-a-css-grammar) *result* according to *prop*’s grammar. If this returns failure, *prop* is [invalid at computed-value time](CSS-VALUES-5#invalid-at-computed-value-time); return.

4.  Otherwise, replace *prop*’s value with the parsed result.

Tests

*   [css-variable-change-style-001.html](https://wpt.fyi/results/css/css-variables/css-variable-change-style-001.html) [(live test)](http://wpt.live/css/css-variables/css-variable-change-style-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/css-variable-change-style-001.html)
*   [css-variable-change-style-002.html](https://wpt.fyi/results/css/css-variables/css-variable-change-style-002.html) [(live test)](http://wpt.live/css/css-variables/css-variable-change-style-002.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/css-variable-change-style-002.html)
*   [variable-declaration-01.html](https://wpt.fyi/results/css/css-variables/variable-declaration-01.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-01.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-01.html)
*   [variable-declaration-02.html](https://wpt.fyi/results/css/css-variables/variable-declaration-02.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-02.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-02.html)
*   [variable-declaration-03.html](https://wpt.fyi/results/css/css-variables/variable-declaration-03.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-03.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-03.html)
*   [variable-declaration-04.html](https://wpt.fyi/results/css/css-variables/variable-declaration-04.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-04.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-04.html)
*   [variable-declaration-05.html](https://wpt.fyi/results/css/css-variables/variable-declaration-05.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-05.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-05.html)
*   [variable-generated-content-dynamic-001.html](https://wpt.fyi/results/css/css-variables/variable-generated-content-dynamic-001.html) [(live test)](http://wpt.live/css/css-variables/variable-generated-content-dynamic-001.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-generated-content-dynamic-001.html)
*   [variable-presentation-attribute.html](https://wpt.fyi/results/css/css-variables/variable-presentation-attribute.html) [(live test)](http://wpt.live/css/css-variables/variable-presentation-attribute.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-presentation-attribute.html)
*   [variable-reference-01.html](https://wpt.fyi/results/css/css-variables/variable-reference-01.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-01.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-01.html)
*   [variable-reference-02.html](https://wpt.fyi/results/css/css-variables/variable-reference-02.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-02.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-02.html)
*   [variable-reference-03.html](https://wpt.fyi/results/css/css-variables/variable-reference-03.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-03.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-03.html)
*   [variable-reference-04.html](https://wpt.fyi/results/css/css-variables/variable-reference-04.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-04.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-04.html)
*   [variable-reference-05.html](https://wpt.fyi/results/css/css-variables/variable-reference-05.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-05.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-05.html)
*   [variable-reference-12.html](https://wpt.fyi/results/css/css-variables/variable-reference-12.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-12.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-12.html)
*   [variable-reference-16.html](https://wpt.fyi/results/css/css-variables/variable-reference-16.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-16.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-16.html)
*   [variable-reference-40.html](https://wpt.fyi/results/css/css-variables/variable-reference-40.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-40.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-40.html)
*   [variable-reference-refresh.html](https://wpt.fyi/results/css/css-variables/variable-reference-refresh.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-refresh.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-refresh.html)
*   [variable-substitution-background-properties.html](https://wpt.fyi/results/css/css-variables/variable-substitution-background-properties.html) [(live test)](http://wpt.live/css/css-variables/variable-substitution-background-properties.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-substitution-background-properties.html)
*   [variable-substitution-basic.html](https://wpt.fyi/results/css/css-variables/variable-substitution-basic.html) [(live test)](http://wpt.live/css/css-variables/variable-substitution-basic.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-substitution-basic.html)
*   [variable-substitution-filters.html](https://wpt.fyi/results/css/css-variables/variable-substitution-filters.html) [(live test)](http://wpt.live/css/css-variables/variable-substitution-filters.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-substitution-filters.html)
*   [variable-substitution-replaced-size.html](https://wpt.fyi/results/css/css-variables/variable-substitution-replaced-size.html) [(live test)](http://wpt.live/css/css-variables/variable-substitution-replaced-size.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-substitution-replaced-size.html)
*   [variable-substitution-shadow-properties.html](https://wpt.fyi/results/css/css-variables/variable-substitution-shadow-properties.html) [(live test)](http://wpt.live/css/css-variables/variable-substitution-shadow-properties.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-substitution-shadow-properties.html)
*   [variable-substitution-variable-declaration.html](https://wpt.fyi/results/css/css-variables/variable-substitution-variable-declaration.html) [(live test)](http://wpt.live/css/css-variables/variable-substitution-variable-declaration.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-substitution-variable-declaration.html)

CSSOM

*   [variable-reference-cssom.html](https://wpt.fyi/results/css/css-variables/variable-reference-cssom.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-cssom.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-cssom.html)

* * *

> **Note:** Note that [substitution](CSS-VALUES-5#substitute-arbitrary-substitution-function) takes place at the level of CSS tokens \[css-syntax-3\], not at a textual level; you can’t build up a single token where part of it is provided by a variable:
>
> ```
> .foo {
>   --gap: 20;
>   margin-top: var(--gap)px;
> }
> ```
>
> This is *not* equivalent to setting [margin-top: 20px;](CSS-BOX-4#propdef-margin-top) (a length). Instead, it’s equivalent to margin-top: 20 px; (a number followed by an ident), which is simply an invalid value for the margin-top property. Note, though, that [calc()](CSS-VALUES-4#funcdef-calc) can be used to validly achieve the same thing, like so:
>
> ```
> .foo {
>   --gap: 20;
>   margin-top: calc(var(--gap) * 1px);
> }
> ```
>
> This also implies that the post-substitution value might not be directly serializable as-is. Here’s a similar example to the preceding:
>
> ```
> .foo {
>   --gap: 20;
>   --not-px-length: var(--gap)px;
> }
> ```
>
> The serialization of the computed (post-substitution) value of --not-px-length is **not** 20px, because that would parse back as the single combined dimension; instead, it will serialize with a comment between the two tokens, like px, to enforce that they are separate tokens even when re-parsing.

Tests

*   [variable-declaration-14.html](https://wpt.fyi/results/css/css-variables/variable-declaration-14.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-14.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-14.html)
*   [variable-declaration-53.html](https://wpt.fyi/results/css/css-variables/variable-declaration-53.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-53.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-53.html)
*   [variable-declaration-54.html](https://wpt.fyi/results/css/css-variables/variable-declaration-54.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-54.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-54.html)
*   [variable-declaration-55.html](https://wpt.fyi/results/css/css-variables/variable-declaration-55.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-55.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-55.html)
*   [variable-reference-15.html](https://wpt.fyi/results/css/css-variables/variable-reference-15.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-15.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-15.html)
*   [variable-reference-without-whitespace.html](https://wpt.fyi/results/css/css-variables/variable-reference-without-whitespace.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-without-whitespace.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-without-whitespace.html)

## Navigation

- Parent: `arbitrary-substitution` — Appendix A: Arbitrary Substitution Functions
- Prev: `early-resolution` — Argument Grammars and Spread Syntax
- Next: `invalid-substitution` — Invalid Substitution
- Children: 1
  - `property-replacement` — replace substitution functions in a property

## Outgoing refs (22)

`webspec-index refs CSS-VALUES-5#resolve-property -d outgoing -l 22`

## Incoming refs (1)

- CSS-VALUES-5#contents
