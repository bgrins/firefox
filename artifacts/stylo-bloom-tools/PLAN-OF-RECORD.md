# CSS and Stylo verification plan

**133 accepted fixes: 133 committed locally, 0 accepted pending, and 1 additional held repair excluded.**

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 26 | 0 |
| Attributes and custom properties | 16 | 0 |
| Animations, timelines and transitions | 16 | 0 |
| Text and fonts | 13 | 0 |
| Layout, sizing and positioning | 22 | 0 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **133** | **0** |

Latest signed fixes: calculated jump-none minimum `ea6cde0db70c` now includes its two expectation corrections; calculated cubic-bezier x ranges `8ccca4c4901c` includes its WPT and two expectation corrections. All 133 accepted fixes are committed; repair 120 stays held and excluded. The current local browser contains both fixes. See the [signing record](../css-local-signing-20261027-v4/CHECKPOINT.md).

## Latest verified work

- Fix 134 `8ccca4c4901c`: original/candidate/restored results 82 PASS/31 FAIL → 110 PASS/3 FAIL → exact 82 PASS/31 FAIL. All 38 targets pass, 28 observations repaired, 75 controls unchanged and all 113 restored exactly. Final installed capture reproduces the candidate with corrected expectations. [Acceptance](../css-cubic-bezier-calc-range-acceptance-v3/REPORT.md).
- Fix 133 `ea6cde0db70c`: the two stale jump-none expectations are now folded into the native/WPT commit. Its 44-row metadata capture preserves all observations. The signed rewrite preserves the final tree and keeps a backup branch.
- Compact Arc borrowing passed five unit tests under each allocation configuration, three compile-fail doctests, all 17 selected host tests and the unchanged 166-outcome browser comparison. The API is committed in `feaec25f9647`; broader owner/provider work remains experimental.
- Canonical Lean totals remain 11,830 audits, 12,424 executable cases, 170 expected-false cases and 2,153 source fingerprints. These are validation counts, not percentages of CSS coverage. The prepared steps transfer has focused replay evidence but is not yet applied to the canonical library.

## Execution order

1. **Finish the older expectation correction.** Fix 121 owns the remaining calculated-start unexpected pass. Its archived isolated range-only comparison establishes attribution. Validate the one-block expectation change, then fold it with its evidence while preserving a backup and updating descendant commit mappings. This is not a new bug. [Proposal](../css-integer-stored-range-metadata-correction-v2/REPORT.md).
2. **Review and integrate the prepared steps model.** The prepared transfer preserves ten theorem bodies and adds fourteen executable observations, including three false controls. Run the full canonical checker and preserve old cases/axioms before updating totals or signing the library. No native-refinement or normative-coverage increment is implied. [Proposal](../css-steps-origin-library-proposal-v1/README.md).
3. **Compile current-provider endpoint resolution.** The reviewed four-file callable stage needs normal/GTest builds and all nineteen host tests. Normal recipe production remains disabled. Winning-provider selection, coherent scheduling, animated-cycle semantics, dependency publication and memory reporting remain open. [Source review](../css-keyframe-provider-resolution-root-review-v1/REPORT.md), [host recipe](../css-keyframe-provider-resolver-host-preparation-v1/README.md), [cycle-policy audit](../css-keyframe-animated-provider-policy-v1/README.md).
4. **Extend specification correspondence and preserve Bloom milestones 1–6.** Continue versioned normative mapping, parser progress, provider ownership and fragmentation. Retain explicit parser/compiler/heap/provider premises; existing checkpoints do not prove all CSS or unchanged correspondence after implementation edits. [Open obligations](FORMAL-CLOSURE-CHECKLIST.md), [Bloom continuation](CONTINUATION-20261017.md).
5. **Keep fixes and evidence reviewable.** Commit each accepted native fix with its WPT and necessary expectation metadata; put supporting research before it. Keep work local. Remove obsolete task-owned build targets only after process and retained-evidence checks; keep the active Firefox object directory and canonical Lean build.

## Historical record

Earlier milestones and scoped claims remain in the [dated archive](PLAN-OF-RECORD-20261027-HISTORY.md) and signed Git history. Current work preserves held repair 120 outside accepted counts.
