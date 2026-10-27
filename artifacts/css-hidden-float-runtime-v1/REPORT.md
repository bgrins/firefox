# Float owner comparison results

The normalized baseline passed 91 of 95 cases; the float candidate passed all 95. Four direct/inline-nested hidden float root/leaf queries changed from stale width 50 to expected width 25. All 79 existing controls and ten visible float controls passed both phases. The two nested-block hidden cases already passed the baseline. This comparison alone does not attribute that result to the prior block repair.

Both comparison builds and the restoration build succeeded. Root authenticated the prepared inputs, all 29 live source guards, unchanged HEAD and 925 staged research payloads, nine preserved WPT files, historical resources and absence of owned temporary tests. Before, final and live snapshots match. The build log retains a Mach resource-monitor KeyError despite successful build exit; it did not prevent restoration or the successful-build report.

This is evidence for a candidate repair, not native acceptance or a new committed fix. Independence from the accepted block repair, final standalone WPT selection, pushed/overflow/continuation ownership and cost remain open. The finite Lean model establishes conditional ownership/readiness properties; it does not verify the whole native engine.
