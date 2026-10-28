# Staged runtime epoch adoption

adopt.py changes only runtime CURRENT-EPOCH.json from the historical empty-staging build2 record (32282c6b…) to the authenticated staged observation record (ca834209…). The source bytes, binaries, HEAD, exact 36-file signing patch, root/nested index, flags, ownership records and accepted zoom overlay remain unchanged. No native v5 source transition is included.

The helper authenticates the sealed observation capsule, derivation, signing-patch bytes, terminal build/browser evidence and referenced helpers before mutation. It uses the existing full staged verifier, claims regular control-file ownership, requires an absent provider-staging-adoption-1 output and SOURCE-TRANSITION.lock, rechecks controls and quiescence immediately before writing, then verifies full preservation again. Failure attempts an ownership-checked restoration of the original CURRENT-EPOCH bytes and verifies the still-staged workspace against its truthful observation record. ROLE and OWNED are never written. An incomplete rollback reports manual_recovery_required.

The output contains exact original CURRENT/ROLE/OWNED bodies and pre/post state. Its successful receipt establishes metadata adoption only, without changing compilation or native acceptance. Adoption is enabled after root and independent review; root owns execution. The build adapter remains disabled.

## Build adapter status

build.py is a separately disabled prepared adapter. It reuses the existing runtime state, phase.py and process cleanup, changing the epoch verifier to the reviewed staged guard and using ownership-checked control publication. It requires a new absent provider-default-candidate-build-3 directory, a sealed v5 transition's exact epoch/variant/source pins, and unchanged staged semantics through the build. The original build command, disk thresholds, timeout and four binary refresh paths remain intact.

No v5 transition exists in this package. BUILD-POLICY.json intentionally has no source pins or epoch and execution_enabled=false. This build draft has syntax review only; it is not execution-ready or approved by adoption review. A new reviewed successor must bind actual v5 inputs and complete build-specific preservation/publication review before activation. No shared runtime state.py/build.py is modified.

## Future signing contract

The v26 resume-first.py, finish.py and synchronize.py remain historical and must not run unchanged after adoption or native iteration. They assume the old runtime 32282/v4 signing capture. A later signing continuation must authenticate the exact untouched 36-file staged patch/tree/message against the then-current source/build epoch, resume that commit without restaging, verify its signature/tree, and only then derive empty staging while preserving actual current native/binary/ownership pins. It must retain the old failed-signing logs and historical v4 evidence. No signature is attempted here.

Validation: check_adoption.py checks the saved original/observation derivation with a matching role fixture and rejects 28 altered inputs/output paths. Owned scratch verifies same-inode epoch write/restoration and is removed. No main, live staged guard, Git mutation, browser or build was executed by this artifact's author.

Observer capsules that pin runtime CURRENT-EPOCH to 32282 become historical after adoption, even though browser/source bodies are unchanged. Root will finish the planned eight-assertion v4 observation before running adoption. That unfinished run is deliberately not added to the completed-observer list; root must confirm its terminal cleanup before launch.
