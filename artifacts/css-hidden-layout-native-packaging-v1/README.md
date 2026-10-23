# Offline hidden-layout native packages

Source packaging only. Both recipes are deliberately unapproved drafts with an expected-head placeholder; no native acceptance or signing is authorized by this capsule. The landing decision remains in the separate unsealed decision artifact pending the current controlled experiment.

The retained base is 683bbe59d5a698a1f708041304f8640a7f987c38. Read-only git show/ls-tree established that its two native blobs exactly equal the sealed compact runtime baselines and that all five proposed WPT paths are absent. Every final mode, Git blob ID, SHA256, source role and pathname is in BINDINGS.json. The patches contain no research or unrelated native edits.

| Package | Native delta | WPT files | Total paths |
|---|---|---:|---:|
| principal.patch | One MarkPrincipalChildrenDirty call at the existing hidden ReflowChildren return |3|4|
| absolute.patch | Selected v2 hidden predicate/MarkSubtreeDirty block before ReflowInput construction |2|3|

All five WPT payloads match both the sealed landing-plan bytes and the actual compact runtime inputs. The source candidates match the corresponding independently tested principal-only and OOF-only variants. Both patches privately apply with zero fuzz, produce every expected final byte and reverse to exact original bytes/test absences. Temporary directories were removed. The two path rosters are disjoint, so their changes do not overlap; runtime independence is supplied by the separate four-variant evidence, not inferred solely from applicability.

The recipe format retains the existing local No bug message convention, with the reviewer group taken from the pinned actual Herald output in css-flex-table-caption-format-v1/reviewers.log. These are proposed local commit messages, not fabricated Bugzilla IDs or review approvals. Root must finalize metadata if a real bug is assigned, fill each expected_head from its verified preceding evidence commit, confirm final acceptance and preserve any current worktree changes when installing the exact package. No signing or Git mutation is implemented here.

References are reused instead of copying full native snapshots or bulk runtime logs. verify.py authenticates this capsule, checks each referenced final/before byte sequence and repeats only artifact-private apply/reverse. It does not inspect or change the live native tree, index or HEAD and does not run a compiler/browser/build.

Fix101 dependency guidance is separate in FIX101-LEDGER-RECOMMENDATION.md. No existing immutable acceptance report or shared ledger was changed.
