# CSS-VARIABLES-1#replace-a-var-function

**replace a var() function** (algorithm)

**SHA**: hash:bbd1d53b85fa3adc1af1aaa906e7cf53baaaa54a20607744d77854e966496d9c

## Content

To **[replace a var() function](https://drafts.csswg.org/css-values-5/#replace-an-arbitrary-substitution-function)**, given a list of *arguments*:

1. Let *el* be the element that the style containing the [var()](https://drafts.csswg.org/css-variables-1#funcdef-var) function is being applied to. Let *first arg* be the first [\<declaration-value>](https://drafts.csswg.org/css-syntax-3/#typedef-declaration-value) in *arguments*. Let *second arg* be the \<declaration-value>? passed after the comma, or null if there was no comma.
2. [Substitute arbitrary substitution functions](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) in *first arg*, then [parse](https://drafts.csswg.org/css-syntax-3/#css-parse-something-according-to-a-css-grammar) it as a [\<custom-property-name>](https://drafts.csswg.org/css-variables-1#typedef-custom-property-name). If parsing returned a \<custom-property-name>, let *result* be the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) of the corresponding [custom property](https://drafts.csswg.org/css-variables-1#custom-property) on *el*. Otherwise, let *result* be the [guaranteed-invalid value](https://drafts.csswg.org/css-variables-1#guaranteed-invalid-value).

    > **Note:** Note: Determining the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) for the [custom property](https://drafts.csswg.org/css-variables-1#custom-property) implies that [property replacement](https://drafts.csswg.org/css-values-5/#property-replacement) takes place, which may cause a [cycle](https://drafts.csswg.org/css-values-5/#cyclic-substitution-contexts).
3. If the [custom property](https://drafts.csswg.org/css-variables-1#custom-property) named by the [var()](https://drafts.csswg.org/css-variables-1#funcdef-var)’s first argument is [animation-tainted](https://drafts.csswg.org/css-variables-1#animation-tainted), and the var() is being used in a property that is [not animatable](https://drafts.csswg.org/web-animations-1/#not-animatable), set *result* to the [guaranteed-invalid value](https://drafts.csswg.org/css-variables-1#guaranteed-invalid-value).
4. If *result* contains the [guaranteed-invalid value](https://drafts.csswg.org/css-variables-1#guaranteed-invalid-value), and *second arg* was provided, set *result* to the result of [substitute arbitrary substitution functions](https://drafts.csswg.org/css-values-5/#substitute-arbitrary-substitution-function) on *second arg*.
5. Return *result*.

## Navigation

- Parent: `using-variables` — Using Cascading Variables: the var() notation
- Prev: `typedef-var-args` — <var-args>

## Outgoing refs (13)

`webspec-index refs CSS-VARIABLES-1#replace-a-var-function -d outgoing -l 13`

## Incoming refs (1)

- CSS-VARIABLES-1#index-defined-here

Makes 3 calls: `webspec-index state CSS-VARIABLES-1#replace-a-var-function --calls`
