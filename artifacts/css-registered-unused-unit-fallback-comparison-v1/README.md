# Unused relative-unit fallback observation

Installed Firefox 158 and Chrome 156 both report two passing controls and one failing proposed expectation. A registered `<length>` using `var(--size, 1em)` resolves to its `0px` initial value even when `--size` selects `20px` or `30px`; `font-size` inherits `11px` or `17px`. Four samples per phase are stable. The missing-primary genuine-cycle case and direct literal control pass.

Both runs completed with all calibration checks passing, no feature overrides, and owned process/profile cleanup verified. This is shared behavior, not an interoperability difference. Independent review concludes INCONCLUSIVE: current substitution ordering favors the proposed expectation, but the registration specification does not explicitly locate its unit-edge scan. The new Lean model proves consequences of both interpretations without choosing between them. No native fix is claimed.
