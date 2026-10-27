# Accepted fix 130: initialize ordinary keyframe attributes

Accept the two-Rust-file/one-WPT patch for initial ordinary keyframe attr() resolution. The keyframe builder now prepares ordinary variable-bearing declarations and their qualified attribute values; final evaluation uses the real element provider. Existing registered-custom-property handling and shared substitution/taint semantics remain intact.

The 116-case comparison changes95PASS/21FAIL to113PASS/3FAIL and reproduces every original outcome after restoration. It repairs16 of24 landing cases and two additional distinct-URL provenance cases. All28 mandatory cases pass; all84 prior/existing controls retain exact outcomes, including70 passing checks for prior fixes. Both native builds, root preservation verification, independent terminal review and targeted WPT lint pass. One attr(var()) context diagnostic progresses to a known context mismatch without repair credit.

The standalone gecko-wpt.patch contains only two Rust files and one corrected24-case WPT. It applies and reverses unchanged on HEAD90; no uncommitted native prerequisite was identified. The exact patch uses the evaluator structure introduced by committed fix70, already an ancestor of HEAD90. No research/tooling belongs in its native commit. Clean-HEAD90 compilation/browser behavior has not been separately measured.

The Lean model supports conditional preparation/provider/taint reasoning; it does not prove the Rust implementation, computed-context selection or dependency scheduler. Source inspection and the browser comparison establish the concrete bug and repair. Initial lookup is the accepted scope: later attribute mutation, inactive reuse and general animated custom contexts remain separate work.

Distinct inert URLs show the original failure selects the CSS-authored literal fallback, not the attribute URL. This is not evidence of exfiltration or universal taint correctness. Triage is tentatively P3 visual/conformance correctness; stock-release and performance effects are unmeasured.

The measured candidate was restored. Installation and signed commits remain pending. Each build contained four disclosed nonfatal Mach export logging KeyErrors; both builds completed successfully. Raw index bytes stayed unchanged during this comparison; older historical discontinuities remain qualified.
