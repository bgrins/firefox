# Steps origin and consumer range

This is a transfer of the reviewed `css-steps-origin-clamping-model-v1`, not new theorem discovery. The original ten statements/proofs and eleven positive examples are retained under a canonical namespace. Three false claims become expected-false executable observations under the existing exact-output checker; focused replay also preserves the original same-claim kernel rejection controls. No checker rejection gate is relaxed.

| Specification rule | Supplied model boundary |
| --- | --- |
| [CSS Easing 1 step functions](https://drafts.csswg.org/css-easing-1/#step-easing-functions): jump-none requires more than one step | `minimum .jumpNone = 2`; other supplied positions use one |
| [Values 4 numeric ranges](https://drafts.csswg.org/css-values-4/#numeric-ranges): prose ranges are numeric constraints too | Conditional minimum is the final consumer range |
| [Values 4 numeric functions](https://drafts.csswg.org/css-values-4/#numeric-function): computed out-of-range results clamp rather than invalidate | `Specified.calculation` remains distinct from `.literal`; `repaired` clamps only resolved calculations |
| [Top-level calculation](https://drafts.csswg.org/css-values-4/#top-level-calculation) and [range checking](https://drafts.csswg.org/css-values-4/#calc-range) | Existing `CssNumericCensorship.complete` and `CssIntegerRounding.round` supply a normalized integer; NaN and zero are equivalent at that boundary |

The authoritative manual trace is `css-steps-nan-oracle-trace-v2` (superseding the earlier inconclusive trace). No fresh web-spec translation or automated translation proof is claimed here. `calculation upper value` first uses the existing positive-integer normalization range [1,upper]; the consumer then applies minimum two. This is a conditional model of the repaired implementation pipeline, not a claim that an intermediate range of one is mandated by CSS. Its repaired NaN result is two. Ordinary-position equivalence explicitly requires normalized positivity. The upper bound theorem requires both the normalized result and the consumer minimum to fit the supplied bound.

`Option.none` represents unavailable context-free resolution; rejecting it preserves the modeled parser admission domain, not a normative requirement to reject every contextual CSS expression. Actual CSS token parsing, literal/calculation tagging, calc tree resolution, binary32/binary64 operations, saturation to signed32, and source/compiler correspondence remain obligations. The abstract exceptional-value model does not prove native IEEE execution. Serialization, WAAPI update atomicity, timing interpolation, DOM/provider lifecycle and browser behavior are outside these theorems.

Versioned native mapping is fix 133's reviewed `css-steps-jump-none-repair-v2` easing change: retain Inline literal validation, admit resolved calculated jump-none counts and clamp in shared computation. Browser discovery/acceptance and later metadata corrections are separate evidence, not Lean-discovered bugs. No whole-CSS coverage increment or quantitative coverage credit is recorded; coverage.json is unchanged.
