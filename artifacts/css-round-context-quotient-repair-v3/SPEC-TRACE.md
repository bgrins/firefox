# Directed Round interval contract

Primary source checked 2026-10-28: [CSS Values4 round](https://drafts.csswg.org/css-values-4/#round-func), [argument ranges](https://drafts.csswg.org/css-values-4/#round-infinities), [numeric precision](https://drafts.csswg.org/css-values-4/#numbers). The spec CLI remains unavailable; direct official draft fallback was used. No automated route enumeration is claimed.

For finite resolved operands, Round selects enclosing integer multiples of the absolute step. Down/up select lower/upper; nearest ties choose upper; to-zero chooses smaller magnitude. Exact multiples retain the input and its zero sign. A zero lower bound is positive; a zero upper bound is negative. Zero steps produce NaN; special infinities and contagious NaN retain their separate rules. CSS numeric precision is implementation-defined, so this does not mandate a particular machine algorithm.

**REACHED, with explicit numeric representation premise:** for exactly represented binary32 step b=11184811/33554432 and value1, 2b<1<3b. Down must choose the lower multiple. Rounding the quotient to3 before choosing the interval selects a different multiple. The retained browser calibration and exact dyadic oracle support the concrete discrepancy; no universal IEEE/native refinement follows.
