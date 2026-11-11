# Reversible baseline/candidate wrapper

Prepared, not executed by the author. Python syntax was parsed without importing or running the wrapper. The parent owns execution and independent restoration verification.

From the repository root:

```sh
/Users/bgrins/venvs/firefox/bin/python -I artifacts/css-pseudo-animation-compose-extraction-20261110-v1/run.py baseline baseline1
/Users/bgrins/venvs/firefox/bin/python -I artifacts/css-pseudo-animation-compose-extraction-20261110-v1/run.py candidate candidate1 baseline1
```

Output names must be new single path components. Candidate mode requires a completed, successfully restored baseline receipt from these exact runtime inputs. A capsule-local lock prevents simultaneous invocations. Do not run another source-changing/build/browser diagnostic concurrently. The wrapper does not use Git to change index/history.

RUN-PLAN.json pins HEAD `4d1607b92c59814d3bd4e234fec8fb917dc3c735`, mozconfig hash and six test selections. SOURCE-ROLES.json pins original and formatted candidate bytes. Those originals match the extraction's earlier `7bc1ed9cde2a3f3f6e8c615125a7cf75c7964f16` copies. RUN-INPUTS.json binds both modes, helpers, copied fixtures, retained build receipt and patch. Changed inputs/HEAD fail before mutation.

The retained build receipt records the earlier build revision `90e0949346b54f6cd3ca02cbc22f72a63b41e9a8`; baseline is a retained-binary calibration, not a new clean build of current HEAD. All recorded executable/XUL/application.ini hashes must match before either mode. Candidate mode runs real `./mach build binaries -j6` through the Firefox Python environment, with a 2,400-second timeout and full unfiltered log. BUILD.json records result, source roles, configuration and resulting binary hashes; timeout/error also leaves process/failure receipts. Only the two native candidate files are written.

Both modes execute WPT headless with one process, STYLO_THREADS=1, and a 1,800-second timeout. Selections: copied 20-case retained-CSSOM controls; copied nine-case underlying controls; target.html; commitStyles.html; combining-effects and keyframe-effects directories. Copies use fresh temporary WPT paths with no metadata. HTML contents and expectations are unchanged. Broad CSS animation/transition suites are excluded from this first check.

The analyzer requires paired starts/ends, no duplicate callback keys, exact control names (20 and nine), 24 target callbacks, and participation of both directories and commitStyles. It retains all actual subtest/harness statuses, messages and expectation fields, including unexpected baseline failures. Comparison matches exact `(test, subtest-or-harness)` keys and actual statuses. Missing/new callbacks and changed statuses fail comparison. Messages are preserved but not compared because diagnostics may contain volatile data. Exit codes never establish equivalence. Differences are not waived or converted to metadata.

Before execution, each mode independently backs up the complete application and three extras: dist/bin/gtest/XUL, build/application.ini, and _tests/web-platform/wptrunner.local.ini. It requires 10 GiB free beyond backup size. After execution or failure, it restores sources, removes fixtures, and restores application/extras. Restoration steps are attempted independently. Verification covers bytes/modes/symlink targets, extras, source hashes, fixture removal, retained binary hashes, mozconfig, HEAD, index and tracked cleanliness. Backups are removed only after verified success. Build intermediates and caches outside application/extras are not claimed restored.

Owned process groups must be terminated before restoration. If they cannot be quiesced, restoration is deferred and backups retained for recovery. Concurrent edits are not silently overwritten. SIGTERM/KeyboardInterrupt are handled; SIGKILL, power failure and filesystem failures cannot guarantee automatic restoration. BEFORE.json/BACKUPS.json retain recovery information on restoration failure. These are limits, not claimed test results.

Current mozconfig has no active --enable-debug. PLAN/RESULT explicitly keep the debug gate outstanding. Passing this optimized comparison would support the extraction only; it would not fix bug 1615083 or complete debug/compositor/overflow validation in RUNTIME-GATE.md.

Copied candidate files were formatted using installed clang-format with repository style and real source paths as --assume-filename. The cpp output was identical; the header split one new parameter line. No unrelated churn. Formatted patch SHA256: `7e155ea1320673a0dd0f999cdc59ad4f85b77d5ee8b82c1d08b9b773198b0eee`.
