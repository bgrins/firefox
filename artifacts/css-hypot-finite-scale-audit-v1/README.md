# Finite-scale CSS hypot numerical robustness audit

Observable repro established in the existing System Firefox158 browser. This is a source-motivated numerical robustness lead, not a formal discovery, local-branch validation, accepted fix or assigned bug ID. Both owned about:blank tabs were closed and temporary elements removed. No browser restart, build or native/index/epoch mutation occurred.

| Opacity expression | Mathematical result | Observed computed value |
| --- | --- | --- |
| calc(hypot(1e20, 0) / 2e20) | 0.5 | 1; specified calc(infinity) |
| calc(hypot(1e-30, 0) / 2e-30) | 0.5 | 0; specified calc(0) |
| Direct ratios and abs() at both scales | 0.5 | 0.5 |
| hypot(3,4)/10 and normalized hypot at1e19 | 0.5 | 0.5 |
| Normalized hypot at1e-20 | 0.5 | 0.499999 |

Exact dyadic witnesses remove decimal-input uncertainty: x=2^64, denominator2^65 produces1 for both hypot(x,0) and hypot(x); x=2^-80, denominator2^-79 produces0. Direct ratios produce0.5. POWER-OF-TWO-OBSERVATION.json retains the exact decimal literals and actual tool response. All four inputs/denominators are exactly representable finite binary32 numbers. Their squares are2^128 (overflow in binary32) and2^-160 (below the rounding threshold for the smallest binary32 subnormal). The bounded struct-rounding calculation reproduces these intermediate failures; using double intermediates returns0.5. This is a two-witness arithmetic check, not a universal native proof.

Normal and moderately large/small inputs do not exhibit the catastrophic behavior because their squares remain in range. The underlying hypot result and normalized final0.5 remain representable even for the failing inputs. The visible effect is therefore avoidable intermediate overflow/underflow, rather than simply asking opacity to hold an enormous number. Length analogues similarly produce0px or the implementation's maximum length rather than0.5px, while direct ratios produce0.5px.

SOURCE.json authenticates the exact local closure-v3 baseline calc.rs and records both affected branches. resolve_internal squares each f32 input, adds the squares and takes sqrt. The simplifier independently performs the same sequence using try_op with multiplication/addition/sqrt; it does not avoid the problem. Literal declarations already serialize to infinity/zero, so these browser witnesses primarily expose constant folding. They do not establish execution of the contextual resolver. Searchfox captures show the same overall algorithms; the separately pinned local source contains the accepted shared-branch modifications.

[CSS Values4 exponential functions](https://drafts.csswg.org/css-values-4/#exponent-funs) defines hypot as vector length and identifies the single-argument result with absolute value. However, [numeric types](https://drafts.csswg.org/css-values-4/#numeric-types) explicitly leaves precision, supported range and closest-value selection implementation-defined. [Range checking](https://drafts.csswg.org/css-values-4/#calc-range) applies property clamps to top-level calculations. These support a well-motivated robustness repair, but this audit does not claim a settled conformance violation or cross-engine interoperability result at arbitrary extremes. The primary draft was read on2026-10-29.

[CSS Values4 argument ranges](https://drafts.csswg.org/css-values-4/#exponent-argument-ranges) makes NaN infectious, including hypot(infinity,NaN), unlike JavaScript Math.hypot. A future repair must preserve that precedence, positive magnitude/zero, genuine infinity, units and unresolved-context behavior. Fixing only resolve_internal would leave the demonstrated constant-folding failure intact.

Dedup: the authenticated147-accepted/148-tracked ledger has no exact hypot entry. Related accepted62,119,128 and145 concern decimal token range, nonfinite lengths, mod/rem or round arithmetic. Bug2083404 fixes negation distribution, not finite-scale squaring; bug1814469 introduced hypot; bug2075532 imported NaN/infinity WPT coverage. Live records are retained. Existing computed/serialization WPT captures cover moderate3e9/4e9, units, contextual expressions, negation and nonfinite arguments, but no normalized finite-extreme witness was found. Indexed Bugzilla searches did not surface an exact duplicate; direct REST summary search was unavailable. This is bounded dedup evidence, not proof that no matching report exists.

Next: prepare an artifact-only two-branch repair proposal and WPTs for exact dyadics, ordinary values, units, unresolved context and nonfinite precedence. Native implementation, paired local browser validation and formal attribution remain separate gates. No native file is changed by this audit.
