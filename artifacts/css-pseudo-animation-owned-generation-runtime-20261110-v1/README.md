# Owned keyframe-generation preservation experiment

Prepared only; no build or browser test has run for this capsule. Execution HEAD and retained-build selection are intentionally unset. The copied four-file candidate is the reviewed patch `3d36502810ce70d334b0a3c8e80949ef93bcd387444bf9d802881e59e3f6e3c5`. It replaces the earlier completed-output snapshot proposal, not the current live implementation. The source/test baseline is `526cc18cd58f62d839863c8587d3daffccfab722`; root's combined #172 build has identical non-artifact tree contents after history reorganization.

## Exact policy and provenance

The experiment permits zero changes. Both variants must produce 130 distinct records: 118 callbacks (99 PASS, 19 known FAIL) and 12 OK harness endings. Callback/harness keys are distinct and duplicate records are rejected. Status, message, expected status and known-intermittent fields must all agree, both against the derived historical baseline and between the fresh baseline and candidate. An unexpected improvement is a failure requiring review, just like a regression; the predecessor's three-improvement rule is not retained.

`derive.py` reparses authenticated accepted raw logs using their authenticated historical analyzers and verifies their recorded parsed results, successful build/terminal and restoration receipts. It takes the complete 99-row range candidate vector, then adds only the retained CSSOM lifetime (20 callbacks) and underlying-value (9 callbacks) pages plus their two harness endings from the accepted snapshot candidate. `EXPECTED-DERIVATION.json` records both raw hashes. The snapshot predecessor compared statuses only; this new policy additionally checks its recorded diagnostic/classification values against the fresh baseline. No historical result is represented as a run of this new candidate.

The important subgroups are 12 passing attribute cases; three passing new named-range grouping cases; percentage `getKeyframes` with 31 PASS and its two known FAILs; CSSOM lifetime with 13 PASS/7 FAIL; underlying values with 6 PASS/3 FAIL. Current named-range WPT content is tracked and must not be installed as a temporary fixture. Only the two retained CSSOM pages are installed in both modes. Both are WPT-linted in both modes.

`ORIGINS.json` separates 19 signed-revision object inputs from 14 reviewed frozen candidate inputs that were not yet committed at preparation. Bundle/process helpers are byte-identical to the newest signed range runtime. `RUN-DIFF.patch` shows only the successful-freeze receipt guard and stricter historical baseline comparison; `ANALYZE-DIFF.patch` replaces the improvement policy; `PARSER-CONTROLS-DIFF.patch` provides the zero-change controls. Source roles install four native files only in candidate mode. Native/test/helper/metadata pins and exact candidate copies are checked independently of the runner.

## Preparation and freeze

Run source-only preparation checks with:

```sh
python3 -I artifacts/css-pseudo-animation-owned-generation-runtime-20261110-v1/check.py
```

This authenticates immutable source objects and copied artifacts, forward/reverse scratch patch application, 38 current test/helper/metadata pins, the derived vector and 30 synthetic parser/comparison rejection controls. It does not inspect or modify the current app, invoke Mach, install tests or change Git state. `BUILD-READINESS.json` separately records a read-only source-bridge check of the completed combined build receipt; it is not a frozen runtime selection or live binary verification.

After root has committed the candidate/source-review work, reviewed the wrapper and reserved exclusive source/app/Git ownership, root may freeze using the full execution HEAD and final retained receipt. Keep this runtime capsule untracked through freeze and execution: freezing changes its plan, which would otherwise dirty the tracked tree and prevent the runner from starting.

```sh
python3 -I artifacts/css-pseudo-animation-owned-generation-runtime-20261110-v1/freeze.py FULL_EXECUTION_HEAD artifacts/css-keyframe-order-combined-current-build-20261110-v1/build-result.json
```

Freeze requires a successful completed build and WPT receipt, clean tracked tree, matching current binaries/config/source/test bytes, and artifact-only tree differences between source pins, build revision and execution revision. It binds the retained receipt and all execution inputs. It emits `FREEZE-READY.json` only after final validation succeeds; the runner refuses execution without that receipt. A failed freeze must be inspected and repaired rather than bypassed. Preparation's `PREPARATION-FILES.json` remains a historical inventory; the later `RUN-INPUTS.json` governs execution.

Root can then run separate transactions:

```sh
python3 -I artifacts/css-pseudo-animation-owned-generation-runtime-20261110-v1/run.py baseline baseline1
python3 -I artifacts/css-pseudo-animation-owned-generation-runtime-20261110-v1/run.py candidate candidate1 baseline1
```

Candidate mode builds `binaries -j6` with a 2,400-second deadline before the identical 12-page suite. Baseline uses the retained binary. WPT exit 0 or 1 is allowed because known unannotated failures remain; exact raw-vector, lifecycle and diagnostic gates remain mandatory. The parser rejects crashes, ERROR/CRITICAL records, malformed lifecycle, missing/duplicate callbacks and harness endings, and out-of-range assertion counts. Root must inspect complete build/harness logs for diagnostics not represented by structured errors.

## Restoration and limits

The inherited transaction backs up the complete application bundle and three extras. It guards source and fixture writes, restores only bytes matching its own writes, restores application/extras and checks HEAD/index/source/config/test pins and sampled binaries. It requires all owned process groups to be absent before restoration or backup deletion. Concurrent mutation is forbidden throughout the transaction and independent terminal review. Build intermediates are not rolled back; this is not byte-for-byte object-directory restoration.

This experiment covers ordinary property generation, CSS default capture/opt-out, endpoint and range handling, existing CSSOM controls and attribute-dependency forwarding. The new `PropertyInputSnapshot::RefreshComputedOffsets` API has no production caller and is not exercised by this suite. A future query path requires direct coverage of owned refresh and coherent timing/style/range context. Even a fully unchanged optimized comparison does not accept a missing-pseudo repair or close its separate debug, transform-hint, provider freshness, cascade/mask and cache/admission gates.
