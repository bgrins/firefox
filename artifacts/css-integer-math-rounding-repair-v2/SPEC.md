Read 2026-10-24. Primary specification: [CSS Values and Units Level 4](https://drafts.csswg.org/css-values-4/), Editor’s Draft 24 August 2026.

§9.1 Numeric Functions requires nearest-integer conversion when a noninteger numeric function occupies an integer position. §5.2 selects the positive-infinity direction at equal distances. §10.12 applies rounding to the top-level calculation, not nested operations. The target is therefore floor(x + 1/2), followed by the supported-range policy, where x is the calculation result.

§5 explicitly leaves numeric precision/range and the meaning of closest supported value implementation-defined. This proposal targets avoidable loss in the final rounding operation on already exactly representable binary32 inputs; it does not establish exact evaluation of arbitrary authored decimal calculations or a universally mandated signed32 range. Literal reference checks calibrate the larger tested range. Ordinary below-half behavior is independently included. Browser results remain unmeasured.

[The Rust Reference, numeric casts](https://doc.rust-lang.org/reference/expressions/operator-expr.html#numeric-cast) specifies lossless binary32 widening and saturating float-to-integer conversion, with NaN mapping to zero. The patch preserves the integer cast and the existing preceding normalization. Its change is the precision of the bias addition.
