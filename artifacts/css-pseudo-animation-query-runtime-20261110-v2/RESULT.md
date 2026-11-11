# Query-driver v2 build result

The baseline preserved all 130 expected WPT records and restored successfully. The candidate passed installed WPT lint, ESLint and test-manifest lint, then failed native compilation with six diagnostics at four unqualified Animation references in the temporary nsDOMWindowUtils driver. Both mozilla::dom::Animation and mozilla::layers::Animation are visible there. Build exit was 2; the runner exited 1 and performed verified restoration. No candidate WPT or direct-driver execution occurred.

The build also exposed an unused pending-state snapshot in Animation.cpp: after the helper refactor its only remaining use is in MOZ_ASSERT. The next revision will preserve the snapshot and mark it maybe_unused while qualifying the four driver types. It will retain all 208 assertions and the corrected preference setup. The frozen v2 inputs and complete failure logs remain unchanged.

This is a development build failure in the proposed helper/driver, not a newly observed Firefox defect. Independent full restoration review follows separately.
