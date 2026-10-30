# CSS-VALUES-5#property-replacement

**replace substitution functions in a property** (algorithm)

**SHA**: hash:6b2a51b0538dade54a602cc25535750a94d9cd637a495ddd6e0e82124deef42a

## Content

To **replace substitution functions in a property** *prop*:

1. [Substitute arbitrary substitution functions](CSS-VALUES-5#substitute-arbitrary-substitution-function) in *prop*’s value, given «"property", *prop*’s name» as the [substitution context](CSS-VALUES-5#substitution-context). Let *result* be the returned [component value](CSS-SYNTAX-3#component-value) sequence.
2. If *result* contains the [guaranteed-invalid value](CSS-VARIABLES-2#guaranteed-invalid-value), *prop* is [invalid at computed-value time](CSS-VALUES-5#invalid-at-computed-value-time); return.
3. [Parse](CSS-SYNTAX-3#css-parse-something-according-to-a-css-grammar) *result* according to *prop*’s grammar. If this returns failure, *prop* is [invalid at computed-value time](CSS-VALUES-5#invalid-at-computed-value-time); return.
4. Otherwise, replace *prop*’s value with the parsed result.

## Navigation

- Parent: `resolve-property` — Resolving in Properties

## Outgoing refs (6)

`webspec-index refs CSS-VALUES-5#property-replacement -d outgoing -l 6`

## Incoming refs (9)

`webspec-index refs CSS-VALUES-5#property-replacement -d incoming -l 9`

Makes 2 calls: `webspec-index state CSS-VALUES-5#property-replacement --calls`
