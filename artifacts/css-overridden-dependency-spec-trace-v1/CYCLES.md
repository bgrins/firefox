# CSS-PROPERTIES-VALUES-API-1#dependency-cycles

**Dependency Cycles via Relative Units** (heading)

**SHA**: hash:959d45c42d151096bbc21a074aff849f48c64f3f393dfc285c437eb326f066c7

## Content

[Registered custom properties](CSS-PROPERTIES-VALUES-API-1#registered-custom-property) follow the same rules for dependency cycle resolution as unregistered [custom properties](CSS-VARIABLES-1#custom-property), with the following additional constraints:

For any registered custom property with a [\<length>](CSS-VALUES-4#length-value) or [\<length-percentage>](CSS-VALUES-4#typedef-length-percentage) syntax component:

*   If the property contains any of the following units: [em](CSS-VALUES-4#em), [ex](CSS-VALUES-4#ex), [cap](CSS-VALUES-4#cap), [ch](CSS-VALUES-4#ch), [ic](CSS-VALUES-4#ic), [lh](CSS-VALUES-4#lh); then add an edge between the property and the font-size of the current element.

*   If the property contains the [lh](CSS-VALUES-4#lh) unit, add an edge between the property and the line-height of the current element.

*   If the property contains any of the following units: [rem](CSS-VALUES-4#rem), [rlh](CSS-VALUES-4#rlh); then add an edge between the property and the [font-size](CSS-FONTS-4#propdef-font-size)' of the root element.

*   If the property contains the [rlh](CSS-VALUES-4#rlh) unit, add an edge between the property and the [line-height](CSS2#propdef-line-height)' of the root element.

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
> and font-size will behave as if the value [unset](CSS-CASCADE-5#valdef-all-unset) was specified.

## Navigation

- Parent: `substitution` — Substitution via var()
- Prev: `fallbacks-in-var-references` — Fallbacks In var() References

## Outgoing refs (15)

`webspec-index refs CSS-PROPERTIES-VALUES-API-1#dependency-cycles -d outgoing -l 15`

## Incoming refs (1)

- CSS-PROPERTIES-VALUES-API-1#contents
