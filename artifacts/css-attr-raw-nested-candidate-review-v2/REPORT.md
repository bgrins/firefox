# Candidate-2 paired evidence review

**PASS for the paired comparison.** Recomputing both raw WPT streams with the sealed assessor confirms the saved assessments and their exact bindings. All 17 baseline failures become passes; no passing assertion changes outcome. This review performs no acceptance or publication action.

| Group | Original-2 | Candidate-2 |
|---|---|---|
| Corrected existing attr-cycle targets |34 PASS / 3 FAIL|37 PASS|
| New raw/EOF targets |22 PASS / 14 FAIL|36 PASS|
| Unchanged regression assertions |329 PASS|329 PASS|
| Reftests |6 PASS|6 PASS|

The two phases serve identical repair-v2 target bytes. The three explicitly adjudicated historical oracle corrections are `CSS Values and Units Test: attr 3`, `attr 28` and `attr 29` (the full observed identities and original failure messages are retained in AUDIT.json). The EOF correction was made before this fresh pair, with primary-spec and independent-review evidence; it is not an expectation changed between phases. The earlier failed comparison remains immutable.

All seven added parser controls pass:

| Control | Original-2 | Candidate-2 |
|---|---|---|
| eof-bare-self | FAIL | PASS |
| eof-raw-string-self | FAIL | PASS |
| eof-typed-self | PASS | PASS |
| eof-nested-type-self | PASS | PASS |
| raw-self-with-valid-trailing-value | FAIL | PASS |
| raw-self-with-invalid-string-trailing-value | PASS | PASS |
| raw-self-with-unmatched-closing-token | PASS | PASS |

The regression signatures match exactly, including identities, outcomes, explicit/default expected fields, intermittent metadata and test ends. All three mutation callbacks finish successfully. The genuine typed-cycle, used-fallback and opposite-resolution-order controls remain passing.

The saved epoch HEAD is `bb88e8e6b31de9b832e896110e39504d68020c71` for both phases. Each phase binds its native role, compiled status and normal browser binaries. The candidate build-published epoch exactly equals its WPT epoch. Both application.ini symlink/target identities and bytes are stable within each phase, and the actual WPT BuildID/revision matches the corresponding saved metadata. BuildID changes from `20261027161407` to `20261027161737`; all other run_info fields match. Application.ini is the only cross-phase resource-pin change. All owned tests, metadata, reference documents and generated manifest are identical; only the owned configuration paths vary.

Root and nested pre/post preservation records are equal within each run. Both saved cleanups report the owned process group absent and temporary profile root removed. The candidate build logs success at 48.79 seconds and exits 0. Four non-fatal `KeyError: export` progress-monitor exceptions remain in its saved log; success is not described as an exception-free log.

## GTest carry-forward

`GTEST-CARRYFORWARD-2.json` is copied byte-for-byte from the root controller. The audit independently checks all 206 source/absence roles and both GTest-library hashes against the prior GTest epoch and current candidate epoch. It rechecks the prior log against the exact 20 selected test names, 20 PASS completions, four suites and zero failures/disabled tests.

This is carry-forward of the previous 20 passing native regression tests, not a fresh GTest execution. The normal browser binaries were rebuilt and have different hashes from that earlier epoch; those binaries are separately covered by candidate-2 WPT. No claim is made that GTests were rerun on the new normal binaries.

## Review boundary

This review authenticates saved capsules, epochs, raw events, copied resources and build/GTest records. Completed wrapper/build records attest full live preservation; current source, binary, process, HEAD and CURRENT-EPOCH state were deliberately not queried while root installed the tested WPTs. No browser/build/source/index/HEAD/epoch mutation occurred. No test-evidence blocker remains in the reviewed pair; signing and the exact standalone commit remain root-owned work.
