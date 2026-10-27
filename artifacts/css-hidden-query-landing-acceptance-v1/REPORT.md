# Hidden-query repair decision

Accept three bounded native repairs for separate local Gecko/WPT commits. The exact final files were exercised individually and together; source/build restoration passed. No full CSS or whole-frame-lifecycle verification is claimed.

| Repair | Native path | Own WPT cases | Baseline failures repaired |
| --- | --- | ---: | ---: |
| Column provider admission | PresShell.cpp | 7 | 2 |
| Skipped block line children | nsBlockFrame.cpp | 14 | 11 |
| Skipped Grid children | nsGridContainerFrame.cpp | 8 | 4 |

The five-phase comparison contains 395 subtest observations and 45 OK harness ends. Baseline has 62 PASS / 17 FAIL; individual column, block and Grid variants have 64/15, 73/6 and 66/13; all three pass 79/79. Every phase preserves all 50 existing controls. Each individual change leaves the other two new partitions unchanged. No calibration failures or new baseline failures occur. WPT lint and all five builds pass.

## Source and formal basis

Column queries can select a clean column or group whose table provider is dirty. The repair checks that typed parent chain and retains the original query target for the hidden-ancestor walk. The provider model and path-composition component prove conditional admission and recovery under explicit native identity, history, lifetime and provider premises. Table-column pruning in the formal model guided the targeted investigation; the native defect was localized through browser probes and source analysis.

The block repair marks every child in the skipped line before returning. The line model extends the existing subtree traversal proof and captures later inline children and selected descendants under its readiness premises. Browser/source investigation established the native branch; this is not automatic verification of the C++ implementation.

Grid's skipped-own-content return now invokes its existing principal-child marking helper. This reuses the existing helper model and source audit; there is no new full Grid-layout theorem. Its direct-item and leaf-first bounding/offset cases reproduce and recover in isolated builds.

The helper uses an iterative worklist and prunes already-dirty roots. Review found no new recursion blocker. Dirty-root/clean-leaf histories, real frame ownership/lifetime, callbacks, provider completion and geometry publication remain explicit mathematical/native boundaries.

## Boundaries and cost

The preceding seven-phase 100-case campaign adds ordinary/inline/owned-child and column-span coverage. Selected column/block landing identities also pass after removing fixes 104/105 while retaining the required fix101 key. That is a bounded dependency check, not an isolated whole-upstream build. Grid fixtures have no flex/table/absolute-child dependency; no separate whole-upstream runtime is claimed.

The broader column/block pair leaves two float queries failing. A separate float fixture reproduces six failures on the restored prototype build; its candidate is unaccepted. Attempted multicol table-fragmentation calibration did not reach actual table splitting and remains unreached coverage.

Combined column/block timing removes 720 stale recovery rectangles. At 128 siblings, median first-query sums over 16 mutations change from 0/0/1 ms to 4/6/7 ms for block/cell/column. Clean hot-loop median changes stay within one millisecond in this coarse fixed-order sample. Recovery performs newly correct work; this is not a broad no-overhead result. Grid and float costs were not measured. The evidence does not establish security impact; these are geometry-correctness repairs.

## Packaging and restoration

Each native commit must contain only its selected native file and its own tested WPTs: column three paths, block two, Grid two. Research precedes those commits. The exact patch-to-phase source/test transfer and worktree overlay apply/reverse checks passed.

The experiment normalized 24 source files, guarded 29, and restored the original working sources and build, including older unaccepted prototypes. Original/final/live source, HEAD and index snapshots matched; temporary WPTs were removed and resources preserved. A final installed-tree build and 79-case run will check integration with those preserved prototypes separately from the isolated attribution above.
