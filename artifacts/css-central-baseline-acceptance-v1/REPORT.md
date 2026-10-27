# Fix111: central baseline synthesis origin

Accepted for an independent Gecko+WPT commit. Empty vertical inline-blocks with asymmetric margins can move20px when selecting First versus Last because central synthesis returns a scalar from the wrong origin. Use the already line-inversion-adjusted sharing group to encode the existing rounded midpoint correctly.

The standalone patch changes only Baseline.cpp and adds the exact tested twelve-case physical-center WPT. Clean HEAD has8 PASS/4 FAIL in that fixture; the correction passes12/12. All204 existing subtests retain their outcomes, including four known expected failures, and the reference test passes. Scoped WPT lint, all builds, restoration and independent raw-result review pass. The patch passes a read-only applicability check against the current native tree, whose Baseline.cpp equals the pinned HEAD body.

Independent replay passes26 focused Lean declarations. Reviewed constructor/caller evidence closes the concrete exceptional negative-margin concern for well-formed shipped layout with nonnegative dimensions and defined prior arithmetic. This is conditional arithmetic plus manual source correspondence, not an arbitrary-int32 API proof or whole-CSS/native verification. The retained integer counterexample and limits remain documented; no clamp or legacy-origin fallback is substituted.

Research belongs in preceding commits. The native/WPT commit is pending the configured signing flow, and the correction is not installed in the restored mixed working tree. The adjacent alphabetic/hanging margin-side issue is separate and excluded from this patch. No security impact is established. Nothing was pushed.
