# Isolated context-free jump-none minimum

**Distinct from held120 and accepted121; already identified in the unexecuted steps prerequisite work.** The smallest useful browser experiment is constant `calc(1)` in `steps(..., jump-none)` through CSS and WAAPI, with literal rejection controls. No font, element provider, contextual admission or held repair is needed. This is not a new discovery or accepted fix.

I read held120's actual `sign-native.draft.json`, accepted patch, and `css-integer-consumer-root-review-v1/REPORT.md`. Held120 changes `leaf.unitless_value()` to `leaf.canonical_value()` in generic sign folding and adds eleven font-basis cases. Its installation hold concerns newly unresolved relative expressions reaching integer consumers. This isolated issue instead concerns an already context-free boxed calculation and the easing function's minimum of two. Accepted121 fixes Integer's stored range when resolving; its positive range is one, so it does not supply jump-none's extra minimum or remove the parser rejection.

The ledger already records `css-steps-context-repair-v1` (HOLD) and `css-steps-keyframe-record-repair-v1` (guarded, unbuilt). Their core helper/admission sketches include this minimum correction, but combine it with unresolved-context work. Neither is an accepted installed repair. Extract the bounded constant part, rather than claiming a newly found defect. The previous API plan omitted this concrete retained-record prototype: reuse its unmerged-source analysis for future contextual work, not the plan's alternative new scheduling flag. Existing source grouping/provenance limitations remain real.

## Deciding specification and WPT evidence

[CSS Easing1 steps](https://drafts.csswg.org/css-easing-1/#funcdef-steps) requires at least two for jump-none. [CSS Values4 numeric functions](https://drafts.csswg.org/css-values-4/#numeric-function) distinguishes literal range rejection from numeric-function computation; its numeric-functions text requires computed/used clamping and integer rounding. [Math range checking](https://drafts.csswg.org/css-values-4/#calc-range) applies this at the top-level calculation. Therefore the constant `calc(1)` produces the minimum two, while literal `1` remains invalid. No contextual provider is consulted. **REACHED** for that finite constant distinction.

Existing WPT explicitly covers it: `timing-functions-syntax-valid.html` admits `steps(calc(1), jump-none)` and `timing-functions-syntax-computed.html` expects `steps(2, jump-none)`. The latter arrived in commit68750d4, February2025, from WebKit bug278925/WPT50533 (“CSS timing functions should not eagerly evaluate calc()”). It is not a hypothetical new oracle.

The NaN conflict is genuine and must be reported before accepting a repair. `step-timing-functions-syntax.html` expects `steps(calc(0/0), jump-none)` to be invalid. Its exact addition is commit87bd604, May2025, from Chromium/WPT52199; the commit says NaN becomes zero at top-level. It is newer than the finite calc test, not an ancient pre-calc leftover. [Values4 NaN handling](https://drafts.csswg.org/css-values-4/#calc-type-checking) censors a top-level NaN to zero; applying the numeric-function range rule then suggests clamping that zero to two. Easing's plain integer range does not explain treating this boxed math result differently from calc(0). The source history demonstrates the conflicting test choices, not a CSSWG resolution. Primary PR/bug page retrieval failed; no discussion outcome is invented.

Keep the existing NaN WPT unchanged during the experiment and explicitly record a candidate unexpected FAIL if admission changes. Do not silently add expected-failure metadata or assert this contradiction is resolved because the finite tests improve. Finite correction is independently observable; landing the general clamp still needs agreement on that NaN oracle. Special-casing the text `0/0`, using a guessed font, or preserving an old count are not proposed solutions.

## Small source-only candidate

`candidate-review-only.patch` is a one-file, uncompiled sketch over the retained committed easing source. It is **not execution-ready or accepted**. Its only intended behavior changes are:

1. Keep the `steps.resolve().is_none()` admission rejection. The proof obligation protecting every existing context-free unwrap remains intact; contextual syntax is not newly admitted.
2. Reject jump-none literal1 via Integer::get(), which explicitly distinguishes an inline literal from boxed math. Existing positive parsing rejects literal0/negative. All math remains boxed even after simplification in the inspected Integer parser.
3. Clamp the resolved count to two only for jump-none in the shared context-free conversion. Other positions retain their current fix121 result. CSS ToComputedValue, Gecko CSS keyframe publication, Servo's backend, effect-level WAAPI and both keyframe forms already route through that conversion. No signatures, storage, grouping, lifetime, target selection or compositor types change.

This also admits context-free NaN and clamps it to two in this sketch; that is the disclosed conflicting test, not a hidden exemption. The unresolved-context guard is intentionally still present, including for API strings. Literal rejection and updateTiming atomicity remain required. Existing numeric normalization/rounding must remain untouched.

## Concrete next experiment

The new scratch WPT has18 tests: four finite boxed counts (`calc(1)`, `calc(0)`, `calc(-10)`, `calc(1.4)`) across two CSS longhands, targetless effect timing and per-keyframe easing; plus CSS literal rejection and failed-update atomicity. Literal2 calibrates serialization/output before target observations. Unsupported constant calc is an explicit admission failure, never a passing oracle. Targetless progress and keyframe opacity sample0.75 with expected1 for steps(2,jump-none), away from discontinuities. Callbacks have not run.

First capture baseline18 plus existing easing syntax/computed and NaN tests using the current restored browser. Then, only after source review/explicit activation, compare this one-file candidate and restore it. Preserve all raw failures, including unrelated existing contextual failures and the NaN contradiction; do not claim complete bug2037743 support. Include existing AnimationEffect/updateTiming and keyframe constructor/processing tests as API controls. No new runner is necessary.

No new contextual lifecycle fixture is needed for this distinct finite experiment. The existing nine-case contextual draft and six retained-record draft remain the later source-owned tests; their unsupported syntax must remain feature-admission failures, not be converted to passing numerical checks. The finite experiment does not unblock held120 or the Round candidate by itself.

Validation here is only JavaScript syntax and18 unique inert registrations. No browser, native application, Rust typecheck, build, canonical/index/ledger writes, new proof or accepted-bug credit. The source sketch and NaN interpretation require review before any candidate run.
