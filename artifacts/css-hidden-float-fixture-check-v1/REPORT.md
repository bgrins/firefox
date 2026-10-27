# Float fixture diagnostic

The build-free diagnostic completed successfully as a diagnostic: 16 subtests, 10 PASS and 6 FAIL, with two OK harness endings. The WPT process exited 1 because of the six retained assertion failures; the enclosing diagnostic exited 0. WPT lint exited 0.

| Family | PASS | FAIL |
| --- | ---: | ---: |
| Main visible controls | 6 | 0 |
| Main hidden queries | 0 | 6 |
| Separate visible float-push calibration | 4 | 0 |

All six failures occur at `change: first selected query`: expected width 25px, observed stale width 50px. They cover the root and leaf for direct floats, inline-nested placeholders, and nested ordinary-block owners. Positions and reported heights match the expected arrays. Before these assertions, each test checks every outer-only flush and fresh visible peer, plus the initial and shown target calibration. Thus these are hidden-query mismatches, not visible calibration failures.

The four separate multicol calibration cases pass, including the prefilled/tall case. This establishes their tested geometry, not execution of a native pushed-float bit or a particular continuation branch. Raw WPT retains the first failed assertion per subtest; it does not serialize the complete `window.floatOwnerQueryResults` arrays. Later repeated-query assertions in failed tests are not established by the failure receipt.

## Independent recount and integrity checks

Reconstructed the exact 16-name roster and two harness endings from the line-delimited raw log, and matched them byte-for-value to `fixtures/RUN.json`. Recomputed counts and checked all six failure messages and `CLASSIFICATION.json`. Authenticated all nine original inputs against INPUT-FILES SHA `7355dc5a698a86581a31116ade1be130b710f5e9b9c04c809c4e38d96bb14f0c`.

Verified BEFORE equals FINAL and the preceding boundary-v2 FINAL. The preceding STATE/FINAL hashes match INPUTS, and that campaign records successful restoration/build with no recovery errors. All 28 native source snapshots, 12 resource/metadata entries (including absent metadata), and two binary pins agree with the WPT before/after maps. Retained source/resource copies match their hashes. Native HEAD, index and native-diff receipt identities are unchanged; the HEAD recorded is `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`.

STATE records terminal, restored true, no failure and no cleanup errors. The driver installs/removes only the two temporary tests, writes no native source and runs no build. Both temporary paths were also absent at review time. These cleanup checks concern this driver's temporary files and state restoration; they are not additional process-group tracing.

## Scope

This is the restored working binary containing preserved native prototypes, not an isolated HEAD build or a float-candidate experiment. No float native patch was installed, and no new native acceptance follows. The nested-owner case may require skipped-line readiness as well as owner-list marking; this diagnostic does not determine that dependency. A later isolated baseline/candidate experiment must bind the selected source variants and establish repair/preservation separately.

Only this report and the final FILES manifest were added during the recount. No browser, compiler, build, native or Git operation was performed by the reviewer.
