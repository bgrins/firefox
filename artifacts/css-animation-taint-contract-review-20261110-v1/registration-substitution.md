# CSS-PROPERTIES-VALUES-API-1#substitution

**Substitution via var()** (heading)

**SHA**: hash:959d45c42d151096bbc21a074aff849f48c64f3f393dfc285c437eb326f066c7

## Content

Like unregistered custom properties, the value of a registered custom property can be substituted into another value with the [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var) function. However, registered custom properties substitute as their [computed value](https://www.w3.org/TR/css-properties-values-api-1#calculation-of-computed-values), rather than the original token sequence used to produce that value.

Any [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var) function that references a registered custom property must be replaced with an **equivalent token sequence**, which is equal to the token sequence that would have been produced by [serializing](https://www.w3.org/TR/cssom-1/#serialize-a-css-value) the computed value, and [tokenizing](https://www.w3.org/TR/css-syntax-3/#tokenization) the resulting string.

> **Example:** Suppose that --x is registered with \<length> syntax, and that '--y’is an unregistered custom property.
>
> ```
> div {
>   font-size: 10px;
>   --x: 8em;
>   --y: var(--x);
> }
> ```
>
> Because the computed value of --x (when serialized) is "80px", the computed value of --y is a [\<dimension-token>](https://www.w3.org/TR/css-syntax-3/#typedef-dimension-token) with a value of "80" and unit "px".

#### Fallbacks In [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var) References

References to registered custom properties using the [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var) function may provide a fallback. However, the fallback value must match the [syntax definition](https://www.w3.org/TR/css-properties-values-api-1#syntax-definition) of the custom property being referenced, otherwise the declaration is [invalid at computed-value time](https://www.w3.org/TR/css-variables-1/#invalid-at-computed-value-time).

> **Note:** Note: This applies regardless of whether or not the fallback is being used.

#### Dependency Cycles via Relative Units

[Registered custom properties](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) follow the same rules for dependency cycle resolution as unregistered [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property), with the following additional constraints:

For any registered custom property with a [\<length>](https://www.w3.org/TR/css-values-4/#length-value) or [\<length-percentage>](https://www.w3.org/TR/css-values-4/#typedef-length-percentage) syntax component:

*   If the property contains any of the following units: [em](https://www.w3.org/TR/css-values-4/#em), [ex](https://www.w3.org/TR/css-values-4/#ex), [cap](https://www.w3.org/TR/css-values-4/#cap), [ch](https://www.w3.org/TR/css-values-4/#ch), [ic](https://www.w3.org/TR/css-values-4/#ic), [lh](https://www.w3.org/TR/css-values-4/#lh); then add an edge between the property and the font-size of the current element.

*   If the property contains the [lh](https://www.w3.org/TR/css-values-4/#lh) unit, add an edge between the property and the line-height of the current element.

*   If the property contains any of the following units: [rem](https://www.w3.org/TR/css-values-4/#rem), [rlh](https://www.w3.org/TR/css-values-4/#rlh); then add an edge between the property and the [font-size](https://www.w3.org/TR/css-fonts-4/#propdef-font-size)' of the root element.

*   If the property contains the [rlh](https://www.w3.org/TR/css-values-4/#rlh) unit, add an edge between the property and the [line-height](https://drafts.csswg.org/css2/#propdef-line-height)' of the root element.

> **Example:** For example, given this registration:
>
> ```
> CSS.registerProperty({
>   name: "--my-font-size",
>   syntax: "<length>",
>   initialValue: "0px",
>   inherits: false
> });
> ```
>
> the following will produce a dependency cycle:
>
> ```
> div {
>   --my-font-size: 10em;
>   font-size: var(--my-font-size);
> }
> ```
>
> and font-size will behave as if the value [unset](https://www.w3.org/TR/css-cascade-5/#valdef-all-unset) was specified.

## Navigation

- Parent: `behavior-of-custom-properties` — Registered Custom Properties
- Prev: `conditional-rules` — Conditional Rules
- Next: `shadow-dom` — Shadow DOM
- Children: 3
  - `equivalent-token-sequence` — equivalent token sequence
  - `fallbacks-in-var-references` — Fallbacks In var() References
  - `dependency-cycles` — Dependency Cycles via Relative Units

## Outgoing refs (5)

`webspec-index refs CSS-PROPERTIES-VALUES-API-1#substitution -d outgoing -l 5`

## Incoming refs (1)

- CSS-PROPERTIES-VALUES-API-1#contents

### Possible effects

CSS-PROPERTIES-VALUES-API-1#substitution

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-PROPERTIES-VALUES-API-1#substitution" --format markdown`
