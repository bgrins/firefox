# Scalar Round classification

The [Round infinity rules](https://drafts.csswg.org/css-values-4/#round-infinities) classify zero steps and pairs of infinite operands as NaN. An infinite value with a finite nonzero step retains its sign and infinity. NaN propagation and top-level censorship follow the [calculation rules](https://drafts.csswg.org/css-values-4/#calc-type-checking). The [simplification algorithm](https://drafts.csswg.org/css-values-4/#simplify-a-calculation-tree) does not justify treating an unresolved child's coefficient as its eventual value.

REACHED for the scalar classifications tested here. Four currently implemented strategies are covered; this is not all current Round syntax. CSS numeric precision, signed-zero identity, complete relative-value semantics, targetless API easing policy, and native refinement are not proved by this package.
