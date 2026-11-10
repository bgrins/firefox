# CSS-VARIABLES-1#replace-a-var-function

**replace a var() function** (algorithm)

**SHA**: hash:72c4b00afaa33f30ded58f4b1e4595c7155bb410d01e0d24b8157cdbdf101e40

## Content

To **[replace a var() function](CSS-VALUES-5#replace-an-arbitrary-substitution-function)**, given a list of *arguments*:

1. Let *el* be the element that the style containing the [var()](CSS-VARIABLES-1#funcdef-var) function is being applied to. Let *first arg* be the first [\<declaration-value>](CSS-SYNTAX-3#typedef-declaration-value) in *arguments*. Let *second arg* be the \<declaration-value>? passed after the comma, or null if there was no comma.
2. [Substitute arbitrary substitution functions](CSS-VALUES-5#substitute-arbitrary-substitution-function) in *first arg*, then [parse](CSS-SYNTAX-3#css-parse-something-according-to-a-css-grammar) it as a [\<custom-property-name>](CSS-VARIABLES-1#typedef-custom-property-name). If parsing returned a \<custom-property-name>, let *result* be the [computed value](CSS-CASCADE-5#computed-value) of the corresponding [custom property](CSS-VARIABLES-1#custom-property) on *el*. Otherwise, let *result* be the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value).

    > **Note:** Note: Determining the [computed value](CSS-CASCADE-5#computed-value) for the [custom property](CSS-VARIABLES-1#custom-property) implies that [property replacement](CSS-VALUES-5#property-replacement) takes place, which may cause a [cycle](CSS-VALUES-5#cyclic-substitution-contexts).
3. If the [custom property](CSS-VARIABLES-1#custom-property) named by the [var()](CSS-VARIABLES-1#funcdef-var)’s first argument is [animation-tainted](CSS-VARIABLES-1#animation-tainted), and the var() is being used in a property that is [not animatable](WEB-ANIMATIONS-1#not-animatable), set *result* to the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value).
4. If *result* contains the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value), and *second arg* was provided, set *result* to the result of [substitute arbitrary substitution functions](CSS-VALUES-5#substitute-arbitrary-substitution-function) on *second arg*.
5. Return *result*.

## Navigation

- Parent: `using-variables` — Using Cascading Variables: the var() notation
- Prev: `typedef-var-args` — <var-args>

## Outgoing refs (13)

`webspec-index refs CSS-VARIABLES-1#replace-a-var-function -d outgoing -l 13`

## Incoming refs (1)

- CSS-VARIABLES-1#index-defined-here

### Possible effects

CSS-VARIABLES-1#replace-a-var-function

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VARIABLES-1#replace-a-var-function" --format markdown`

Makes 3 calls: `webspec-index state CSS-VARIABLES-1#replace-a-var-function --calls`
