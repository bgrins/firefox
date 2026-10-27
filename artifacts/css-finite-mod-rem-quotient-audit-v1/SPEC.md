Primary sources inspected 2026-10-24:

- https://drafts.csswg.org/css-values-4/#round-func — integer-multiple definition, sign convention and finite mod/rem examples.
- https://drafts.csswg.org/css-values-4/#round-infinities — zero/infinite argument exceptions and finite-dividend identity cases.
- https://drafts.csswg.org/css-values-4/#numeric-types — implementation-defined range and precision, including closest-value policy.

The expected finite table uses exact integer division on the calibrated operands. It is not generated from the native floating formula, the browser result, or the earlier Round candidate. The range/precision qualification is part of the claim, not an executable failure waiver.
