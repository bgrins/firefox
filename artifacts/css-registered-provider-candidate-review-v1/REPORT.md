# Provider candidate: hold acceptance

Independent saved-evidence check 047d15/0 confirms 775 matching raw assertion identities: 20 FAIL→PASS, four FAIL→FAIL with changed full messages, and 751 unchanged signatures. The comparison includes message and expected/intermittent field presence. Candidate totals are 699 PASS / 76 FAIL. All 30 harness endings and six passing reftest statuses match baseline.

The four changed failures are the conditional @property initial-color cases. During the dark snapshot, the selected provider value and consuming color change from blue in the baseline to red in the candidate. The direct color control stays blue; the undeclared registered initial calibration stays red in both runs. All three light→dark→light snapshots were decoded directly from raw event messages, independently of the generated COMPARISON.json.

This is a real observable change, but the CSS-rule registration-admission oracle remains conditional because the current @property policy text is unresolved. Do not describe it as four newly proven standards violations. Equally, do not accept the candidate on the strength of 20 repaired assertions or unchanged FAIL statuses: the broad cached-default change has unadjudicated behavior beyond the intended readiness repair. Preserve the snapshots and either resolve the policy/representation boundary or preserve the established behavior before acceptance.

A status-only comparison would miss all four color changes. The raw full-message comparison detects them despite identical expected status and the same final assertion failure text. RESULT.json truthfully retains complete_comparison:false/comparison_gate_passed:false from the observation runner; the later offline COMPARISON.json is separate evidence, not a retroactive successful execution gate.

Both runtime inventories authenticated. Saved PRE and POST are equal; application metadata pre/post match; saved cleanup reports owned group absent and temporary root removed; assessments are complete/preserved without infrastructure errors. The candidate outer wrapper exited0 (72723/3024cf), while WPT exited1 as expected for the retained assertion failures. Exact saved epoch/source joins show only custom_properties.rs and cascade.rs changed among the nine inspected native paths; accepted zoom7 is preserved. No live preservation check or browser was rerun by this reviewer.

No acceptance increment, no native patch, no fixture or runtime mutation. CHECK.json records the extracted snapshots; REFERENCES.json pins all inspected evidence.
