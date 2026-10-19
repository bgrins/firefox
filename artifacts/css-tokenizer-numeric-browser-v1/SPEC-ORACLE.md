# Numeric literal oracle

Root consulted the current editor drafts on 2026-10-19:
- https://drafts.csswg.org/css-syntax-3/#consume-a-number
- https://drafts.csswg.org/css-values-4/#numeric-types
- https://drafts.csswg.org/css-color-4/#transparency

The number algorithm combines a base-ten number part with its signed power-of-ten exponent. Values 4 describes numeric quantities independently of their syntactic representation and assumes unbounded arithmetic in specifications, allowing implementation conversion when the numeric value is not representable. Opacity computes the specified number clamped to [0,1]. Each diagnostic complete literal equals exactly 0.5, already supported by the controls. Root therefore infers an expected computed opacity of 0.5; intermediate binary overflow or underflow is not an out-of-range final quantity. Huge actual values and zero are separate controls. This is a reviewed normative inference; browser outcomes are recorded separately.
