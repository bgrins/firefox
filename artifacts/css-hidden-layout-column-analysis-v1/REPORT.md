# Hidden layout: controlled cost and column readiness

Runtime restoration passed: the original and final snapshots match, all 28 guarded source files and HEAD/index match the live checkpoint, all 10 temporary test paths are absent, and the restoration build and experiment exit successfully. The bounded native decision is recorded separately.

## Correctness

The baseline passes 30 of 66 tests; both bounded repairs pass 55. All seven file ends are OK. There are 25 improvements and no regressions. All 58 identities, statuses and messages retained from compact-v3 are unchanged in their corresponding phase. The 50 proposed landing tests all pass with both repairs; the earlier isolated phases establish each repair's own partition separately.

The 11 unchanged failures consist of the four existing column/group probes and seven new ordinary-block probes. In the new file, changing the outer block's width leaves stale geometry for col, colgroup, td and table. Changing the table's own width leaves stale geometry for col, colgroup and td; querying the table itself succeeds. Each case checks explicit visible-peer and outer-box calibration before checking the selected query. These results show a broader remaining query-readiness problem than columns alone. They do not establish an installed-release or upstream-only reproduction.

## Controlled measurements

Both phases complete the same 220 progress markers, 84 measured batches and 13,440 full-rectangle observations under identical explicit startup controls. Both timing runners verify unchanged source/binary pins, process-group cleanup and profile removal. The baseline has 3,213 geometry mismatches, all hidden absolute descendants; both repairs have none.

At 256 branches, the median first-query bucket, summed over 16 post-mutation queries, changes from 1 to 8 ms for principal descendants and from 1 to 7 ms for absolute descendants. The principal fixture already has correct baseline geometry, so its added work is a conservative-invalidation cost. The absolute comparison includes recovery of incorrect baseline rectangles and is not an equivalent-correct-work comparison.

Visible mutation medians at 256 branches remain 5 ms for principal and 3 ms for absolute fixtures. Visible-query and repeated/distinct/second-pass/no-mutation medians remain 0 ms. Individual nonzero ticks are retained in COST.json. Integer-ms resolution, one process per variant, fixed phase order, benchmark overhead and the selected sizes limit the performance conclusion. These data show no repeated-query loop or visible-path cost blocker in this sample; they do not prove zero work or broad performance equivalence.

The earlier incomplete combined measurement remains a separate failed attempt. This successful controlled comparison supplies the missing observation without proving the cause of that earlier startup failure.

## Native column trace

The 16 instrumented outcomes and messages exactly match their uninstrumented counterparts. For each of col and colgroup, the trace records 12 clean-target queries with a dirty table provider, 44 clean-target queries with a clean provider, and four queries with both target and provider dirty. It separately records 196 column and 98 group rectangle publications.

The clean-target/dirty-provider condition therefore occurs in actual native execution. A query record binds both pointers and dirty bits within one call. The trace does not bind a DOM identity, assertion stage, stable frame lifetime, hidden ancestor or later publication to that call. Pointer equality across events is not used as a substitute for those missing joins. No table-kind query is logged; the queried table element's primary-frame representation is not established by that absence.

The minimal provider-readiness candidate is justified for a bounded paired experiment. It is not yet a native fix, and clean-table/stale-ancestor histories remain an explicit countermodel to universal sufficiency. The new td/table failures are outside the candidate's additional column/group branch.

## Reproduction

Run analyze.py, cost.py and trace.py with `python3 -I -S`. They bind their raw inputs by SHA-256, compare keyed outcomes, recount observation buckets and retain the trace's identity limitations. The independent runtime review additionally checks exact progress rosters, unchanged prior identities and restoration.
