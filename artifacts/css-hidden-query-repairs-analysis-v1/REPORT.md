# Hidden geometry query candidates

The four native variants isolate two proposed repairs on top of committed fixes 104 and 105. They do not include the other working-tree prototypes.

| Variant | PASS | FAIL |
|---|---:|---:|
| Baseline | 55 | 11 |
| Column provider gate | 61 | 5 |
| Skipped block line marking | 58 | 8 |
| Both | 66 | 0 |

`analyze.py` independently recounts all raw WPT events, requires exactly 66 distinct subtests and seven successful file ends per variant, and compares the baseline status/message tuples with the preceding experiment. The 50 already committed flex and absolute-positioned landing cases pass in every variant.

Six failures are repaired by the column change alone: four flex/absolute table column or group queries, plus ordinary direct-table-width column and group queries. Three are repaired by the block change alone: ordinary outer-width cell and table queries, and the direct-table-width cell query. Two ordinary outer-width column/group queries require both changes. The exact cases and failure messages are in `RESULT.json`.

There are no PASS-to-FAIL transitions when adding either candidate to baseline or adding the remaining candidate to either single-repair variant. Replacing one candidate with the other is not an additive comparison and loses that candidate's distinct repairs.

The model composition in `css-hidden-provider-path-proof-v1` explains how marking a selected block subtree can make a table provider eligible while leaving its column group and columns clean. The proposed column gate can then admit the original query target. That is a conditional model result: this experiment does not trace native frame identities, the selected line membership, or the complete invalidation and publication history. Passing geometry tests does not discharge those proof premises.

Neither candidate is accepted as a native bugfix yet. Remaining checks include ordinary block/inline and owned-child boundaries, table spans and fragmented-provider behavior, the shared scrolling caller, and the added cost of recovery and clean geometry queries. This run has no timing or instrumentation phases. Earlier flex/absolute cost measurements do not measure these candidates. The baseline contains fixes 104 and 105, so this run alone also does not establish independence from those fixes.

The runtime controller preserves the five tracked WPT files, temporarily installs only the two diagnostic files, guards 28 source paths, and restores the 23 written source files and the original working-tree prototypes. Terminal restoration and build receipts are retained with the runtime; their final authentication is recorded separately in `ROOT-FINAL-CHECK.json`.
