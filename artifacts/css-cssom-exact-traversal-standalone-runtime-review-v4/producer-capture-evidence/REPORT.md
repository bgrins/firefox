# Standalone traversal v4 without fix 102

**STANDALONE_WITHOUT_102_FINITE_GATE_PASS.** This is producer evidence for the requested finite independence check, not an independent review or native acceptance.

After root reported experiment 89714 terminal with exit 0, this artifact captured all 115 runtime files read-only and verified stable hashes during copying. Postprocessing reconstructs the raw WPT event stream, rather than accepting only the driver's summary. All 74 keyed subtest outcomes and all 23 file outcomes exactly match the historical integer-only oracle, including expected-status fields and overall WPT exit **1**.

| Group | PASS | FAIL expected by WPT metadata | Intentional oracle FAIL with PASS expected |
| --- | ---: | ---: | ---: |
| Untransformed-edge precision, four tests | 4 | 0 | 0 |
| Separate transformed-edge precision, four tests | 2 | 0 | 2 |
| Existing regression tests, 66 subtests | 64 | 2 | 0 |

Thus the four traversal tests pass without the DOMRect repair. The two transformed precision failures remain observable; neither the driver nor postprocessor changes their expected status. The total is 70 PASS and four FAIL. Candidate and restoration binary builds, WPT lint and scoped format checks all returned zero. Full build logs, including their warnings, are retained. No timing run or baseline rerun occurred.

## Exact source roles

The candidate contains the sealed v4 four-file traversal implementation plus temporary pre-fix-102 DOMRect.cpp, SHA-256 `7f3d650772a2053cdac784410c68014a2abb2998e1b1cd4f57430585c7b12cc5`. Preparation obtained that file from the specified Git parent and checked it against the older integer-only source and runtime receipt. V4's own original DOMRect snapshot already includes fix 102 and was not mislabeled as the pre102 source.

All five original sources were restored byte-for-byte, including fixed DOMRect SHA-256 `340a676a79f33faa6f6243bd1c5af4c4bba99310142ee0b24a6ecbf2da1bfc9e`; the temporary WPT was removed and the restored build succeeded. Twenty other native files remained fixed through WPT and restoration. Candidate source, test, metadata and binary hashes were stable before/after WPT. Retained source snapshots match those contemporaneous hashes.

BEFORE, FINAL and pinned INPUTS agree on historical HEAD `99a9ca84f08370c1797720db8688bcb3747f6985`, the staged binary diff and full stage-entry hashes for the 229-file research commit. These establish preservation at the end of the experiment. Subsequent authorized signing may advance HEAD and staging; the checker deliberately does not consult the current repository. Raw index metadata-byte identity is not claimed.

## Replay and limits

`python3 -I -S -B verify.py --files-sha256 <external FILES pin>` authenticates the closed artifact and reconstructs COMPARISON from captured raw events, source roles and restoration/build receipts. It runs no build, browser or Git operation. Driver, INPUTS and oracle pins are fixed in EXPECTED-PINS; every prepared runtime-local input is rechecked. The pinned 400-input preflight's external research dependencies were authenticated by the reviewed driver before execution; this postprocessor does not re-execute their proofs. Historical binaries are identified by contemporaneous hashes and are not archived here.

This is a shared-build check with fix 102 removed temporarily, not an isolated upstream build or proof of universal independence. The source applicability package, formal/provider admissions, independent runtime review and performance decision remain separate. No live runtime files, native source, index, HEAD or browser state were modified by this postprocessing task.
