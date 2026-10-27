# Consolidated offset and scroll comparison

All 32 new precision tests pass. The fresh baseline has 53 PASS and eight precision FAIL across 61 cases; its 29 scroll/zoom/overflow controls all pass. Adding the authenticated historical 80 controls gives 129 PASS and 12 FAIL. The candidate has 137 PASS and four unchanged metadata-expected FAIL across 141 cases: exactly eight repairs, no PASS regressions and no changed retained-failure diagnostics.

Both comparison builds, WPT lint, candidate WPT and restoration build succeed. The baseline WPT exits one for its eight expected-for-this-experiment regressions. Reused controls retain full provenance to the original raw log and independent reanalysis; the original parser-order failure is preserved. Native roles are HEAD90 with the native portions of fixes 102/103 reversed, then only the consolidated Element.cpp conversion added. This is not a clean-upstream or release-browser comparison.

Root independently checked all 30 restored source bodies, 47 guards, 318 final source/resource/binary pins, existing tests, HEAD, the unchanged 925-path stage/full index and original native diff. The owned WPT and native source temporaries are absent. Both WPT process groups were cleaned up. Build logs preserve existing progress-monitor exceptions/warnings alongside successful completion.

This passing experiment supports one shared integer-conversion defect in offsetLeft/Top/Width/Height and scrollWidth/Height. Scoped acceptance remains a separate root decision after independent terminal review and packaging. Earlier geometry/unzoom and broader CSS fractional policy are outside the arithmetic proof.
