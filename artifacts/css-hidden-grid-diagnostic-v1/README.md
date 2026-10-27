# Own-hidden Grid diagnostic

Source-only proposal, not browser-calibrated. Eight independent fixtures: visible/hidden grid × direct item/leaf-first × bounding/offset size. Each records five stages (40 total) without stopping on target mismatches. Root owns execution; window.gridDiagnosticPromise resolves to the raw result. A loopback capture wrapper may await that promise.

The visible parent is an ordinary block. The grid itself is the sole hidden element. Fixed explicit row and minmax(0,1fr) column avoid an auto-min/intrinsic-track oracle. Item fills 200px then120px; leaf is50%, hence100px then60px. Heights32/16px are fixed. The parent-width mutation changes no descendant style. Only the visible parent is queried before the selected target; leaf fixtures never query the grid item first. Each fixture begins with visible calibration, hides/queries once, changes width, queries/repeats, and shows/restores. No flex, absolute positioning, table provider, text/font, transform or fragmentation dependency.

A hidden mismatch with passing visible/outer calibrations is evidence to investigate, not a confirmed missing-mark cause. Geometry does not prove exact dirty flags or which native sizing branches execute. Existing Grid intrinsic measuring protection, resize propagation, and forced-query history can mask the suspected normal own-content skip. Offset dimensions and bounding dimensions are independent query APIs but deliberately omit position; this is not comprehensive geometry coverage.

Source lead: css-hidden-grid-followup-v1 FILES8d3ef797b882037f39f40e190dede6b5ff57a3f0675aa688696114f0dbbb1006. No native patch is proposed. Current campaign must finish before a separate runtime is scheduled.
