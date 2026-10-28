Primary source consulted 24 October 2026: CSS Values and Units Level 4, Editor's Draft dated 24 August 2026.

- https://drafts.csswg.org/css-values-4/#round-infinities: zero step and two infinite operands produce NaN; an infinite value survives only a finite nonzero step. Finite value/infinite step depends on strategy, sign and signed zero.
- https://drafts.csswg.org/css-values-4/#simplify-a-calculation-tree: numeric conversion and operator folding require sufficient available information. Remaining context-dependent leaves do not supply resolved magnitudes merely by being leaves.
- https://drafts.csswg.org/css-values-4/#calc-ieee and https://drafts.csswg.org/css-values-4/#calc-type-checking: NaN propagation and the top-level conversion boundary must remain distinct from intermediate operands.
- https://drafts.csswg.org/css-values-4/#font-relative-lengths: em uses the applicable font size, so zero font size supplies a concrete zero basis for the proposed ordinary-size probes.

This mapping supplies special-value semantics and knowledge obligations. It does not certify a native evaluation trace, all floating-point conversions, or future browser observations.
