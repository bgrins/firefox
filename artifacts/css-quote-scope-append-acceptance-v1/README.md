# Contained quote append repair

The reviewed three-file patch is ready for a standalone native/WPT commit. The parent-list append fast path can leave retained contained-child quotes stale. Both fixed captures pass all 64 cases; removing the patch reproduces 12 calibrated failures. All 18 existing regressions are unchanged. Full builds, exact restoration, WPT lint and independent source/terminal reviews pass.

The Lean models corroborate conditional scope and delivery laws. This is a source-audit and browser-reproduced bug, not a proof-discovered defect or complete native correctness proof. No clean-upstream build or performance measurement is claimed.
