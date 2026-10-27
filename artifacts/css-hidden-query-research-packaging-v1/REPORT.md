# Hidden-query research packaging inventory

This is a read-only packaging audit, not native acceptance or a commit recipe. No index, HEAD, native source, browser, or build was changed. Inventory HEAD was `90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e`, and the narrowly inspected tracked artifact files had no staged or unstaged changes.

## Suggested evidence commits

| Order/group | Directories | Files | Bytes |
| --- | ---: | ---: | ---: |
| 1. Shared boundary evidence | 14 | 925 | 70,181,348 |
| 2. Grid source and disabled draft | 6 | 143 | 6,237,916 |
| 3. Final landing inputs | 4 | 29 | 314,002 |
| Separate float follow-up | 9 | 247 | 6,561,479 |

`GROUPS.json` gives the exact directory membership. `SAFE-PATHS.json` gives all **1,344 explicit files**, their sizes and SHA-256 values: **83,294,745 bytes**. Use this file roster rather than recursively staging the directories. These files were untracked at inventory time. This inventory's own files can accompany the management/evidence commit separately.

The shared group preserves the failed fragment-calibration campaign and its corrected successor, source-only identity trace, fixture checks, cost evidence, guard correction, and independent reviews. Do not discard failed historical evidence merely because the corrected campaign passed its intended gates. Its size is chiefly retained raw runtime/build evidence, not compiler products.

Grid's older indexed-source discovery is retained beside the corrected actual-HEAD source binding. `css-hidden-grid-runtime-v1` is a closed **disabled, unprepared source draft**, authenticated by `DRAFT-FILES.json`, not a completed runtime capsule. Its source-only files are safe to retain; no isolated Grid execution is claimed. The active combined landing experiment will supply the new runtime evidence later.

Final landing inputs include the cleaned actual WPT bytes, driver review, historical before-run readiness snapshot, and private worktree-overlay apply/reverse evidence. Readiness's frozen status intentionally predates execution. The overlay demonstrates how the same native hunk applies to selected HEAD and preserved worktree roles; only the block role retains unrelated prototype differences. It does not establish browser equivalence of those roles.

Float evidence is separate research, not a prerequisite or acceptance claim for column/block/Grid.

## Dependency and evidence audit

`INVENTORY.json` records 62 scoped directories and the narrow read-only Git commands. **56 FILES manifests** were validated against all payload hashes and complete regular-file rosters. One additional disabled Grid draft uses its previously checked closed draft roster. `TRACKED-DEPENDENCIES.json` identifies 24 already tracked dependency directories; do not duplicate them in new evidence commits. No compiler product candidates were found in the inventoried paths. Hash validation establishes identity and packaging completeness, not semantic correctness.

The existing column provider proof, skipped-line proof and provider-path proof remain conditional local components. Grid reuses the exact existing Hidden/Subtree helper model and its tracked independent review; this inventory does not invent a new Grid theorem or replay. Actual source-role differences remain documented in Grid source-binding-v2.

The completed boundary-v2 campaign preserves seven equal 100-case rosters: 64/36 baseline, 76/24 column, 78/22 block, 98/2 both, and 37/63, 45/55, 51/49 in the three standalone controls. Each pair is PASS/FAIL. The remaining two main-both failures are float follow-ups. Standalone controls remove 104/105 while retaining 101; they are not a full upstream runtime. Historical restoration, source pins and empty-index observations are evidence for that run, not an assertion about a later live worktree.

Its cost records preserve baseline recovery errors, require correct hot-loop geometry, and compare unequal useful recovery work. They are not broad performance acceptance. The final cleaned landing WPT files differ from research inputs and require their own actual-file execution; the 100-case campaign is not a substitute.

## Holds

`HOLDS.json` excludes five unsealed or active directories:

- `css-hidden-query-landing-runtime-v1`: active 79-case campaign; no final roster or restoration acceptance yet.
- `css-hidden-query-landing-review-v1`: ongoing loose review.
- `css-hidden-query-commit-preparation-v1`: root-owned commands/logs; later receipt commit.
- `css-hidden-query-checkpoint-commits-v1`: mixed already tracked and loose management files; new files need separate finalization.
- `css-hidden-query-boundaries-draft-revision-v1`: unsealed historical metadata. Sealed revision-v2 retains the corrected transition evidence; this inventory does not delete or silently stage revision-v1.

Active-path counts in the inventory are historical snapshots and must not be used as final runtime rosters. After the 79-case run restores and seals, add its runtime/review to a new explicit landing-results group, then recheck hashes before staging. No active files are included in `SAFE-PATHS.json`.

## Authentication notes

The externally supplied worktree-overlay FILES pin is `88291d7b720f4086bddc4c2789020767ea3913cf9ae9dd4d04c7e69abeb81fc1`; readiness is `519954025fb2da6a9ec361278dc04084ef2a4173657b774179230f300b64005d`. Both match. The first extension of the inventory validator rejected an older manifest's `{sha256, bytes}` row format; support for that existing format was added, after which all 56 manifests passed. A report-generation variable typo failed before writes and was corrected. No producer files changed during either correction.
