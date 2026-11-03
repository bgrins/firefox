# Root-font cancellation in installed Firefox 158

The unchanged 34-case diagnostic ran in installed Firefox 158 with a fresh temporary profile and no added feature preferences. All 68 samples were collected and all calibration controls passed. PRE.json and POST.json bind unchanged application metadata, executable and XUL bytes; this is release-browser evidence, not a build of the local branch.

After cancelling an animation of the root font size, a new rem-based animation on an existing child or root pseudo-element computes 64px instead of 46px. Both the immediate sample and the sample after animation readiness and two animation frames remain 64px. Reading the root computed style before creating the dependent animation produces 46px. A newly inserted child also produces 46px without that read. Corresponding rlh controls produce the expected 74px.

EXECUTED-FUNCTION.js is byte-identical to the archived original diagnostic. BROWSER-RAW.json preserves the complete connector response; REPORT.json decodes its returned JSON string. ASSESSMENT.json comes from the unchanged css-root-self-animation-order-probe-v1/assess.py. Other root-self cases are retained as separate observations and are not evidence that every mismatch has the same cause.

The normative cancellation oracle is traced in ../css-root-font-cancellation-synchronous-spec-trace-v1/TRACE.md. This run establishes release exposure and persistence across the diagnostic settling barrier. It does not establish the native cause or prove the behavior of a candidate build.

The server-owned browser was closed after evaluation. The connector was configured back to the installed Firefox, non-headless, about:blank, with no explicit profile; configuration does not launch a new browser. A process inspection found no remaining process using the task profile before cleanup.
