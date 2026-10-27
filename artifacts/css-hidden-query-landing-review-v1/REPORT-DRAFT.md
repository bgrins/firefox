# Final hidden-query landing files: result review (pending)

All five completed phases independently recounted. Recommendation: GO for the three separate bounded native+WPT repairs on the tested HEAD, conditional on successful authenticated final restoration and the separate source/formal gates. Final review seal awaits restoration. This reviewer authored earlier boundary controllers but did not author this final landing controller or final cleanup. The review verifies source/test transfer and actual raw outcomes; it does not claim universal layout/dirty-state or machine-code correctness.

| Phase | PASS | FAIL | Column7 | Block14 | Grid8 | Existing50 |
|---|---:|---:|---|---|---|---|
| Baseline |62|17|5P/2F|3P/11F|4P/4F|50P|
| Column only |64|15|7P|3P/11F|4P/4F|50P|
| Block only |73|6|5P/2F|14P|4P/4F|50P|
| Grid only |66|13|5P/2F|3P/11F|8P|50P|
| All three |79|0|7P|14P|8P|50P|

Each completed phase has79 exact ordered subtests,9 OK harness ends, zero calibration failures and exact expected statuses/messages. Each native repair passes all its own landing cases while leaving the other two repair subsets unchanged. Relative to baseline, column fixes2, block11 and grid4; none introduces a new failing test. Phase build exits0 and all29native/resource/binary-before/after/raw-RUN joins pass.

## Exact patch and source roles

INPUTS e582fdf18c401b30289fbaf26bf461c2f421808020718f263d83d176e55809fb authenticates112 controller/source/test inputs. Landing fixture seal d07313be9f6bf371cac7579a0ec7a43d8e57184d0f63da1ecf50949d63d2bcbc authenticates final cleaned bytes. Exact in-memory hunk application proves:

- Column patch0ccbbe34247fe08012bf916167f88a17b5d5415ae291e7d66f5ec521b3fe2fe4 produces selected PresShell candidate plus column geometry3 and unchanged auto4 tests.
- Block patch8135894b6f983e81c3aeb90fb8b35185685052b8c3b09a0b353c164f58ea5ef8 produces selected nsBlockFrame candidate plus cleaned14case test.
- Grid patch91a4c17345c0e12c77218e9c7ef5122f7056d92554a48444c9eb3ac2bb670c14 produces selected nsGridContainerFrame candidate plus8case test.

No patch has additional native or research targets. Column cleanup specializes the existing table-width path to col/colgroup/table, removes unused outer-route/td code and unused debug recording, and keeps ordered queries/calibration/expectations. Block cleanup preserves all14 selected case objects and removes only unused float/OOF fixture/style branches and debug recording. Auto4 bytes are unchanged. These final files are now actually run, not merely mapped to older larger fixtures.

Each phase normalizes24 source files to retained HEAD90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e, then applies explicit PresShell/block/grid roles. The remaining five guarded files remain pinned. Fixes101/104/105 are constant in these builds. The final restoration restores the original working tree, which includes unaccepted prototypes; that restored build is distinct from every tested phase. No proof of arbitrary-upstream independence follows. Prior boundary-v2 separately tested column/block selected cases without104/105, with101 retained.

## Scope retained

Column eligibility uses immediate group/table provider readiness for a clean column/group while keeping the original queried frame for ancestor walking. Block marks every child of the skipped line. Grid marks principal children at its own hidden-layout return. The tests demonstrate the selected visible/hidden, nested leaf, later inline-child, table-first rescue and auto-scroll paths. They do not prove all histories/dirty barriers/anonymous providers/continuations or arbitrary float/OOF ownership. Earlier main boundary run retains two float failures; failed fragment calibrations remain unreached coverage. Those are not silently converted to success by this compact landing set.

This campaign has no timing run. Prior cost evidence compares baseline/both block-column under bounded workloads and cannot establish grid cost or broad no-regression. Individual native/source and conditional formal review obligations remain separate.

Reproduce source transfer with `python3 -I -S -B source_check.py` and each completed phase with `python3 -I -S -B recount.py PHASE`. No live source/test/browser/build/Git mutation is performed by these checks.

Combined phase now independently verifies79PASS/0FAIL,9OK, no calibration failures, exact predictions and all29source/resource joins. Across five phases:395 raw subtest observations and45 OK harness ends. Each individual repair fixes its targeted failures and the combined build fixes all17 baseline failures; no additional runtime is requested by this review. Final restoration and immutable runtime manifest remain the final evidence gate.
