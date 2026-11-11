# Independent terminal review

The completed optimized experiment is valid, with three failed interpretation probes. It is not an all-pass test or public CSSOM repair acceptance. The live hold is released after independent restoration checks.

The frozen 81-input manifest is `311ac44a991a9f250240a0b65a17c6ac79d924fea28f71b5aad07a7e29679858`, at execution HEAD `449da6d3112d164287e6a76de66c45344e4cc2a7`. Every input hash was authenticated. Build/source/config/sample-binary receipts agree; the actual `mach build binaries -j6` exited zero after approximately 671 seconds. Five lint commands succeeded. This is independent result/restoration review, not independent authorship of every earlier helper.

## Observations

- Baseline and candidate WPT records are identical, including messages and expected classifications: 99 PASS, 19 FAIL, 12 harness OK. The 19 failures were retained, not waived or converted into new defects.
- Query driver: all 208 assertions and 13 tasks pass, including setup gates. Recascade driver: all 100 assertions and six tasks pass.
- Composed driver: all 122 assertions occur in exact order inside five complete task scopes. All 119 hard checks pass, including 33 setup checks. The three explicitly named interpretation probes fail. The normal aggregate ends `FAIL`, `Finished in 29ms`; the command exits 1. The enclosing wrapper exits zero because this exact, complete probe-only result is a valid investigation.
- In the current-before/no-fill case, the animation map contains `50px`, transition map is null, and returned style is `30px`. These are the source-predicted observations, not proof that a normative rule is violated. Active overlap, additive overlap, transition-only importance, and fixed/implicit/additive composition controls pass.

`replay.py` reproduces each saved parser/comparison result. Separate review scripts reconstruct raw WPT, query/recascade and composed records without relying only on saved booleans. `COMPOSED.json` retains the three exact messages and classification counts.

## Restoration

`AUDIT.json` independently verifies 9,378 application entries and 42,811 installed Mochitest-tree entries by semantic file/link/mode identity; six extras; all 14 source roles; test/config and retained-build source/binary hashes; execution HEAD and index; clean tracked/staged diffs; and the original 527 unrelated untracked path identities. This does not claim content hashes for every unrelated untracked file. Temporary fixtures, backups and lock are absent. Both transaction receipts agree with the independently scanned live state. All 12 owned process groups are absent in the separate process-table snapshot; unrelated browser processes were preserved.

## Log limitations

`LOG-SCAN.json` retains warning/error/exception/crash-word occurrences from all full command logs. Inspection found four nonfatal build-monitor `KeyError: export` tracebacks, compiler/deprecation warnings including SWGL floating-point options, and successful final linking. WPT and Mochitest output includes SWGL framebuffer crash annotations and Nimbus EmptyDatabaseError console messages; there is no structured crash or missing callback. The candidate WPT also logs a `testcommon.js` `handleFrame` script-termination timeout while closing a previous window. It does not produce a timeout harness result or any callback/message difference, but this run is not described as warning-free. Mochitest reports an already-running unrelated `/Applications/Firefox.app` process, Node deprecation warnings, shutdown channel errors after completed tests, and disabled refcount leak logging. No leak-clean or debug assertion claim follows. The composed Error Summary contains only the three recorded probes and their aggregate failure.

## Boundary

This supports the bounded optimized composition-to-transient-style experiment with stable providers. Missing-pseudo public CSSOM integration, general dependency/provider coherence, visited-style behavior beyond the prior source contract, and final debug/transform-hint checks remain open. Probe policy ambiguity is preserved; no new bug count or native repair acceptance is asserted.
