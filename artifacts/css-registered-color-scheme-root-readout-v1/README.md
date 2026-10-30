# Registered identifier and color-scheme regression

Installed Firefox 158 reproduces a correctness failure in two reduced cases. A registered custom property selects `light` or `dark` from a union containing `<custom-ident>` and `<color>`. Adding an unused `attr()` fallback to the consuming `var()` makes both the custom property and `color-scheme` compute to the registered initial value, `normal`. The same cases pass in portable Chrome 156.

| Case | Firefox | Chrome |
|---|---|---|
| Union, plain var() | light → dark; PASS | light → dark; PASS |
| Union, unused attr() fallback | normal → normal; FAIL | light → dark; PASS |
| Reversed union, unused attr() fallback | normal → normal; FAIL | light → dark; PASS |
| Identifier-only registration, unused attr() fallback | light → dark; PASS | light → dark; PASS |
| Literal color-scheme control | light → dark; PASS | light → dark; PASS |

Each cell describes both the first computed color-scheme and subsequently read computed custom value. These are sequential observations, not an internal-state snapshot. Firefox has 3 PASS / 2 FAIL; Chrome has 5 PASS. Both harnesses finish normally. Registration and literal calibrations pass in both engines. No feature preferences were overridden.

The expected identifiers follow the first matching registration clause and ordinary valid var() substitution. The source-supported cause is an overly broad ColorScheme dependency derived from the registration's possible color type. The unused attr() fallback matters because it admits this longhand into the existing dependency traversal. Native before/after evidence is still needed to confirm that cause and validate a repair.

This is one observed bug candidate with two reproducing tests, not two accepted fixes. Accepted local fixes remain 149. A standalone native repair and WPT commit are pending; the broader contextual attr/animation prototype is not a prerequisite unless a concrete implementation dependency establishes otherwise.

Discovery was source/spec review while extending dependency verification; confirmation was browser execution. This specific native defect has not been proved in Lean. The separate ancestry and SCC models remain bounded design evidence.

Root independently checked report/raw-request agreement, derived reporter and assertion results, exact served fixture/harness/report bytes, application pins and process/profile cleanup. Both runtime manifests are frozen. Cleanup initially recorded a process-group permission error, then successfully reaped the owned process and checked group absence; the original receipt is preserved. Root's independent process census also confirms absence.

[Exact tentative WPT and spec/source trace](../css-registered-color-scheme-dependency-review-v1/README.md) · [Firefox evidence](../css-registered-color-scheme-firefox-runtime-1/ROOT-REVIEW.json) · [Chrome evidence](../css-registered-color-scheme-chrome-runtime-1/ROOT-REVIEW.json).
