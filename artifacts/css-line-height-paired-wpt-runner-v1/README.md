# Callable reversible line-height WPT phase

This runner executes only the six frozen pages from css-line-height-paired-validation-plan-v1: 12 target assertions and 22 existing regressions. It does not install source, build, sign, or read/write the canonical CURRENT epoch. Root's reversible owner supplies an actual successful phase-local build epoch and restores source/binaries afterward. A passing comparison is validation evidence, not native acceptance.

Invocation (absolute epoch/output paths):

```
python3 -I -S -B artifacts/css-line-height-paired-wpt-runner-v1/run.py CAPSULE_SHA original-1 ABS_OWNER/original-build/EPOCH.json EPOCH_SHA ABS_OWNER/original-wpt
python3 -I -S -B artifacts/css-line-height-paired-wpt-runner-v1/run.py CAPSULE_SHA candidate-1 ABS_OWNER/candidate-build/EPOCH.json EPOCH_SHA ABS_OWNER/candidate-wpt
```

ABS_OWNER must be the checkout's artifacts/css-line-height-reversible-pair-runtime-1. Both outputs must be absent. The phase-local marker has exactly role, build_directory, source_package_manifest and owner_runtime. It binds the sealed font-only source proposal and original/candidate source hashes. Actual outer RESULT must report a successful preserved browser build with no owned processes/errors; inner build-RESULT must report exit0 and completed process cleanup. COMMAND and exact saved EPOCH bytes are pinned as evidence. This package is executable only with those future receipts; none has been fabricated or executed during preparation.

The staged guard is byte-identical to the reviewed typecheck-v2 guard, with the same STAGING.json. It checks exact staged165 names, blobs, patch, normal index flags, native scope, nested state, epoch pins and file identities against the supplied phase-local epoch. It does not project an empty index or publish any epoch. Existing source/control preservation outside this phase is additionally owned by the outer reversible driver.

The runner copies frozen fixtures, resources (including Rochester.otf), headers and metadata to a private root, uses the genuine captured manifest, and owns a fresh temporary profile/server process group. Timeout is600seconds; cleanup and post-preservation run even after process errors. BuildID and actual application metadata bytes/identity are independently bound for each phase.

Candidate loading pins the complete original output inventory and tools symlink, authenticates its same-capsule effective policy, successful preservation/cleanup, exact original build receipts and raw assessment replay. These checks repeat after the candidate. Unrelated phase pins and preserved staging/nested/ownership records must agree; only font.rs and four rebuilt binaries are excluded from paired pin equality. Source native scope differs only by font.rs. Index HEAD/entries/cached_diff must agree; working_diff may reflect the one native change and each phase's full guard verifies it independently. Raw index is phase-local, not required to equal across native writes/builds.

Original completed FAILs are observations. Candidate requires all12 target assertions PASS, at least one original target FAIL, exact22 full regression signatures and all6 harness-end signatures. Status, message, expectation/intermittent values and field presence are preserved. All assertions must complete and all page endings must be OK; infrastructure errors reject. Existing inherited-lh/font-load metadata permits intermittent failures, but a paired difference still rejects rather than being silently normalized.

Preparation performed only syntax/static and synthetic saved-evidence controls. No browser, native build, main runner, live epoch/index guard or mutation ran. Actual owner integration and browser results remain pending. A draft used cached instead of the actual cached_diff semantic field; root and reviewer caught it before sealing. The corrected original-replay controls use the exact semantic schema extracted from pinned v33 PRE-CURRENT-EPOCH, and explicitly reject cached_diff/entries/head drift.
