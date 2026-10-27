# CSS and Stylo verification plan

Fix 135, contained quote append invalidation, is committed as `0d27cb839f013f214973215cd0a8ce8a87c4b780` after research `d2e8f520eb1f1f66d69ad5568b092b9b05fdf9a4`. The candidate/original/candidate comparison gives 64 PASS / 52 PASS + 12 FAIL / 64 PASS, with all 18 existing regressions unchanged (15 PASS and three expected FAIL). Tentative P3 visual correctness. Discovery came from source audit and browser reproduction; conditional Lean models corroborate scope/dependency laws, not universal native correctness. No clean-upstream build, security or measured performance claim. The adjacent counter hypothesis remains unrun and uncounted.


**134 accepted fixes: 134 committed locally, 0 accepted pending, and 1 additional held repair excluded.**

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 26 | 0 |
| Attributes and custom properties | 16 | 0 |
| Animations, timelines and transitions | 16 | 0 |
| Text and fonts | 14 | 0 |
| Layout, sizing and positioning | 22 | 0 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **134** | **0** |

Fix 121 now includes its validated one-block expectation correction. The signed history rewrite preserves the final tree; current commit IDs below come from the [new rewrite receipt](../../artifacts/css-integer-stored-range-history-publication-runtime-v1/RESULT.json). Historical signing receipts retain their original IDs. All 134 accepted fixes remain committed; held repair 120 stays excluded.

## Latest verified work

The callable current-provider resolver passed the normal and GTest builds and all 19 native tests; normal pending recipe production remains disabled. The 113-case metadata comparison preserved all 110 PASS and three expected FAIL observations, changing only the fix 121 expectation. The canonical library is signed at `162b20fb7c53a0ab89b20875a965baee98fb66bb` and its full check passes 11,840 audits, 12,438 cases, 173 expected-false cases and 2,155 source fingerprints. Ten audits transfer from reviewed steps research, with no new discovery, normative coverage or native-refinement credit.

Next: Integrate winning pending animation providers through the real cascade and dependency scheduler; preserve explicit current-base, cycle-policy, dependency-publication and memory-reporting obligations.

## Execution order

1. Keep quote fix 135 and its research separately reviewable; retain its exact comparison evidence.
2. Continue the full animation pending-provider integration through winning cascade gates; do not replace scheduling with preselected provider snapshots.
3. Preserve Bloom milestones 1–6 and scoped specification correspondence; keep accepted fixes and their research separately reviewable.

## Historical record

Earlier milestones and scoped claims remain in the [dated archive](PLAN-OF-RECORD-20261027-HISTORY.md) and signed Git history. Current work preserves held repair 120 outside accepted counts.
