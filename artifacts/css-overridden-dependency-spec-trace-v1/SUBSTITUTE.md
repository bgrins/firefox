# CSS-VALUES-5#substitute-arbitrary-substitution-function

**substitute arbitrary substitution functions** (algorithm)

**SHA**: hash:6b2a51b0538dade54a602cc25535750a94d9cd637a495ddd6e0e82124deef42a

## Content

To **substitute arbitrary substitution functions** in a sequence of [component values](CSS-SYNTAX-3#component-value) *values*, given an optional [substitution context](CSS-VALUES-5#substitution-context) *context*:

1. [Guard](CSS-VALUES-5#guarded) *context* for the remainder of this algorithm. If *context* is marked as a [cyclic substitution context](CSS-VALUES-5#cyclic-substitution-contexts), return the [guaranteed-invalid value](CSS-VARIABLES-2#guaranteed-invalid-value).
2. [For each](INFRA#list-iterate) [arbitrary substitution function](CSS-VALUES-5#arbitrary-substitution-function) *func* in *values* (ordered via a depth-first pre-order traversal) that is not nested in the contents of another arbitrary substitution function:

    1. [Substitute early-invoked functions](CSS-VALUES-5#substitute-early-invoked-functions) in *func*’s contents, and let *early result* be the result.
    2. If *early result* contains the [guaranteed-invalid value](CSS-VARIABLES-2#guaranteed-invalid-value), replace *func* in *values* with the guaranteed-invalid value and [continue](INFRA#iteration-continue).
    3. [Parse](CSS-SYNTAX-3#css-parse-something-according-to-a-css-grammar) *early result* according to *func*’s [argument grammar](CSS-VALUES-5#argument-grammar). If this returns failure, replace *func* in values with the [guaranteed-invalid value](CSS-VARIABLES-2#guaranteed-invalid-value) and [continue](INFRA#iteration-continue); otherwise, let *arguments* be the result.
    4. [Replace an arbitrary substitution function](CSS-VALUES-5#replace-an-arbitrary-substitution-function) for *func*, given *arguments*, as defined by that function. Let *result* be the returned list of [component values](CSS-SYNTAX-3#component-value).
    5. If *result* contains the [guaranteed-invalid value](CSS-VARIABLES-2#guaranteed-invalid-value), replace *func* in *values* with the guaranteed-invalid value. Otherwise, replace *func* in *values* with *result*.
3. If *context* is marked as a [cyclic substitution context](CSS-VALUES-5#cyclic-substitution-contexts), return the [guaranteed-invalid value](CSS-VARIABLES-2#guaranteed-invalid-value).
4. Return *values*.

## Navigation

- Parent: `substitution` — Substitution
- Prev: `replace-an-arbitrary-substitution-function` — replace an arbitrary substitution function
- Next: `substitution-context` — substitution context

## Outgoing refs (12)

`webspec-index refs CSS-VALUES-5#substitute-arbitrary-substitution-function -d outgoing -l 12`

## Incoming refs (17)

`webspec-index refs CSS-VALUES-5#substitute-arbitrary-substitution-function -d incoming -l 17`

Called from 9 algorithms: `webspec-index state CSS-VALUES-5#substitute-arbitrary-substitution-function --callers` · makes 2 calls: `webspec-index state CSS-VALUES-5#substitute-arbitrary-substitution-function --calls`
