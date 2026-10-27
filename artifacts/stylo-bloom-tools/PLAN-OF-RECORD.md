# CSS and Stylo verification plan

Fix 137, used non-type attribute fallback cycles, is committed as `aa3f0588538800300df20a2f7de40ce8ac2ffec1` after research `38c1b6093c7bf87034ad583e2c84c2277f34ccfb`. The original/candidate comparison changes 15 PASS + 19 FAIL to 34 PASS; all 154 existing assertions and six reftests remain passing. Native build and WPT lint pass. Tentative P3 CSS correctness. Source audit and browser reproduction found the defect; the separate Lean guard model supports normalized cycle semantics, not native refinement. The upstream export documents overlap with numeric fix 499c0c6 and has transport/syntax validation only. Existing raw-nested expectations remain unchanged. No new canonical Lean coverage is claimed.

Fix 136, contained counter append invalidation, is committed as `37bc9b06f034c191be50aa4949b072bbf7d5a64e` after research `7cc4b9b3f524117870d19fff665843fc876d495d`. The original/candidate/original/candidate comparison gives 12 PASS + 12 FAIL / 24 PASS / 12 PASS + 12 FAIL / 24 PASS. All 64 quote subtests and eight existing counter regressions remain passing. Three builds and WPT lint pass. Tentative P3 visual correctness. Source audit and browser reproduction found the issue; the separate Lean model corroborates conditional delivery laws (14 audits, 12 examples, five rejected false claims). No clean-upstream build, security, measured performance or universal native-refinement claim. The original outer tool handle was lost; archived child exits and a fresh final-state verification supply the completion evidence.

The typed-demand prototype now passes its full native build, 20 native tests including 22 new real-resolver calls, and four ordinary WPTs (253 PASS, three existing expected FAIL; no unexpected results). Production pending-provider integration remains unfinished and disabled. The versioned var-fallback trace does not cover the newly observed attribute and unit dependency failures. Canonical Lean coverage counts are unchanged.

Fix 135, contained quote append invalidation, is committed as `0d27cb839f013f214973215cd0a8ce8a87c4b780` after research `d2e8f520eb1f1f66d69ad5568b092b9b05fdf9a4`. The candidate/original/candidate comparison gives 64 PASS / 52 PASS + 12 FAIL / 64 PASS, with all 18 existing regressions unchanged (15 PASS and three expected FAIL). Tentative P3 visual correctness. Discovery came from source audit and browser reproduction; conditional Lean models corroborate scope/dependency laws, not universal native correctness. No clean-upstream build, security or measured performance claim. The adjacent counter append issue is tracked separately as fix 136.


**136 accepted fixes: 136 committed locally, 0 accepted pending, and 1 additional held repair excluded.**

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 26 | 0 |
| Attributes and custom properties | 17 | 0 |
| Animations, timelines and transitions | 16 | 0 |
| Text and fonts | 15 | 0 |
| Layout, sizing and positioning | 22 | 0 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **136** | **0** |

Fix 121 now includes its validated one-block expectation correction. The signed history rewrite preserves the final tree; current commit IDs below come from the [new rewrite receipt](../../artifacts/css-integer-stored-range-history-publication-runtime-v1/RESULT.json). Historical signing receipts retain their original IDs. All 135 accepted fixes remain committed; held repair 120 stays excluded.

## Latest verified work

The callable typed-demand resolver passed all 20 selected GTests across four suites. Four ordinary substitution WPTs produced 256 subtests (253 PASS and three existing expected FAIL), four OK harness endings and no unexpected results. Source/resource/metadata and root/nested preservation checks passed. See [validation checkpoint](../css-demand-and-cycle-validation-20261027-v1/REPORT.md).

The used bare/unit attribute fallback defect is now fixed and committed as fix 137. The raw-nested lead still has five reproduced discrepancies and eight controls; its reviewed proposal explicitly corrects two old WPT expectations and adds 29 tests, but is not browser-validated. Registered-number comparison still shows seven shared discrepancies and one additional local prototype control failure. Those remaining leads are unaccepted.

The signed substitution-completion model has 17 audits, 16 kernel examples and six rejected false claims, independently replayed. It proves already-settled outcomes stable under coherent completion, not native scheduler confluence or full CSS semantics. The canonical library remains at `162b20fb7c53a0ab89b20875a965baee98fb66bb` with previously verified 11,840 audits, 12,438 cases, 173 expected-false cases and 2,155 source fingerprints; this turn did not rerun or expand those counts.

The separate attribute guard model also passes 13 general laws, 23 kernel examples and nine rejected false claims. It distinguishes selected fallback cycles from opaque raw strings; parsing, namespaces, invalidation and native correspondence remain outside that model.

## Execution order

1. Preserve signed fix 137 and its original/candidate evidence, alongside independently reviewable quote fix 135 and counter fix 136.
2. Build and validate the reviewed raw-nested repair and 29-case WPT, including explicit correction of two historical attr-cycle expectations.
3. Complete actual winning pending-provider collection and joint ordinary/animated/prioritary resolution, preserving current-base freshness, cycle policy, isolated endpoint contexts, effect publication and memory reporting. The single-collector and disposable-context proposals remain uncompiled.
4. Resolve registered-number false dependencies while retaining real numeric math operands; distinguish the additional local prototype failure from release defects.
5. Preserve Bloom milestones 1–6 and scoped specification correspondence; keep accepted fixes standalone and all work local.

## Historical record

Earlier milestones and scoped claims remain in the [dated archive](PLAN-OF-RECORD-20261027-HISTORY.md) and signed Git history. Current work preserves held repair 120 outside accepted counts.
