# Raw nested attribute partial-commit handoff

This artifact adapts the used-fallback partial-commit-v2 helper for the raw-nested three-file patch. It never stages the real index, commits, changes HEAD, edits native/WPT bodies, updates an epoch, or invokes builds/browser tests. Scratch indexes and new Git objects use disposable directories; the live object database is only a read-only alternate.

## Exact scope and prerequisite

The patch is artifacts/css-attr-raw-nested-repair-v1/fix.patch. It changes only cascade.rs, the existing attr-cycle.html (two explicitly adjudicated oracle corrections plus related comment/help link), and new attr-raw-nested-cycle.html (29 tests). Both existing paths have exact parent/preimage and candidate-head hashes. The new path must be absent from the supplied parent. All three mode/blob/path checks are explicit.

Fix137, aa3f0588538800300df20a2f7de40ce8ac2ffec1, must be an ancestor of the supplied parent. The committed custom_properties.rs helper body must match the prerequisite's head hash, and bind also checks its full working-body hash. The raw fix does not restage that helper or include the remaining cascade prototype. Removing this prerequisite is unsupported; the separate used-fallback upstream-export caveats still apply.

Historical PLAN.json is pinned to cc636a8068e3a8a49b5643d065650d675d0a4e76, with tree e6141023d899058009e122ca97dd8926a1781caf. It is not silently rebound when preceding research commits advance HEAD.

## Root-owned handoff

After research commits, generate a fresh plan using the explicit then-current parent and epoch digest:

    python3 -I -S -B artifacts/css-attr-raw-nested-partial-commit-v1/check.py prepare NEW_PLAN_DIR EXPECTED_HEAD EPOCH_PATH EXPECTED_EPOCH_SHA256

Prepare checks the full epoch before/after and authenticates the sealed proposal. It stages and reverses in scratch only. Its output contains exact tree/blob/mode/path/flag expectations and staged.patch.

Only after candidate testing succeeds, the full candidate cascade and unchanged prerequisite helper are installed, both exact WPT candidate bodies are installed, and root has extended its current epoch accordingly:

    python3 -I -S -B artifacts/css-attr-raw-nested-partial-commit-v1/check.py bind NEW_BINDING_DIR EPOCH_PATH EXPECTED_EPOCH_SHA256 PLAN_DIR

Bind checks complete candidate working bodies separately from the smaller staged blobs, all epoch pins/identities, both index states/flags, and repeated external epoch SHA. It records the exact remaining diff expected after committing these three files. It does not assume cascade.rs becomes clean. Test success must be supplied by root's actual comparison evidence; bind is not itself browser validation.

Root owns applying only the generated staged.patch with git apply --cached and making a signed commit. Never git add the complete cascade.rs. After signing:

    python3 -I -S -B artifacts/css-attr-raw-nested-partial-commit-v1/check.py verify-after BINDING_DIR PLAN_DIR

Verification requires the exact parent/tree/three paths/modes/blobs, configured-key signature verification, empty staging, expected index entries/flags, unchanged full working bodies and exact remaining diff, all preserved epoch pins/identities, and unchanged nested raw/semantic index/flags. The new WPT is under testing, outside the existing layout/dom/servo/mfbt untracked_native inventory; that field and its count remain unchanged. Real index raw bytes change during staging/signing and are not asserted equal to their pre-commit value. The verifier emits POST-EPOCH.json and RECEIPT.json; root must explicitly adopt the epoch.

## Validation performed

The final helper passed scratch forward/reverse transport, exact three-file postimage/tree checks, fix137 ancestor/helper checks, and unchanged live/nested index, flags, HEAD and working-diff checks at the historical parent. Wrong epoch SHA and wrong expected parent fail without creating output. Python syntax passes. Temporary index/object directories were removed.

No original full-current epoch validation was run; signing-v11's observed epoch SHA61d16a73c7bbd4aa4921365588b1805bb771cd7aa9a31da6b069aaf783209455 is recorded only as historical input context. Fresh prepare/bind must use the later post-candidate epoch after installation/testing. Candidate bind, post-signature verification, native build and browser execution have not been performed by this helper audit. No fix138 acceptance or new formal-coverage credit is claimed.
