This diagnostic successor binds WPT capsule-v4 and the two-path native admission proposal v3. The report.js, report.html, CASES.json and validator are byte-identical to observation-v1. It requires a completed, preserved matching candidate WPT phase and the same candidate epoch, sources, normal binaries and application metadata.

Only the exact saved original-v1 RESULT identified in ADOPTED-ORIGINAL.json may cross the capsule boundary. Adoption authenticates the old manifest, all14 saved runtime files, unchanged observer payload/validator and original semantic policy; binds original sources, HEAD, epoch, binaries, application metadata and cleanup; invokes capsule-v4's narrow adoption of the exact original WPT experiment; and recomputes the summary from RAW.json. Other old results, capsules, changed fixtures or validation rules are rejected. The original remains original-1 under its v1 manifest. Candidate output adds ORIGINAL-ADOPTION.json and original_adoption without relabeling history, and repeats adoption checks after execution.

Results remain observations. Comparison reports every changed case; it does not require equality or classify a spec violation. The browser uses a fresh default profile; WPT preferences are not imported. Owned loopback server, isolated profile/process group, cleanup and full pre/post preservation are retained. All actual values and registration errors remain data.

Frozen HEAD is e2839ec561c1e19de963bd0d56f46f4c067685d0. If research signing advances HEAD, this package cannot run without an explicitly reviewed immutable successor/rebinding. No browser or native execution occurred during preparation.

Invocation:

    python3 -I -S -B artifacts/css-registered-admission-zoom-observation-v2/run.py MANIFEST_SHA candidate-1 ABSOLUTE_CURRENT_EPOCH EPOCH_SHA ABSOLUTE_CANDIDATE_WPT_ASSESSMENT WPT_SHA ABSENT_OUTPUT ABSOLUTE_ORIGINAL_RESULT ORIGINAL_SHA

Use the exact original result and digest in ADOPTED-ORIGINAL.json. The candidate output must be a fresh absent artifacts/css-registered-admission-zoom-runtime-candidate-N directory. Candidate WPT assessment must belong to sealed capsule-v4, with matching sources/epoch. Native acceptance is never implied by diagnostic completion.
