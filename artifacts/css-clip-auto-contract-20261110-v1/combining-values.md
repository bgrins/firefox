# CSS-VALUES-4#combining-values

**Combining Values: Interpolation, Addition, and Accumulation** (heading)

**SHA**: hash:525ff9eb18a45f0b497a8e73717a48325285ffcf9184e2189ab7dc81fd562ba0

## Content

Some procedures, for example [transitions](https://www.w3.org/TR/css-transitions/) and [animations](https://www.w3.org/TR/css-animations/), **combine** two CSS property values. The following combining operations—​on the two [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value) *VA* and *VB* yielding the computed value *Vresult*—​are defined. For operations that are not commutative (for example, matrix multiplication, or accumulation of mismatched transform lists) *VA* represents the first term of the operation and *VB* represents the second.

**interpolation** 

Given two property values *VA* and *VB*, produces an intermediate value *Vresult* at a distance of *p* along the interval between *VA* and *VB* such that *p* = 0 produces *VA* and *p* = 1 produces *V*B.The range of *p* is (−∞, ∞) due to the effect of [timing functions](https://drafts.csswg.org/css-easing-2/#easing-function). As a result, this procedure must also define extrapolation behavior for *p* outside \[0, 1\].

**addition** 

Given two property values *VA* and *VB*, returns the sum of the two properties, *V*result.

> **Note:** Note: While [addition](https://drafts.csswg.org/css-values-4#addition) can often be expressed in terms of the same weighted sum function used to define [interpolation](https://drafts.csswg.org/css-values-4#interpolation), this is not always the case. For example, interpolation of transform matrices involves decomposing and interpolating the matrix components whilst addition relies on matrix multiplication.

If a value type does not define a specific procedure for [addition](https://drafts.csswg.org/css-values-4#addition) or is defined as **not additive**, its addition operation is simply *Vresult* = *VB*.

**accumulation** 

Given two property values *VA* and *VB*, returns the result, *Vresult*, of combining the two operands such that *VB* is treated as a *delta* from *VA*.

> **Note:** Note: For many types of animation such as numbers or lengths, [accumulation](https://drafts.csswg.org/css-values-4#accumulation) is defined to be identical to [addition](https://drafts.csswg.org/css-values-4#addition).A common case where the definitions differ is for list-based types where [addition](https://drafts.csswg.org/css-values-4#addition) may be defined as appending to a list whilst [accumulation](https://drafts.csswg.org/css-values-4#accumulation) may be defined as component-based addition. For example, the filter list values blur(2) and blur(3), when added together would produce blur(2) blur(3), but when accumulated would produce blur(5).

If a value type does not define a specific procedure for [accumulation](https://drafts.csswg.org/css-values-4#accumulation), its accumulation operation is identical to [addition](https://drafts.csswg.org/css-values-4#addition).

These operations are only defined on [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value). (As a result, it is not necessary to define, for example, how to add a [\<length>](https://drafts.csswg.org/css-values-4#length-value) value of 15pt with 5em since such values will be resolved to their [canonical unit](https://drafts.csswg.org/css-values-4#canonical-unit) before being passed to any of the above procedures.)

### Range Checking

Interpolation can result in a value outside the valid range for a property, even if all of the inputs to interpolation are valid; this especially happens when *p* is outside the \[0, 1\] range, but some [easing functions](https://drafts.csswg.org/css-easing-2/#easing-function) can cause this to occur even within that range. If the final result *after* interpolation, addition, and accumulation is out-of-range for the target context the value is being used in, it does not cause the declaration to be invalid. Instead, the value must be clamped to the range allowed in the target context, exactly the same as [math functions](https://drafts.csswg.org/css-values-4#math-function) (see [§ 10.12 Range Checking](https://drafts.csswg.org/css-values-4#calc-range)).

> **Note:** Note: Even if interpolation results in an out-of-range value, addition/accumulation might "correct" the result and bring it back into range. Thus, clamping is only applied to the *final* result of applying all interpolation-related operations.

## Navigation

- Prev: `value-defs` — Value Definition Syntax
- Next: `textual-values` — Textual Data Types
- Children: 6
  - `combine` — combine
  - `interpolation` — interpolation
  - `addition` — addition
  - `not-additive` — not additive
  - `accumulation` — accumulation
  - `combining-range` — Range Checking

## Outgoing refs (7)

`webspec-index refs CSS-VALUES-4#combining-values -d outgoing -l 7`

## Incoming refs (4)

- CSS-VALUES-4#contents
- WEB-ANIMATIONS-1#animating-font-weight
- WEB-ANIMATIONS-1#animating-properties
- WEB-ANIMATIONS-1#animating-shadow-lists

### Possible effects

CSS-VALUES-4#combining-values

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VALUES-4#combining-values" --format markdown`
