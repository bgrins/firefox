# CSS-VALUES-5#property-replacement

**replace substitution functions in a property** (algorithm)

**SHA**: hash:c982d70262c9366a7ec3b832f129af3f3314c1241448d5d1f66493482cd9f382

## Content

To **replace substitution functions in a property** *prop*:

1. [Substitute arbitrary substitution functions](https://drafts.csswg.org/css-values-5#substitute-arbitrary-substitution-function) in *prop*’s value, given «"property", *prop*’s name» as the [substitution context](https://drafts.csswg.org/css-values-5#substitution-context). Let *result* be the returned [component value](https://drafts.csswg.org/css-syntax-3/#component-value) sequence.
2. If *result* contains the [guaranteed-invalid value](https://drafts.csswg.org/css-variables-2/#guaranteed-invalid-value), *prop* is [invalid at computed-value time](https://drafts.csswg.org/css-values-5#invalid-at-computed-value-time); return.
3. [Parse](https://drafts.csswg.org/css-syntax-3/#css-parse-something-according-to-a-css-grammar) *result* according to *prop*’s grammar. If this returns failure, *prop* is [invalid at computed-value time](https://drafts.csswg.org/css-values-5#invalid-at-computed-value-time); return.
4. Otherwise, replace *prop*’s value with the parsed result.

## Navigation

- Parent: `resolve-property` — Resolving in Properties

## Outgoing refs (6)

`webspec-index refs CSS-VALUES-5#property-replacement -d outgoing -l 6`

## Incoming refs (9)

`webspec-index refs CSS-VALUES-5#property-replacement -d incoming -l 9`

### Possible effects

CSS-VALUES-5#property-replacement

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VALUES-5#property-replacement" --format markdown`

Makes 2 calls: `webspec-index state CSS-VALUES-5#property-replacement --calls`
