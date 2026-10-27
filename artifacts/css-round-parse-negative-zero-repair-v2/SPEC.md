# Oracle

Primary source checked 2026-10-24: [CSS Values 4, Editor’s Draft 24 August 2026](https://drafts.csswg.org/css-values-4/).

[round()](https://drafts.csswg.org/css-values-4/#funcdef-round) chooses the upper multiple for nearest ties, up, and the relevant negative to-zero cases. Its zero upper multiple has negative sign; exact multiples preserve their input. [pow() argument ranges](https://drafts.csswg.org/css-values-4/#funcdef-pow) map negative zero raised to a negative odd integer to negative infinity, while positive zero gives positive infinity. [Nested arithmetic](https://drafts.csswg.org/css-values-4/#calc-ieee) retains these distinctions inside the calculation; [clamp()](https://drafts.csswg.org/css-values-4/#funcdef-clamp) then maps the negative infinity to zero and positive infinity to one. Thus the observer produces ordinary finite opacity values with an exact zero/one oracle.

The exponent is exactly -1 and all finite operands are small dyadic numbers. No approximate decimal or representation-limit premise is needed for these cases. The single known infinite-step control checks unchanged behavior; it is not the separately observed unknown-value/infinite-step defect.
