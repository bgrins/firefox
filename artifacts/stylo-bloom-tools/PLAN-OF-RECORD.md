# CSS and Stylo verification plan

**132 accepted fixes: 132 committed locally, 0 accepted pending, and 1 additional held repair excluded.**

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 26 | 0 |
| Attributes and custom properties | 16 | 0 |
| Animations, timelines and transitions | 15 | 0 |
| Text and fonts | 13 | 0 |
| Layout, sizing and positioning | 22 | 0 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **132** | **0** |

The accepted queue is fully signed. The [fix ledger](BUGFIX-COMMITS.md) retains each native/WPT commit, prerequisite and evidence boundary. Repair 120 remains held and excluded; prototypes are not accepted fixes.

## Latest verified work

- Latest signed work: fix 133 `75271a173ba0` repairs calculated jump-none counts, preceded by evidence `366551d71eea`. The compact Arc borrow API and tests are separate in `feaec25f9647`. All 132 accepted fixes are committed; repair 120 remains held and excluded. See the [signing record](../css-local-signing-20261027-v2/CHECKPOINT.md).
- Latest signed checkpoints: CSS library `ef6f4dd2ed94` in its own repository; animation research `37e1d4e898c6` and steps research `0f0a8a5fb7d5` on the Firefox branch. The [signing record](../css-local-signing-20261027-v1/CHECKPOINT.md) includes an exact recovery snapshot of 132 unfinished working files. Accepted bug counts are unchanged.
- `19a313060adb`: signed computed-name research checkpoint. The integrated library passes 11,830 declaration audits, 12,424 executable cases, 170 expected-false cases and 2,153 source fingerprints. These are validation counts, not percentages of CSS coverage. The new model assumes normalized name parsing; raw CSS parsing and native correspondence remain open. [Full check](../css-variables-computed-name-library-application-v1/REPORT.md).
- `73a62b1ecf58`: signed test-only commit for real-document keyframe computation. `KeyframePresentation.LiteralOpacity` compiled and passed with a nonempty computed value and presentation teardown. Its two-file commit excludes the unfinished operation-arena registration. [Validation](../css-keyframe-presentation-calibration-validation-v1/REPORT.md).
- The operation/descriptor prototype previously passed both builds, ten native GTests and the exact browser comparison: 162 passing subtests, four retained provider failures, two passing crash tests and eleven successful harness endpoints. The retained failures still need a repair. [Comparison](../css-keyframe-operation-descriptor-capture-runtime-v1/REPORT.md).
- Both signed checkpoints preserve working source bodies and nested-library staging. The fixture build intentionally updates the two matching GTest-library copies. Its outer wrapper failed on obsolete log syntax; independent parsing confirms the actual named test passed, and the original failed wrapper remains recorded.

## Execution order

1. **Transition endpoint mutation: red/green validation complete.** The new regression produced exactly one stale-descriptor failure; clearing it preserves the full concrete replacement and passes both native tests, including explicit versus implicit underlying composition and retained ownership. The normal build and preservation checks pass. This is a prototype invariant repair, not a newly observed browser bug. The metadata test and correction remain with the uncommitted prototype. [Result](../css-keyframe-transition-green-validation-v1/REPORT.md).
2. **Complete current-provider animation resolution.** Compact borrowing now passes five unit tests under each allocation configuration and three compile-fail doctests. The normal/GTest builds and all 17 selected host tests pass. Browser comparison preserves all 166 outcomes (162 PASS, four provider FAIL), two passing crashes and eleven OK harnesses. The pointer-sized API is committed; the owner prototype remains experimental. Review and compile the prepared current-provider resolver next, then connect winning-provider enumeration, cycle policy and publication. [Results](../css-keyframe-owner-browser-terminal-review-v1/REPORT.md).
3. **Calculated easing ranges: jump-none fixed; cubic-bezier next.** Fix 133 is committed with its WPTs. Original/candidate/restored comparison repaired 20 failures, passed all 22 targets, preserved 55 controls and reproduced all 77 baseline outcomes after restoration. The separate Lean model has 10 audits, 11 examples and three false controls; no native-refinement or integrated coverage claim. The next prepared cubic-bezier experiment has 113 cases and needs independent review, compilation and browser comparison. Contextual integers and held repair 120 stay separate. [Acceptance](../css-steps-jump-none-acceptance-v1/REPORT.md).
4. **Extend the CSS model and correspondence.** Continue versioned normative requirement mapping, custom-property dependency/completion histories, parser progress, provider ownership and fragmentation. Separate specification-model results, executable examples and native refinement. Carry explicit parser/compiler/heap/provider premises; connect proofs to actual changing implementations rather than treating historical replay as current verification. [Whole-CSS strategy](../css-whole-spec-completion-strategy-v1/README.md), [open obligations](FORMAL-CLOSURE-CHECKLIST.md).
5. **Preserve the original Bloom milestones 1–6.** Their accepted checkpoints retain their recorded selector/provider/source scope. Changed cached dispatch and broader CSS semantics need fresh correspondence arguments; historical milestone completion does not close those gaps. [Bloom continuation](CONTINUATION-20261017.md).
6. **Commit and maintain evidence as work becomes ready.** Keep each accepted native fix and WPT in one commit, with required research preceding it. Record the commit and any prerequisites in the fix ledger. Keep work local. Remove task-owned build targets only after active-process checks and retained-evidence checks establish they are no longer needed; keep the active Firefox object directory and canonical Lean build.

## Historical record

The previous 2,024-line plan is preserved verbatim in [the dated archive](PLAN-OF-RECORD-20261027-HISTORY.md). Its pending, running and signing statements describe historical checkpoints. The linked acceptance records retain their original scope; this shorter current plan does not promote them to full CSS or Stylo verification.
