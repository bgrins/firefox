Primary sources inspected2026-10-24:

- CSS Values4: https://drafts.csswg.org/css-values-4/#round-func and #round-infinities define modulo/rem signs, zero and exceptional argument behavior.
- CSS Values4: https://drafts.csswg.org/css-values-4/#numeric-types leaves numeric range/precision and closest-supported rounding implementation-defined.
- Rust Reference: https://doc.rust-lang.org/reference/expressions/operator-expr.html#arithmetic-and-logical-binary-operators defines percent by truncating division and dividend sign. This is not IEEE remainder's nearest-integer quotient.
- Rust f32 documentation: https://doc.rust-lang.org/std/primitive.f32.html#method.rem_euclid explicitly describes the rounded divisor-endpoint case. We use this as a numerical limitation comparison, not as the actual candidate operator or proof of native compiler lowering.

The exact integer principal witnesses and rational oracle are independent of quotient reconstruction. No universal CSS binary32 precision mandate or whole-operator native proof is claimed.
