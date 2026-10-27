# Immediate font mutation follow-up (unrun)

This six-case artifact tests the same conversion-readiness defect family on a style-dependent basis. It does not change the frozen nine-case viewport WPT or active comparison, and is not a new accepted bug.

Searchfox discovery `--define SVGContentUtils::GetFontSize` was checked against explicit HEAD90. SVGLength's em factor calls SVGElementMetrics::GetEmLength, then SVGContentUtils::GetFontSize. With an existing primary frame, the latter reads the frame's current Style(); its other path calls GetComputedStyleNoFlush. No synchronous style update is supplied by that function. DOMSVGLength::ConvertToSpecifiedUnits currently lacks the flush present in GetValue. The proposed repair flushes style if either source or destination is font-relative.

Warm an attached scalar x or text-list x with font-size20px, mutate inherited font-size to40px, and convert before any style/geometry read. A stale destination factor would store2em from40px instead of1em; a stale source factor would store40px from2em instead of80px. A later style flush would leave those stored errors persistent. Two GetValue controls should report80px. These are source predictions, not observed results. Existing font-change controls change the font after conversion or flush before conversion and therefore do not establish this history.

The probe copies first/repeat/unit before calibration reads, verifies an independently preflushed reference and fixed400×100 viewport, then checks the captured result and post-flush resolution. Em uses the computed font size directly, so no particular glyph or font loading metrics are required. The class changes inherited style on a fixed-size SVG; no percentage basis, hidden content, viewBox, transform or zoom is involved. Failure of font/viewport/reference calibration must not be classified as conversion evidence. The getter control itself intentionally supplies readiness.

The previously pinned SVG2 SVGLength conversion algorithm reads the current value and current computed font-size basis; the existing14-theorem rational model applies to supplied current factors20→40, with the same native/provider/IEEE limits. This follow-up adds no theorem or coverage credit. Only JavaScript syntax was checked; no browser, lint, native source or index operation ran.

The v1 draft omitted an explicit body before synchronous tests. This successor adds `<body>` so fixture construction has a valid parent; v1 is retained and must not run. JavaScript is unchanged.
