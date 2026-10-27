# Partial native fix commit handoff

This helper stages only repair-v3's two Rust-file delta and exact 34-case WPT in a disposable index. It never writes the real index, creates a commit, changes HEAD, edits native files, invokes a build/browser, or updates the root epoch. Scratch Git objects also live in a disposable object directory; the live object database is only a read-only alternate. Scratch indexes start as exact real-index copies so index flags are preserved.

## Why the v10 condition is wrong here

The signed v10 helper requires each touched previously modified native path to disappear from modified_native_paths. Both Rust files still contain unrelated work after this fix is committed, so that equality rejects a correct partial commit. It also equates each staged blob with the complete working file, which would incorrectly stage the animation prototype.

This helper distinguishes committed preimages, staged postimages, and complete working bodies. It checks exact parent, tree, three-path set, modes, blob IDs and SHA-256 digests. After the candidate is installed, bind records the exact remaining diff against the proposed index and preserves all epoch pins, modified native bodies, the fixture, installed identities, and nested state. Post-commit verification requires that exact remaining diff; neither Rust path needs to become clean.

## Historical audit and fresh preparation

PLAN.json and AUDIT.json are historical, pinned to 4ebfb9861c95d33290f5fb472fddd78de241d043. Their expected tree is d63c4dde4fd7c96dc0e211d5501911c65d1d3b65. They are not automatically rebound if research commits advance HEAD. The helper rejects staging dirt.

After committing research/tooling, the root agent supplies a fresh expected parent and exact current epoch digest:

    python3 -I -S -B artifacts/css-attr-non-type-fallback-partial-commit-v1/check.py prepare NEW_PLAN_DIR EXPECTED_HEAD EPOCH_PATH EXPECTED_EPOCH_SHA256

This validates the entire epoch before/after; authenticates repair-v3; checks the two native HEAD bodies against its original base-head hashes; requires the new WPT absent from HEAD; stages/checks/reverses only in scratch; and creates a new PLAN.json, staged.patch, and AUDIT.json. It does not infer an acceptable parent from HEAD. Output directories must be new. The research-only parent can differ while the native preimages remain exact.

## Binding and signing handoff

Run bind only after the exact candidate native sources and exact WPT are installed, the intended local tests have passed, and the root's candidate epoch includes the resulting source/binary state:

    python3 -I -S -B artifacts/css-attr-non-type-fallback-partial-commit-v1/check.py bind NEW_BINDING_DIR EPOCH_PATH EXPECTED_EPOCH_SHA256 PLAN_DIR

Bind requires the full candidate-live hashes, not the smaller candidate-head blobs. It saves EPOCH.json byte-for-byte, remaining.patch, and BINDING.json in the new output directory. This operation still changes no live Git state. Bind is not proof that tests passed; root must separately attach the actual original/candidate results.

Root then owns the live staging/signing transaction: apply only PLAN_DIR/staged.patch with git apply --cached (check first), verify staging against that plan, and make one signed commit using the existing signing workflow and reviewed commit message. Do not git add the whole Rust files or reuse the old v10 partial-path assertion. Do not change source/binary bodies between binding and verification. On a staging/signing failure, inspect the existing staged state; do not silently reset it.

After the commit:

    python3 -I -S -B artifacts/css-attr-non-type-fallback-partial-commit-v1/check.py verify-after BINDING_DIR PLAN_DIR

The verifier requires exactly one parent equal to the supplied plan parent; exact tree/path/mode/blob contents; successful verify-commit against the pinned existing allowed-signers file; empty staging and expected complete index entries/flags; unchanged nested raw and semantic index/flags; unchanged working bodies; exact remaining diff; and all prior epoch pins/identities. It writes POST-EPOCH.json and RECEIPT.json into the binding directory. Root must deliberately adopt the verified epoch; no canonical epoch is overwritten. Real-index raw bytes necessarily change across staging/commit; exact raw equality is required only within read-only preparation and for the nested index throughout.

## Packaging limits

Only two Rust paths plus the WPT belong in the fix commit. This research helper must precede it. The repair uses ParsedNamespace directly and supplies the complete shared numeric primitive. The branch substitution context already contains correction 499c0c6; its literal patch is not asserted to apply unchanged upstream. The separately sealed upstream-self-contained.patch at artifacts/css-attr-non-type-fallback-upstream-v1 contains the same native behavior and exact WPT, with numeric overlap documented. It has only transport/syntax validation, not an upstream build/browser result. No old numeric bugfix is squashed or relabeled as a new discovery.

## Checks actually run

The historical staged plan passed forward/reverse transport and exact three-blob/tree checks; live HEAD/index/diff and nested state/flags were unchanged. Fresh explicit-parent/epoch preparation passed full signed-v10 epoch preservation and produced the identical historical plan. Wrong epoch digest and wrong expected parent both failed before creating output. Final Python syntax passed. A final repeated epoch-file hash assertion was added after the successful fresh-prepare process had loaded its code; the negative checks exercised the final source. Bind and verify-after have not been exercised against a candidate or signed commit yet. There was no live staging or signature operation in this audit.
