# Isolated hidden Grid two-phase draft

DRAFT_DISABLED_NOT_PREPARED_NOT_RUN. Root review and successful restoration of `css-hidden-query-boundaries-runtime-v2` are required before enabling preparation. No driver, browser, build or Git command was executed to author this draft.

## Inputs and source roles

The landing plan is authenticated against FILES `106e02648208d773ce222ef937e68cc8dbd60fe274562100353611b138d6b45f`. The first23 baseline files are exact copies of current campaign `prepared/head`, verified through externally pinned INPUTS `7f8b3a0e3d5892d65a1a6472f283a7c942f4f172b10ca4b7630f0bfb51ee4fbd`. Grid original/candidate are authenticated to the plan's source-role pins. `evidence/` retains these identities. All24 reviewed HEAD files are included, rather than adopting whatever native files happen to be live during a phase.

HEAD is fixed to `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`. Preparation compares every selected baseline to actual HEAD, snapshots all24 original and HEAD files, verifies the remaining five guards equal HEAD, requires an empty index and exact tracked tests, and pins support/metadata including Ahem. It also requires the prior campaign's terminal successful source restoration/rebuild and absent temporary tests. Any later HEAD change requires explicit source-role review; passing another command-line HEAD cannot bypass CONFIG.

## Two phases and gates

Both phases normalize all24 files to HEAD, excluding unaccepted prototypes. Candidate changes only `nsGridContainerFrame.cpp`, adding one `MarkPrincipalChildrenDirty()` call in the existing own-content hidden return. Existing101/104/105 repairs remain identical between phases. No column or block candidate, trace, cost hook, or standalone-removal phases are included.

Six files contain58 subtests: the exact executed Grid eight-case fixture plus five unchanged tracked landing controls (50). Only the Grid file is temporarily installed. Baseline must have exactly four hidden Grid FAILs at `selected query: after-parent-width`, four visible Grid PASSes, and50 control PASSes. Candidate must pass58, with all50 control status/message pairs unchanged. A different isolated baseline stops and restores for investigation. Outcomes and raw logs are retained before these gates; no assertions are relaxed. Passing would be bounded evidence, not full Grid correctness or upstream runtime coverage.

`run_wpt.py` is byte-identical to the reviewed boundary-v2 runner. It requires exact ordered subtest rosters, owned test IDs, six OK harness ends, complete suite, command exit0/1, stable source/binary/resource pins, and no calibration failure. Source/HEAD/index guards surround each build/test. The exception and restoration tail is also byte-identical: best-effort all-file restoration and owned-test removal continue across receipt-write failures, followed by restoration rebuild even when opening its log fails; final snapshots and virtual resource pins must match. External cancellation/host failure can still require manual recovery from retained originals.

## Review / later execution

`CONFIG.json` intentionally has `ready_for_preparation: false`. After root review and prior restoration, root may explicitly enable it and regenerate DRAFT-FILES; that changes the draft pin and must be recorded. Then the existing interfaces are:

```
python3 -I -S -B artifacts/css-hidden-grid-runtime-v1/prepare.py --draft-sha APPROVED_NEW_DRAFT_SHA --expected-head 90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e
python3 -I -S -B artifacts/css-hidden-grid-runtime-v1/experiment.py --inputs-sha PREPARED_INPUTS_SHA
```

These are future interfaces, not executed commands. `STATIC-CHECKS.json` records Python AST syntax, exact source-only delta, roster checks, unchanged runner and restoration tail. The two script diffs expose every change from the reviewed seven-phase controller. No new proof or calibration harness is introduced.
