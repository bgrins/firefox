# Current local baseline review

Independent replay `c8db6d/0` authenticates both complete runtime inventories, their exact capsule manifests, and the saved assessor publications. `replay.py` reads saved evidence only; it performs no live guard, process query, browser execution, or canonical-state operation.

| Local Firefox 160 baseline | Result | Meaning |
|---|---|---|
| Numeric, 24 tests / 72 snapshots | 16 PASS, 8 FAIL | Only the relative-leaf step at font size zero differs. Literal NaN and fixed finite steps pass. |
| Admission, 8 tests / 32 snapshots | 8 PASS | All constant-result declarations remain admitted and compute like their literal controls. |

Both exact rosters and their single OK test ending are checked through the original assessments. Numeric raw test statuses are additionally joined to all three recorded snapshots per test. Admission raw statuses are joined to support, assigned serialization, and literal/computed equality. Direct calibrations pass. The four direct contextual easing categories—steps, cubic-bezier, linear output, and linear second position—reject; those are diagnostic baseline observations, not failures of the eight constant-result tests.

PRE and POST match exactly for protected source/app/configuration identities and contents, canonical control hashes, and root/nested Git snapshots. Expected policy pins match PRE. Root-terminal receipts join the saved RESULT digests and successful wrapper exits. Cleanup reports both owned groups absent and temporary directories removed. Each runtime's sole `tests/tools` symlink is checked by exact path/target without following it; there is no broad inventory exclusion.

The local NaN PASS results supersede any inference that the isolated generic shortcut necessarily produces an observable NaN failure on this branch. System Firefox 158 did fail those cases, but it is a different browser. The earlier source review did not establish the complete reachable parsing path for that local prediction. Its known-information requirement and the independently observed relative-leaf failure remain relevant.

The proposed canonical-step guard is still uncompiled and unexecuted. Its predicted effect on easing admission is not an observed regression. No native fix is accepted, no count changes, and no additional formal coverage is claimed. This package keeps references to the saved evidence instead of duplicating state records.

Reproduce with `python3 -I -S -B artifacts/css-round-infinite-value-local-baseline-review-v1/replay.py`.
