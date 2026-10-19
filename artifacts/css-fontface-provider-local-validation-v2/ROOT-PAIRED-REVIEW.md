# Loaded FontFace candidate v2: local paired evidence

The exact 16-file candidate built successfully on macOS (terminal session 72558, exit 0). The build log, pre-build pins and actual terminal attestation are retained. Both browser suites authenticate their unchanged pre/post inputs and binary hashes.

The fixed 68-case matrix has 68 PASS and three OK harnesses: 38 baseline failures become PASS, and the other 33 status/expected tuples are unchanged. The eight regression harnesses contain 19 PASS subtests, four PASS test endings, three OK endings and one unchanged expected FAIL reftest. The style/family-swap subtest improves from FAIL to PASS; all other 26 tuples are unchanged. Regression process exit 1 is its unexpected PASS against old expected-FAIL metadata.

Native lint emitted no diagnostics. WPT lint identified missing canvas spec metadata and a false Ahem-system-font match in the HTML ternary expression. The v3 artifact fixes metadata/whitespace only, preserving exact case names; final installed bytes and expectation cleanup still need their own run.

Independent source review found no concrete new loaded-provider blocker. It does not establish all-platform compilation, shutdown scheduling, local-font resource immutability or full native lifetime correctness. Legacy nonloaded wrapper mutation remains unchanged. This evidence belongs to the known bug 1072149 family and is not a Lean-discovered native fix.

The shared tree includes the earlier worker-removal repair. Before calling this repair independently landable, determine whether the native change or final WPT controls require that prerequisite, and validate the resulting dependency claim. No standalone native repair is accepted by this checkpoint.
