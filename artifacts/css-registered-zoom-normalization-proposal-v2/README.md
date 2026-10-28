# Registered-value normalization experiment with container provenance

This seven-file experimental proposal extends the six-file predecessor with per-axis container zoom provenance. It is not an accepted fix. Source roles, exact patch transport and Rust formatting checks are recorded alongside the patch.

The container lookup stores each axis's raw app-unit dimension together with the effective zoom of the container that supplied it. Registered-value computation divides that dimension by its source zoom in double precision. Missing axes retain the small-viewport fallback without target-zoom division. Merging keeps each dimension and its own zoom together. The ordinary path converts raw app units to f64 CSS pixels before the same factor arithmetic as previously; its known zoom behavior is not repaired by this experiment.

The source-container interpretation is an explicit inference from the specification chain, not a settled numerical oracle. The coordinate review records that limit and the observations supporting an experiment. The separate logical-unit scheduling discrepancy remains unresolved: a registered cqi/cqb value can choose axes using inherited writing mode before the element's own writing mode is ready. This patch does not claim to fix that defect.

The remaining six files scope registered computation, normalize absolute/font/viewport length leaves, preserve canonical custom-property CSSOM lengths, and apply the same scope to all six numeric style-range operand types. The predecessor documents the representation rationale and current baseline of 50 failures and six passes in the 56-test zoom calibration. The matrix and style-range passes must be preserved.

Next compile this candidate, repeat the full calibration and container observations, then address any remaining regressions and the separate writing-mode readiness case. Admission/scheduling/regression/sign comparisons, animation and recascade checks, final WPT lint and an independently landable native-plus-WPT split remain required before accepting a fix. No new formal-coverage or accepted-fix credit is claimed.
