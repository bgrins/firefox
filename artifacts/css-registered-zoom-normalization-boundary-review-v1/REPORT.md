# Registered zoom normalization boundary review

Source-only review of the pinned isolated six-file proposal. No live source, browser, build, epoch or Git mutation. The proposal remains incomplete for container units and is not accepted.

## Concrete finding corrected by author

QueryStyleRange::resolve_value originally scoped only the Length operand. Float(Number), Angle, Time, Resolution and Percentage can also contain contextual length leaves in admitted math. Their stored registered counterpart enters Value::to_computed_value scope, but the query literal did not. The author has now scoped all six direct numeric conversions in the pinned candidate.

With an 809 CSS-pixel viewport, effective zoom 2 and <number> calc(0.1vw / 1px), the scoped value is approximately 0.8. The old unscoped query operand is approximately 0.808333 because viewport resolution truncates app units before the ratio cancels zoom. FINITE-PRECISION.json emulates source f32 inputs/output and f64 truncation. It is not an executed CSS test or normative conclusion.

## Producer and consumer audit

The explicit outer Value ToComputedValue wrapper covers ordinary parsing, prepared admitted values, computed registration initials and parsed custom animation inputs that enter that trait. Inner component/list derives preserve the scope through numeric wrappers, transform lengths and image geometry. Computed clones, inherited/CSS-wide copies and custom animated values must remain canonical copies; they must not undergo another divide. Context-free parsed absolute shortcuts already contain canonical lengths. This is a manually traced boundary argument, not exhaustive Rust refinement.

Actual CalcNumeric::resolve maps length leaves through NoCalcLength::to_computed_value_for_math, so number ratios, signs, inverses and typed scalar math reach the edited boundary. LengthPercentage calc maps through that same method; its ordinary registered computation uses identity text-zoom closure. Numeric matrix entries remain numbers and are intentionally not length-scaled. Relative-font helpers preserve font/line-height/metrics reads and invalidation flags before unzooming the result. Non-root rem/root-metric paths explicitly multiply by current effective zoom, so the added divide cancels that scale; current-font and line-height cases rely on existing scheduling readiness, which this patch does not prove or expand.

CSSPixelLength and LengthPercentage custom-property resolution retain canonical lengths while other ToResolvedValue effects, including color resolution, remain active. Query literal conversion must use the same canonical mode, including all scalar math arms. The RAII scope restores the previous flag even for nesting/unwinding; constructors initialize it false.

## Container boundary remains an explicit blocker

Captured ContainerSizeQueryResult stores width and height independently, and lookup may merge them from different ancestors. It presently carries no coordinate/zoom provenance. The candidate intentionally leaves container conversion unchanged while changing custom CSSOM interpretation globally. Thus canonical storage is not established for container-bearing lengths, ratios, transforms or images, and this is not a complete repair.

Do not attach one target effective zoom or one shared container zoom to this aggregate. If measurements establish that conversion requires source-container scaling, preserve the selected source separately for each physical axis before merge; viewport fallback has its own coordinate convention. Source-ancestor normalization can avoid introducing a new target Zoom dependency. Dividing by target effective zoom instead would require settled target zoom and could introduce a new self-cycle for zoom:var(--n) with --n using cqw-derived math. Current source does not justify that dependency or cycle policy. Confirm raw-frame coordinate semantics against the controlled observer and existing bug 1894104 before choosing the formula.

## Remaining scope

No further concrete missing producer was established in this bounded review. Animation/typed-attribute paths, fractional zoom, font metric units, nested image/transform math and mutation invalidation still need native tests; their absence is not evidence of correctness. No canonical Lean coverage or accepted bug count changes.

## Unexecuted focused WPT draft

registered-numeric-style-range-zoom.html adds eight draft tests: number, angle, time and resolution, each direct and selected substitution. Each captures zoom 1, 2, 0.5, 1 before assertions. The factor is derived from innerWidth to place the viewport leaf at 48.75 app units, away from rounding boundaries, without resizing the browser. Overflow is hidden to avoid scrollbar viewport ambiguity. An independently computed initial-value element calibrates grammar admission; an unregistered number range calibrates range support; a deliberately false range controls matching. The main oracle compares identical admitted expressions, without requiring exact numeric serialization. Percentage hints and integer rounding are intentionally outside this narrow equality fixture. No callbacks or browser tests have run. The draft needs actual grammar/viewport calibration before inclusion in an acceptance suite.
