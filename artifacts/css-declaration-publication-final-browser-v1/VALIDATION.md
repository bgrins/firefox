# Declaration publication repair: paired browser check

The final six-test run contains 147 unique `(action, test, subtest)` outcomes. Baseline: 128 PASS, 13 FAIL, 6 harness OK. Candidate: 140 PASS, 1 FAIL, 6 harness OK. Exactly twelve publication cases change from FAIL to PASS; the other 135 outcomes are unchanged. All 49 new subtests pass. The retained failure is the existing metadata-expected `param(ident("--a"), orange)` computed-style case. Candidate harness exit is zero.

`PAIR-CHECK.json` compares full normalized rows by identity. Each phase checks recorded source/config/test/binary pins before and after execution. The only changed fixed pin is properties/mod.rs; the binary hashes change after the explicit Rust library rebuild and binaries link. Both build commands exit zero. The binaries-link log retains four build-monitor `KeyError: export` tracebacks; the XUL link completes and the resulting binary passes the candidate run. No warning-free build claim is made. WPT lint reports zero problems. The build is the shared macOS checkout containing earlier local work; this is not isolated upstream runtime evidence.

The directory metadata enables link-parameters. Both normal and important priority now maintain one declaration after setting and no declaration after removing. The captured removal snapshot covers length, item(0), cssText, property value, and priority. Existing-property updates, cssText, empty/none and invalid-input controls remain unchanged.

The two-file patch applies and reverses on upstream base as recorded separately in css-declaration-publication-root-v1/PATCH-CHECK.json. The unchanged pre-existing whole-file Rust formatting discrepancy is recorded in FORMAT-CHECK.json; the changed line is stable under rustfmt.
