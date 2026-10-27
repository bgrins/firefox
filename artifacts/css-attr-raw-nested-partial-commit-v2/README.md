# Raw nested attribute partial-commit helper, version 2

This version binds the unchanged partial-commit workflow to sealed css-attr-raw-nested-repair-v2. Only four constants change: proposal directory, historical audit parent, proposal manifest SHA and new-WPT SHA. v1 remains immutable. Native postimages are identical to repair-v1; WPT bodies now include the third explicit EOF oracle correction and seven parser-boundary controls. The revised target count is73 (37 existing plus36 new), not the earlier66. This helper supplies no test acceptance.

The three staged paths remain cascade.rs, modified attr-cycle.html, and new attr-raw-nested-cycle.html. The existing fixture SHA is429713c4530a47d62d79e17b686edc4a5eae4d853f0641c94b3fe0970fa35055; new fixture SHA is e62be068c0a82b5670e99b9d31d5c2142a86d8fde843fc968c64be07b3e51a42. The unchanged staged cascade SHA is2cc7b3d4047b9759277f41809ad7ba7baef99431c26b608bcf459b2d83764656. Full working cascade body and its unrelated WIP are checked separately during bind.

Fix137 aa3f0588538800300df20a2f7de40ce8ac2ffec1 remains an explicit ancestor prerequisite. Its committed helper SHA and full working helper SHA are preserved. No helper code or unrelated prototype is added to this patch.

Historical PLAN.json is pinned to bb88e8e6b31de9b832e896110e39504d68020c71. After research commits or other parent changes, create a fresh plan using an explicit expected parent and then-current epoch digest:

    python3 -I -S -B artifacts/css-attr-raw-nested-partial-commit-v2/check.py prepare NEW_PLAN_DIR EXPECTED_HEAD EPOCH_PATH EXPECTED_EPOCH_SHA256

Only after successful new original/candidate validation and exact candidate source plus both WPT installations, with the root epoch extended to those bodies:

    python3 -I -S -B artifacts/css-attr-raw-nested-partial-commit-v2/check.py bind NEW_BINDING_DIR EPOCH_PATH EXPECTED_EPOCH_SHA256 PLAN_DIR

Root owns live staging/signing using only the generated staged.patch. Do not git add the complete cascade file. Afterwards:

    python3 -I -S -B artifacts/css-attr-raw-nested-partial-commit-v2/check.py verify-after BINDING_DIR PLAN_DIR

The inherited checks require the exact parent/tree/path/mode/blob set and configured-key signature, all full working bodies and epoch pins/identities, exact remaining diff, real index flags/entries, and unchanged nested raw/semantic index and flags. Root explicitly adopts the emitted verified post-commit epoch. No canonical epoch is updated automatically. The existing restricted untracked_native inventory excludes testing paths and remains unchanged.

The scratch audit passed against the historical parent: exact forward/reverse patch transport, unchanged live HEAD/index/flags/working diff and nested state, expected three-file tree/blobs, and fix137 ancestry/helper checks. Python syntax passes. Git apply --cached and write-tree created objects only in a disposable private object database, with the live database as read-only alternate; the scratch index/object directory was removed. This audit ran no full-current epoch validation or candidate bind, and made no live source/index/HEAD/epoch changes or signature operation.

The earlier candidate failure remains a failed66-target comparison. These revised fixture pins cannot relabel it as passing; a fresh73-target comparison is required. No fix138 acceptance, new bug count or formal-coverage increment is claimed.
