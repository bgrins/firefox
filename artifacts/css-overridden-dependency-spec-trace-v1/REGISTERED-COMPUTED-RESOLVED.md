# CSS-PROPERTIES-VALUES-API-1#calculation-of-computed-values

**Computed Value-Time Behavior** (heading)

**SHA**: hash:959d45c42d151096bbc21a074aff849f48c64f3f393dfc285c437eb326f066c7

## Content

The [computed value](CSS-CASCADE-5#computed-value) of a [registered custom property](CSS-PROPERTIES-VALUES-API-1#registered-custom-property) is determined by the syntax of its [registration](CSS-PROPERTIES-VALUES-API-1#custom-property-registration).

If the [registration’s](CSS-PROPERTIES-VALUES-API-1#custom-property-registration) syntax is the [universal syntax definition](CSS-PROPERTIES-VALUES-API-1#universal-syntax-definition), the [computed value](CSS-CASCADE-5#computed-value) is the same as for unregistered [custom properties](CSS-VARIABLES-1#custom-property) (either the specified value with variables substituted, or the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value)).

Otherwise, attempt to [parse](CSS-SYNTAX-3#css-parse-something-according-to-a-css-grammar) the property’s value according to its registered syntax. If this fails, the declaration is [invalid at computed-value time](CSS-VARIABLES-1#invalid-at-computed-value-time) and the [computed value](CSS-CASCADE-5#computed-value) is determined accordingly. If it succeeds, the [computed value](CSS-CASCADE-5#computed-value) depends on the specifics of the syntax:

For `"<length>"`, `"<length-percentage>"`, `"<angle>"`, `"<time>"`, `"<resolution>"`, `"<integer>"`, `"<number>"`, and `"<percentage>"` values:

*   If the specified value is a [dimension](CSS-VALUES-4#dimension) literal (such as 50em or .2s), the computed value is the same value, but with the unit converted to the corresponding [canonical unit](CSS-VALUES-4#canonical-unit) for the type of value.

*   If the specified value is any other numeric literal (such as 5 or 20%), the computed value is as specified. (In particular, percentages are never resolved against anything.)

*   If the specified value is a function that evaluates to one of those types (such as a [math function](CSS-VALUES-4#math-function)), the computed value is defined by that function.

For `"<color>"` values, the value is computed by resolving color values, per [CSS Color 4 §  14. Resolving \<color> Values](CSS-COLOR-4#resolving-color-values).

For `"<custom-ident>"`, ident, or `"*"` values, the computed value is as specified.

For `"<url>"` values, the computed value is one of the following:

*   if the URL is a relative URL, the computed value is the resolved absolute URL as described in \[css3-values\].

*   otherwise, the computed value is as specified.

URL behavior examples

> **Example:** Because URLs resolve against the base URL of the stylesheet they appear in, we can end up with multiple relative URLs that resolve against different base URLs, even though they appear in the same property.For example, suppose --url-foo and --url-bar are registered custom properties with \<url> syntax, and that we have a stylesheet at `/style/foo/foo.css`:
>
> ```
> div {
>   --url-foo: url("foo.png");
> }
> ```
>
> and another stylesheet at `/style/bar/bar.css`
>
> ```
> div {
>   --url-bar: url("bar.png");
> }
> ```
>
> and finally a document at `/index.html`:
>
> ```
> <link href="/style/foo/foo.css" rel="stylesheet" type="text/css">
> <link href="/style/bar/bar.css" rel="stylesheet" type="text/css">
> <div style="background-image: var(--url-foo), var(---url-bar);">
> </div>
> ```
>
> Here, the var(--url-foo) reference would produce a URL that resolves against `/style/foo`, and the var(--url-bar) reference would produce a URL that resolves against `/style/bar`.
>
> On the other hand, if both --url-foo and --url-bar were *un*registered, they would substitute their literal values (relative URLs) into the `/index.html` stylesheet, which would then resolve the URLs against `/index.html` instead.

For `"<image>"` values, the computed value is the [computed \<image>](CSS-IMAGES-4#computed-image).

For `"<transform-function>"` and `"<transform-list>"` values, the computed value is as specified but with all lengths resolved to their computed values.

For values with [multipliers](CSS-PROPERTIES-VALUES-API-1#multipliers), the computed value is a list of the computed values of the base type.

For syntaxes specified with [the | combinator](CSS-PROPERTIES-VALUES-API-1#combinator), the computed value is given by applying the computed-value rules for the first clause that matches the value.

## Navigation

- Parent: `behavior-of-custom-properties` — Registered Custom Properties
- Prev: `specified-value` — Specified Value-Time Behavior
- Next: `animation-behavior-of-custom-properties` — Animation Behavior

## Outgoing refs (15)

`webspec-index refs CSS-PROPERTIES-VALUES-API-1#calculation-of-computed-values -d outgoing -l 15`

## Incoming refs (4)

- CSS-PROPERTIES-VALUES-API-1#contents
- CSS-PROPERTIES-VALUES-API-1#parsing-custom-properties
- CSS-PROPERTIES-VALUES-API-1#substitution
- CSS-PROPERTIES-VALUES-API-1#the-registerproperty-function
