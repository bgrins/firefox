# Specified-origin steps admission companion

The canonical numeric pipeline already proves the arithmetic needed here. It does not encode the steps consumer's literal-versus-calculation admission distinction. A search of the current canonical Lean sources found no jump-none/StepsTiming consumer. Existing integer-range symbolic research concerns omitted stored-range policy over binary32 inputs, not this subsequent conditional consumer range. This artifact adds only that missing consumer adapter.

Reuse map:

| Existing result | Use here |
|---|---|
| CssNumericCensorship.censor_iff / complete_nan / complete_zero | Existing exceptional value model censors NaN to zero and applies range clipping; no new arithmetic implementation. |
| CssIntegerRounding.round / rounded / round_integer | Existing nearest-integer/ties-positive convention. |
| CssNumericFinalization.finish_bounded | Supplies normalized_bounded via the actual canonical integer finalizer, including its exceptional-value domain. |
| CssIntegerClipping.round_clip | Existing general commute result; no duplicate theorem is added. |
| css-integer-range-symbolic-v1 | Existing separate binary32/native-expression reasoning; not imported as a Lean certificate. |

Steps.lean introduces Specified.literal and Specified.calculation with Option Int for resolution availability. The exact modeled old path validates either normalized result against the consumer minimum; the repaired path retains literal validation but clamps resolved calculations, preserving unresolved rejection. Position.ordinary represents positions with minimum one; jumpNone has minimum two. There is no CSS token parser or invented element/font context.

The substantive consumer theorems cover arbitrary normalized counts and origins: old successful results remain exactly equal; all literals and unresolved calculations retain their behavior; ordinary-position calculations remain unchanged under the explicit positive-normalization premise; and, among positive normalized counts, the old jump-none rejection occurs exactly at one. The repaired result meets the consumer minimum and stays below a supplied machine bound when both the normalized integer and the minimum fit that bound.

integerNormalize reuses canonical completion and rounding, with a supplied finite upper bound. The adapter's normalized-count theorems do not assume a particular floating-point representation. Applying them to Rust requires showing that Integer::resolve produces the supplied integer and respects the chosen machine bound; this artifact does not prove binary32/binary64 conversion or signed32 saturation. The concrete examples use bound4, sufficient to expose the lower-range distinction without claiming a Firefox upper-range model. Infinity behavior is inherited in the symbolic canonical provider, not newly refined to Stylo.

The NaN/zero examples exercise the actual canonical provider and show original rejection versus repaired two, while literal one and unresolved calculations remain rejected. Contextual integer admission remains outside scope. The model says nothing about timing/getKeyframes serialization, DOM lifecycle, WPT process behavior, or whole-CSS parsing.

There are 10 named standalone audits and 11 positive examples, with only ordinary Lean axioms reported. Three same-claim false controls assert that literal one clamps, calculated NaN is rejected, or an unresolved calculation is admitted. The NaN negative rewrites using the proved concrete repaired_nan result before decide; its original proposition is unchanged. Exact full diagnostics and exit1 are required. The gate also rejects the retained failed change-tactic attempt, reduction failures, unknown identifiers, altered propositions, extra errors and wrong exits. A first strict replay rejected a deprecation warning; replacing if_true with ite_true produced the final clean source. Neither failed attempt is credited as a semantic rejection.

All compilation uses pinned Lean4.35.0-rc4 with one thread and existing pinned canonical oleans. Own temporary compiler output is removed; the shared .lake, canonical sources, indices and native files are untouched. No canonical audit/case/coverage totals are incremented. Existing arithmetic proof transfers receive no new numerical/normative coverage credit. Browser acceptance remains entirely separate.

Replay into an absent directory:

    python3 -I -S -B artifacts/css-steps-origin-clamping-model-v1/replay.py --output /private/tmp/steps-origin-review-UNUSED

External canonical source/olean and compiler dependencies are exact-pinned in IMPORT-PINS/INPUTS; this is not a self-contained clean-clone replay package.
