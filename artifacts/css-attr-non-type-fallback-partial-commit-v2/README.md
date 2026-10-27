# Partial commit binding consistency follow-up

The only executable change from partial-commit-v1 is a second SHA-256 check of the external epoch file immediately after bind's second full-current verification. Bind already copies the initially authenticated epoch bytes into its output. This extra check refuses to emit a binding if the caller's epoch file changed during the operation, matching the prepare command's check. It does not provide a filesystem lock or claim immunity to changes after the final check.

No untracked-inventory bug was found. verify_current explicitly enumerates only layout, dom, servo, and mfbt. The new fixture is under testing and is outside that existing field. Therefore committing it does not change untracked_native or its count under the current schema. This version preserves that scope and does not remove any untracked entries. The fixture body is independently required by bind, preserved in BINDING.json's working pins, and verified by exact post-commit blob/path/tree checks plus unchanged working-body checks. The candidate root epoch may additionally pin its bytes without adding it to the restricted untracked_native inventory.

Use the same commands as v1, with the new helper path:

    python3 -I -S -B artifacts/css-attr-non-type-fallback-partial-commit-v2/check.py prepare NEW_PLAN_DIR EXPECTED_HEAD EPOCH_PATH EXPECTED_EPOCH_SHA256
    python3 -I -S -B artifacts/css-attr-non-type-fallback-partial-commit-v2/check.py bind NEW_BINDING_DIR EPOCH_PATH EXPECTED_EPOCH_SHA256 PLAN_DIR
    python3 -I -S -B artifacts/css-attr-non-type-fallback-partial-commit-v2/check.py verify-after BINDING_DIR PLAN_DIR

The root owns live staging, signing, and epoch adoption. Future preparation/binding must use the then-current post-build native-runtime-v2 epoch and explicit parent. Historical v1 plans remain immutable, pinned to their original parent; they are not automatically rebound. The v1 README describes the full transaction and preservation checks.

Validation here is limited to exact one-line delta inspection and Python syntax. No full-current original-epoch validation, candidate bind, native build, browser run, live Git mutation, or signature operation was performed. Historical transport and full-epoch preparation evidence belongs to v1 and is not claimed as execution of v2.
