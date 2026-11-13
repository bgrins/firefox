# Baseline padding reflow observations

The existing local browser reproduces history-dependent layout for six of 32 variants. In contain:layout size and contain:strict, first-baseline alignment against the large-font peer moves content down by18px per child text edit; reported content height decreases from100 to82,64,46,28px. Replacing the grid with an equivalent fresh copy restores original geometry. Last-baseline variants also drift. Other26 variants are stable. Every initial/fresh pair matches exactly.

The192 observations cover eight containment/overflow modes, first/last baseline alignment and two peer font sizes. X/XX edits preserve line height. The193 WPT subtests only check observation collection, not normative correctness. ANALYSIS.json records differences. This supports the source-derived PresShell padding feedback hypothesis but does not directly trace frame/property writes.

CSS Alignment baseline content alignment describes effective padding adjustment: https://drafts.csswg.org/css-align-3/#baseline-align-content . Equal final DOM/style/font inputs should not acquire cumulative adjustment from prior reflows. Existing WPT css/css-grid/alignment/grid-baseline-align-001.html covers initial alignment; this probe adds incremental histories.

Run38292 ended7ef114 exit0. Restored browser hashes match before/after, owned groups are absent and temporary WPT removed. No native source/build changed. Browser connector was unavailable; local headless WPT supplied observations. Standalone repair and normative regression remain next; no fix accepted here.
