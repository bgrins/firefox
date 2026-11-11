# Getter branch runtime comparison preparation

Prepared only. No build, WPT lint, browser execution, live source write, application inspection or Git mutation has occurred in this capsule. Execution HEAD and retained-build selection are null until root freezes the experiment. Independent candidate source review is pending separately.

The copied candidate changes only `KeyframeEffect::GetKeyframes` in `dom/animation/KeyframeEffect.cpp`. The exact four-case `getkeyframes-specified-branch.html` fixture is copied unchanged. This comparison does not install the earlier four-file owned-generation candidate or implement its missing-pseudo work.

## Exact expected comparison

The suite has 13 pages and 135 records: 122 callbacks plus 13 OK harness endings. Its first 12 pages are the signed owned-generation ordinary suite, with all 130 records preserved. The added page has the existing passing WAAPI control and three reproduced failures.

| Stage | PASS callbacks | FAIL callbacks | OK harness endings |
|---|---:|---:|---:|
| Required fresh baseline | 100 | 22 | 13 |
| Predicted candidate | 103 | 19 | 13 |

The only allowed changes are these three FAIL-to-PASS transitions on the new page:

- Replaced CSS keyframes preserve specified variable expressions.
- Detached CSS effect returns only its specified endpoint.
- Transferred CSS effect returns only its specified endpoint.

`EXPECTED-BASELINE.json` is derived from authenticated **actual raw logs**, including messages, expected statuses and known-intermittent classifications. It is not the earlier status-only four-case proposal vector. `derive.py` reparses the signed ordinary baseline and its accepted candidate, checks their stored results and successful build/restoration receipts, then reparses the separate four-case baseline at `ec467c0219d3d5daf70f42fcc53677cf8a262173`. Archived executions and analyzers are never rewritten or refreshed.

`EXPECTED-CANDIDATE.json` is a prediction, not observed candidate output. Only the three target rows change. Their success-row shape is derived from the actual passing WAAPI callback on that same page, preserving field presence precisely. The comparison requires those three exact status transitions and exact predicted success details. All other statuses, messages, expected statuses and intermittent classifications remain identical, including all ordinary records and the WAAPI control. Missing or additional improvements are refused, as are regressions or changed diagnostics on an unchanged status.

## Inherited transaction and deltas

`bundle.py`, `process.py` and `freeze.py` are byte-identical to the signed owned-generation runtime. `run.py` has one behavioral delta: candidate comparison selects the exact-three-improvement policy. The complete raw-log parser and comparison-key construction in `analyze.py` are unchanged; only comparison policy is extended. `HELPER-PROVENANCE.json` and the `*-DELTA.patch` files record every helper origin and change.

The candidate performs a real `mach build binaries -j6` with the inherited 2,400-second deadline. Baseline mode uses the reviewed retained binary, as in the predecessor transaction. Both modes install/lint the same three temporary WPT fixtures and execute the identical 13-page suite with a 1,800-second deadline. The tracked named-range test remains an existing suite input, never a temporary fixture. Forty source/helper/metadata pins cover the test inputs.

Strict lifecycle checks reject crashes, ERROR/CRITICAL records, duplicate or missing callbacks/harness endings, wrong names/statuses, malformed suite/test ordering and assertion-count violations. Forty-one synthetic rejection controls exercise the preserved gates plus partial/extra improvements, WAAPI regression and changed baseline/candidate details for the intended improved rows.

## Preparation and root-owned freeze

Preparation checks are read-only outside this capsule and temporary patch-check directories:

```sh
python3 -I artifacts/css-keyframe-getter-branch-comparison-20261110-v1/check.py
```

They authenticate 25 signed helper/evidence objects and 16 separately frozen candidate/baseline inputs, check exact forward/reverse scratch patch application, rederive the vectors and run synthetic parser/comparison controls. Preparation does not inspect or change the live application. Candidate source-review completion remains a root review responsibility; the frozen hashes prevent silent candidate changes.

After source/runner review and exclusive source/app/Git reservation, root selects the full execution HEAD and retained-build receipt:

```sh
python3 -I artifacts/css-keyframe-getter-branch-comparison-20261110-v1/freeze.py FULL_EXECUTION_HEAD PATH_TO_COMPLETED_RETAINED_BUILD_RECEIPT
```

Keep this capsule untracked through freeze and execution, because freeze updates its plan and execution manifest. Freeze preserves the inherited clean-tree, source/binary/config/test identity, artifact-only source bridge and completed-build/WPT receipt gates. It emits `FREEZE-READY.json` only after validation succeeds. No execution is permitted by the runner while HEAD is null or a successful freeze receipt is absent.

Root then runs fresh transactions:

```sh
python3 -I artifacts/css-keyframe-getter-branch-comparison-20261110-v1/run.py baseline baseline1
python3 -I artifacts/css-keyframe-getter-branch-comparison-20261110-v1/run.py candidate candidate1 baseline1
```

Neither command has been run for this capsule. The pre-existing four-case baseline is historical evidence for the expected vector, not a substitute for the fresh 135-record baseline.

## Restoration and acceptance boundary

The unchanged transaction backs up the complete application bundle and three extras; guards source/fixture writes; restores only bytes matching its own writes; checks process-group quiescence before restoration/backup deletion; and verifies source/config/test pins, HEAD/index, sampled binaries and application/extras. It retains backups on restoration failure. Full build intermediates are not rolled back, so this is not byte-for-byte objdir restoration.

Root owns execution, complete build/harness log review and independent final restoration verification. WPT exit 0 or 1 alone is not success: the exact vector and all lifecycle/diagnostic gates must pass. Optimized success would validate this narrow getter repair; it would not close the separate missing-pseudo, general reentrancy, debug/sanitizer or full CSSOM serialization obligations.
