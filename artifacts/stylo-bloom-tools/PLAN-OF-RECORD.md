# CSS and Stylo verification plan

**131 accepted fixes: 131 committed locally, 0 accepted pending, and 1 additional held repair excluded.**

| Area | Committed | Accepted, pending |
|---|---:|---:|
| Selectors, Bloom filters and scoping | 10 | 0 |
| Cascade, layers and shorthands | 6 | 0 |
| Parsing, tokens and CSS math | 26 | 0 |
| Attributes and custom properties | 16 | 0 |
| Animations, timelines and transitions | 14 | 0 |
| Text and fonts | 13 | 0 |
| Layout, sizing and positioning | 22 | 0 |
| Container queries | 3 | 0 |
| Colors, images, SVG and shapes | 8 | 0 |
| CSSOM geometry and hidden layout | 13 | 0 |
| **Total** | **131** | **0** |

The accepted queue is fully signed. The [fix ledger](BUGFIX-COMMITS.md) retains each native/WPT commit, prerequisite and evidence boundary. Repair 120 remains held and excluded; prototypes are not accepted fixes.

## Latest verified work

- `19a313060adb`: signed computed-name research checkpoint. The integrated library passes 11,830 declaration audits, 12,424 executable cases, 170 expected-false cases and 2,153 source fingerprints. These are validation counts, not percentages of CSS coverage. The new model assumes normalized name parsing; raw CSS parsing and native correspondence remain open. [Full check](../css-variables-computed-name-library-application-v1/REPORT.md).
- `73a62b1ecf58`: signed test-only commit for real-document keyframe computation. `KeyframePresentation.LiteralOpacity` compiled and passed with a nonempty computed value and presentation teardown. Its two-file commit excludes the unfinished operation-arena registration. [Validation](../css-keyframe-presentation-calibration-validation-v1/REPORT.md).
- The operation/descriptor prototype previously passed both builds, ten native GTests and the exact browser comparison: 162 passing subtests, four retained provider failures, two passing crash tests and eleven successful harness endpoints. The retained failures still need a repair. [Comparison](../css-keyframe-operation-descriptor-capture-runtime-v1/REPORT.md).
- Both signed checkpoints preserve working source bodies and nested-library staging. The fixture build intentionally updates the two matching GTest-library copies. Its outer wrapper failed on obsolete log syntax; independent parsing confirms the actual named test passed, and the original failed wrapper remains recorded.

## Execution order

1. **Transition endpoint mutation: red/green validation complete.** The new regression produced exactly one stale-descriptor failure; clearing it preserves the full concrete replacement and passes both native tests, including explicit versus implicit underlying composition and retained ownership. The normal build and preservation checks pass. This is a prototype invariant repair, not a newly observed browser bug. The metadata test and correction remain with the uncommitted prototype. [Result](../css-keyframe-transition-green-validation-v1/REPORT.md).
2. **Complete current-provider animation resolution.** Validate compact rule ownership and host lifetime, then connect retained endpoint recipes to actual winning providers. Turn the four calibrated provider failures into passes while preserving existing controls. Cover iteration endpoints, recipe errors, animated dependency cycles, ownership and memory reporting. Do not substitute cached values when recipe evaluation fails.
3. **Resolve the contextual-integer prerequisite for the next numerical lead.** The reviewed `round()` candidate has a 38-case historical diagnostic and 14 calibrated failures, but its repair changes context-dependent `steps()` admission. Investigate existing bug 2037743 and targetless Web Animations semantics before accepting that change. Then refresh the numerical baseline and run an isolated before/after/restored comparison. Keep held repair 120 excluded. [Candidate assessment](../css-next-observable-experiment-review-v1/REPORT.md).
4. **Extend the CSS model and correspondence.** Continue versioned normative requirement mapping, custom-property dependency/completion histories, parser progress, provider ownership and fragmentation. Separate specification-model results, executable examples and native refinement. Carry explicit parser/compiler/heap/provider premises; connect proofs to actual changing implementations rather than treating historical replay as current verification. [Whole-CSS strategy](../css-whole-spec-completion-strategy-v1/README.md), [open obligations](FORMAL-CLOSURE-CHECKLIST.md).
5. **Preserve the original Bloom milestones 1–6.** Their accepted checkpoints retain their recorded selector/provider/source scope. Changed cached dispatch and broader CSS semantics need fresh correspondence arguments; historical milestone completion does not close those gaps. [Bloom continuation](CONTINUATION-20261017.md).
6. **Commit and maintain evidence as work becomes ready.** Keep each accepted native fix and WPT in one commit, with required research preceding it. Record the commit and any prerequisites in the fix ledger. Keep work local. Remove task-owned build targets only after active-process checks and retained-evidence checks establish they are no longer needed; keep the active Firefox object directory and canonical Lean build.

## Historical record

The previous 2,024-line plan is preserved verbatim in [the dated archive](PLAN-OF-RECORD-20261027-HISTORY.md). Its pending, running and signing statements describe historical checkpoints. The linked acceptance records retain their original scope; this shorter current plan does not promote them to full CSS or Stylo verification.
