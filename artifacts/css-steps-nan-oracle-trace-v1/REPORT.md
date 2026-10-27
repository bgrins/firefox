# steps() NaN oracle: normative boundary and originating implementations

**Question:** Does `steps(calc(0 / 0), jump-none)` have to be rejected, while `steps(calc(1), jump-none)` computes to two steps?

**Scenario:** A well-typed, context-free number calculation in a CSS easing value. No variables, font units, target element, animated provider, or unsupported feature is involved. Literal `steps(1, jump-none)` is a separate invalid control.

## Normative call chain

1. CSS easing parsing selects the step function. [Easing 1 §2.3](https://drafts.csswg.org/css-easing-1/#step-easing-functions) requires a positive integer greater than one for `jump-none`. [Easing 2 §2.3](https://drafts.csswg.org/css-easing-2/#step-easing-functions) expresses the same minimum and says values below it make the function invalid. Neither section identifies a NaN exception or specifies an intermediate positive-integer clamp followed by a separate rejection.
2. The argument is a numeric math function. [Values 4 §9.1](https://drafts.csswg.org/css-values-4/#numeric-function) says numeric functions returning out-of-range values “never cause a declaration to become invalid.” Their results clamp to the allowed context range at computed/used time; integer contexts also round. This differs from literal range validation.
3. [Values 4 §10.9.2](https://drafts.csswg.org/css-values-4/#top-level-calculation) makes division zero/zero NaN, then censors it to zero on leaving the top-level calculation. `steps()` is not an enclosing math calculation. This is not invalid-at-computed-value-time handling, nor propagation through the CSS `clamp()` math function.
4. [Values 4 §10.12](https://drafts.csswg.org/css-values-4/#calc-range) applies numeric clamping/rounding at the top-level calculation. Reading the conditional step minimum as the argument's context range gives **NaN → 0 → 2**, and **calc(1) → 2**. This is the strongest cross-module reading, not evidence of a special NaN rejection rule.
5. For `updateTiming({easing: ...})`, [Web Animations §6.5.4](https://drafts.csswg.org/web-animations-1/#update-the-timing-properties-of-an-animation-effect) step 4 throws if easing cannot parse, before step 5 assigns timing fields. Its separate NaN checks concern numeric iterations/duration members, not a NaN expression inside the easing string. It supplies no new step-count rule. A targetless call does not change this context-free trace.

**Verdict: INCONCLUSIVE** — the drafts strongly favor clamping both calculations to two, but the retrieved material does not explicitly settle the interaction between Easing's conditional validity prose and Values' numeric-function range rule. In particular, no located CSSWG decision authorizes rejecting the censored-zero case while clamping the finite-one case. The incompatible test expectations therefore cannot safely be treated as a jointly settled landing oracle.

| Alternative route | Assessment |
|---|---|
| Reject because the calculation contains NaN | Contradicts the explicit censor-to-zero rule; no such exception found. |
| Treat the censored value as if the author wrote literal zero | Loses numeric-function provenance and bypasses the range rule. |
| Clamp to generic positive integer 1, then reject `jump-none` | Actual Chromium ordering below; not itself a normative decision. |
| Reject literal one | Ordinary literal validation remains intact; no conflict with calculation clamping. |

## What the originating changes actually establish

[WPT 52199](https://github.com/web-platform-tests/wpt/pull/52199) imports [Chromium change 6494566](https://chromium-review.googlesource.com/c/chromium/src/+/6494566), final revision `5a3b10acab0bb826a848a2f7285e794968249536`. Its description correctly addresses NaN censoring. Exact source files are archived here:

- `ConsumePositiveInteger` chooses stored `kPositiveInteger`.
- New `GetValueIfKnown` calls `ClampDouble`; that helper converts NaN to zero.
- `ClampToPermittedRange` clamps this stored range to at least one and rounds.
- `ConsumeSteps` then rejects a known count less than two for `jump-none`.

Thus the new invalid test follows **NaN → 0 → 1 → rejection**. The same historical parser also rejects known `calc(1)` through the final guard. This is not a demonstrated deliberate semantic distinction between NaN and finite calculations. No browser was run here; these are source-derived paths.

[WPT 50533](https://github.com/web-platform-tests/wpt/pull/50533) originates in [WebKit bug 278925](https://bugs.webkit.org/show_bug.cgi?id=278925) / [PR 32946](https://github.com/WebKit/WebKit/pull/32946), commit `2047aa6f9356073f2eac55f0ea91d31bd024717a`. The change explicitly removes eager calc resolution. Its parser rejects jump-none only when `isOne()` identifies a literal; math values remain unevaluated. `CSSStepsTimingFunctionValue::createTimingFunction` resolves the integer and clamps it with `max(steps, 2)` for jump-none. This supports the finite test's architecture. This audit does not trace WebKit's entire NaN resolver or claim a WebKit NaN browser result.

Both WPT PR issue-comment lists were empty. The Chromium comments fetched add no steps-specific rationale; WebKit review approves removal of eager resolution without a NaN-specific rule. Chronology cannot resolve the normative conflict.

## CSSWG decision and search limits

[CSSWG 7067, resolution](https://github.com/w3c/csswg-drafts/issues/7067#issuecomment-1111211295) explicitly decides that top-level NaN is coerced to zero. It does **not** decide whether the conditional jump-none minimum is the range to clamp to. The issue's title proposing invalid-at-computed-value-time is not its resolution.

The bounded API searches retained here found 9 jump-none results and 18 steps+NaN results (all returned), 40 NaN+clamp results, and 103 steps+calc results (first 50 only). Relevant complete comment threads 7067, 10809 and 11211 were read. 11211 concerns unresolved `linear()` canonicalization timing, not this conditional minimum. No specific contrary decision was located; this is not an exhaustive claim about all CSSWG discussions. `webspec-index` was unavailable, so primary HTML/API and manual anchor validation were used instead of claiming a complete indexed trace.

## Small next experiment and missing decision

Keep the existing invalid-NaN WPT unchanged. Run it beside the finite constant diagnostic and literal controls as **oracle-conflict observations**, recording CSS specified retention, computed easing, targetless WAAPI acceptance/throw, and updateTiming atomicity separately. Do not count a NaN expectation reversal as a Firefox regression or success without adjudicating the oracle. The finite-only review patch remains unaccepted/uncompiled; special-casing NaN merely to satisfy both tests would need new normative justification.

The precise question for a future CSSWG/WPT clarification is: **Does the `jump-none` conditional minimum define the numeric function's clamping range, including a top-level NaN censored to zero, or is it an independent validity check after generic `<integer [1,∞]>` computation? If the latter, why should `calc(1)` be accepted?** A decision or explicit spec/test correction at this boundary is sufficient; no font/element/timeline API design is needed to ask it. No issue was filed and no metadata was changed.

This is the previously identified steps prerequisite associated with bug 2037743, not held sign-folding repair 120, a new accepted fix, or evidence of a new security defect. The current audit sharpens the existing blocker; it does not establish a landable finite-only repair.
