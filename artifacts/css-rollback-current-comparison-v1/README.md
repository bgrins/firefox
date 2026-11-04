# Current-stack rollback comparison

The two-source A+B+D candidate repaired all six reproduced failures without losing any of the 74 prior passes. The four existing regression-control pages retained five passing callbacks, two exact known cycle failures, three successful testharness completions and one passing crashtest. This is a local comparison on the current project branch, with revert-rule explicitly enabled, not an isolated upstream or release-default test.

| Evidence | Baseline | Candidate |
|---|---|---|
| Primary A16+B16+D48 | 74 PASS / 6 FAIL, 3 OK | 80 PASS, 3 OK |
| Existing controls | 5 PASS / 2 known FAIL, 3 OK, 1 crashtest PASS | Identical statuses and failure messages |
| Supplemental raw-event audit | Passed | Passed |

Baseline output: ../css-rollback-local-baseline-runtime-v1. Candidate output: ../css-rollback-local-native-runtime-v1. Exact callback comparison: ../css-rollback-local-native-runtime-v1/COMPARISON.json. Control baseline: ../css-rollback-controls-baseline-runtime-v1. The original per-callback messages and raw logs are retained; failures in the primary pages were unannotated. Only the separate cycle controls carry explicit historical expected-failure metadata.

The native owner f447ff/session38186 closed at 3e06a3 with exit zero. Its native build succeeded, the two browser suites completed, and its restoration checks passed. The owner removed the verified 1,008,634,455-byte backup. Independent restoration acceptance is recorded separately under ../css-rollback-restoration-audit-v1.

Only applicable_declarations.rs and properties/cascade.rs were changed for the candidate. stylist.rs remained pinned unchanged, excluding the held C identity repair. Both roles retain the same separate three-file empty ArcSlice library patch and use HEAD a6f39620516a4cf76a5dbf5208960adc79068cf1. Native sources and installed application were restored after the experiment; the candidate is retained under ../css-rollback-cutoff-e86-rebase-v1.

The six failed callbacks represent the existing A/B defects and D preservation coverage, not six new bugs. No new fix commit or catalogue increment is claimed. The cumulative state preserves Origin, ordinary Layer, and important-inline Layer exclusions. Rule rollback preserves these bounds; it does not add the separate same-rule identity repair. The two cycle failures and their specification question remain outside this repair.

Commit-boundary review recommends one coherent A+B+D production unit because the tested behavior couples the predicate correction and cumulative state. Earlier partial repairs regressed one another. This does not establish that no alternative split exists; independently landable subpatches would need their own matched comparisons. Research and tooling must precede the minimal fix-and-three-WPT unit. See ../css-rollback-commit-boundary-review-v1/README.md.

Formal results remain conditional on the supplied priority mapping and accepted consumer events. Complete native refinement, provider/substitution correctness, whole-cascade behavior and cycle resolution are not proved by these tests or the cutoff model.

Independent restoration audit f30b09/session28561/19dfb4 exited zero and verified the restored source identities, library/context preservation, Git state, 9,378 application entries, three extra files and absence of all four owned process groups. Root read the audit result. The completed consumer bridge was kernel-checked and its eight artifact payloads and import hashes authenticated; see ../css-rollback-native-consumer-bridge-lean-v1.
