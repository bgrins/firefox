# CSS-PROPERTIES-VALUES-API-1#fallbacks-in-var-references

**Fallbacks In var() References** (heading)

**SHA**: hash:959d45c42d151096bbc21a074aff849f48c64f3f393dfc285c437eb326f066c7

## Content

References to registered custom properties using the [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var) function may provide a fallback. However, the fallback value must match the [syntax definition](https://www.w3.org/TR/css-properties-values-api-1#syntax-definition) of the custom property being referenced, otherwise the declaration is [invalid at computed-value time](https://www.w3.org/TR/css-variables-1/#invalid-at-computed-value-time).

> **Note:** Note: This applies regardless of whether or not the fallback is being used.

## Navigation

- Parent: `substitution` — Substitution via var()
- Next: `dependency-cycles` — Dependency Cycles via Relative Units

## Outgoing refs (3)

- CSS-VARIABLES-1#funcdef-var
- CSS-PROPERTIES-VALUES-API-1#syntax-definition
- CSS-VARIABLES-1#invalid-at-computed-value-time

## Incoming refs (1)

- CSS-PROPERTIES-VALUES-API-1#contents
