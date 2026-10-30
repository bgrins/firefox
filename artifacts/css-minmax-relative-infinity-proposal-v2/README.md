Uninstalled min/max proposal preserving retained contextual infinities.

The guard defers replacement only when a child has an infinite unresolved coefficient and is structurally different from the selected winner. Keeping a structurally equal relative-infinity leaf preserves its future NaN when the basis becomes zero. Equality includes unit and value; percentage leaves also include their hint. Signed-zero equality cannot exempt an infinite coefficient. Explicit NaN early returns remain before this guard.

Compared with proposal v1, the additional equality condition preserves single-child and duplicate-only simplification. The CSS calculation simplification algorithm explicitly removes a single-child Min or Max node. The prior guard would retain it. Source review found this regression risk before native acceptance; it is a correction to our candidate, not a newly accepted Firefox bug.

SINGLETON-OBSERVATION.json records four System Firefox 158 probes: singleton and duplicate positive-infinity em min, and negative-infinity em max. All simplify to the corresponding calc expression and compute to zero at zero font size. That browser is not authenticated as the branch. New WPT preservation controls and a fresh exact-source broader comparison are required.

The earlier eighteen-case candidate pair tested proposal v1. It is historical evidence for the original defect and that candidate, not validation of this changed source. This proposal is not installed, built, browser-tested or accepted. The existing binary MinMax Lean model does not prove this n-ary structural-equality optimization. The independent source review supports it conditionally on equal leaves resolving in the same evaluation context; native compiler and browser validation remain necessary.

Specification: https://drafts.csswg.org/css-values-4/#calc-simplification, read 29 October 2026.
