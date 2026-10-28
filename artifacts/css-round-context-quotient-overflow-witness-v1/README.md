# Finite quotient overflow witness

For A = 2^64 and B = 2^-64, both operands are normal binary32 numbers. A is an exact integer multiple of B, so every supported Round strategy must retain A in the exact interval model. The internal quotient 2^128 exceeds the largest finite binary32 value and its nearest-even overflow threshold. Negative A has the symmetric result.

The new browser cases use exact decimal spellings of A, B and 2A. A font-relative sign keeps the value contextual; the surrounding sign of 2A minus the positive rounded result, or 2A plus the negative rounded result, exposes infinity without relying on opacity's upper clamp. The zero-input phases before and after the nonzero phase are recovery controls. Browser behavior is not established by this package.

The pinned predecessor scalar adapter was compiled unchanged with rustc 1.92.0. All eight sign/strategy combinations returned signed infinity with the old branch and the exact signed A with the candidate. This is a small selected-input execution of an existing adapter, not a configured Gecko build or universal floating-point proof. Its assumptions about resolved numeric operands and unit joining remain unchanged.

Lean recompiled the existing integer interval model, instantiated its exact-multiple theorem for both signs, and checked the concrete quotient, finite-limit, overflow-threshold and normal-exponent arithmetic. These are witness checks, not a verified binary32 decoder, IEEE operation semantics, Rust refinement or additional canonical library coverage. The normal-value encoding and overflow threshold interpretation are explicit representation premises; the compiled scalar result supplies separate implementation evidence. The deliberately false finite-quotient control was rejected. Only the reused exact-multiple proof depends on propext; the other witness facts have no axioms.

The arithmetic family was already discovered and sampled. These eight browser targets add an observable route, not another bug count. The four witness declarations do not increment canonical CSS-spec coverage. The existing proof source and scalar adapter were copied or compiled read-only, and temporary compiler outputs were removed.

The current CSS Values 4 draft defines exact multiples and the four strategy choices in [Stepped Value Functions](https://drafts.csswg.org/css-values-4/#round-func). Its [numeric precision rules](https://drafts.csswg.org/css-values-4/#numeric-types) leave representation precision implementation-defined. The observer has a large finite margin and the chosen binary32 operands/results are exactly representable; no claim about complete Round conformance or the additional line-width strategy follows.

Reproduce without altering these saved results:

```sh
python3 -I -S -B artifacts/css-round-context-quotient-overflow-witness-v1/check.py ABSENT_OUTPUT_DIRECTORY
```
