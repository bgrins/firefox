Fix 119 is accepted for the exact 4-path Gecko/WPT patch. Preserve nonfinite intermediate values while resolving relative lengths inside CSS calculations. Keep the existing final normalization policy for ordinary length conversion.

This fix is independently tested on normalized local HEAD90.

The isolated comparison repairs 6 failures and passes all 8 landing cases. The combined pair passes all19 new cases. Across1,037 subtests in13 files, both phases preserve every baseline PASS and exact retained failure; combined additionally preserves raw-only outcomes. The1,018 existing controls remain988PASS/30FAIL. All phase builds, WPT lint, original-stack rebuild, root preservation verification and independent terminal review pass.

The initial Sign proposal exposed a NaN regression during source/helper investigation. Browser comparisons then demonstrated six pre-existing failures in the separate intermediate-transport path. Conditional contextual-normalization models explain the distinction between intermediate and final normalization; 455 finite source-shaped helper cases at two optimization levels support the mapping. No universal native IEEE, provider or compiler refinement proof.

Working-stack installation and signed commits remain pending. Research and tooling belong in preceding commits; this patch contains only the listed Gecko files and regression WPT. The tested base is the local branch, not pristine upstream. No security impact or full CSS verification is claimed.
