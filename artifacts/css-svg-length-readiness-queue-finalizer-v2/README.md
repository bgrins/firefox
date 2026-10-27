Inert finalizer for expanded114 queue-v3. It is not run during the live comparison and contains no guessed acceptance, installation, binary or review pins. It never stages, signs, builds, launches a browser, or writes native files. It reads the five live patch bodies only when root invokes it after successful installed25 validation and final review.

Use python3 -I -S finalize.py with each required option supplying an artifact-relative path and full SHA256:

- --comparison FILES.json SHA
- --results-review FILES.json SHA
- --acceptance FILES.json SHA
- --installation FILES.json SHA
- --installation-review FILES.json SHA
- --updater DRAFT-FILES.json SHA (the reviewed bound installer, same driver as installed runtime)
- --updater-review FILES.json SHA (must contain the full updater-manifest hash)
- --preflight ROOT-PREFLIGHT.json SHA (actual root preflight record; path is explicit)

It authenticates every supplied capsule payload, the frozen438-file selection and five-path patch. Review capsules must contain the complete corresponding target manifest hashes. Expected acceptance/root schemas are the existing SCOPED_ACCEPTED, RESTORED_VERIFIED and INSTALLED_VERIFIED forms; differing future schemas fail rather than being silently inferred. Successful terminal comparison/restoration, exact51 raw identities and16 failure-to-pass repairs, installed25 raw identities and3OK, build/lint success, source/index/old-test preservation receipts, and five exact live native/WPT hashes are mandatory. Runtime control/fault proofs remain supported by the authenticated independent reviews and root receipts; this packaging tool does not rerun the browser or duplicate the complete runtime verifier.

Only after validation does it create artifacts/css-svg-length-conversion-commit-queue-v3, which must be absent. Old queues/draft remain unchanged. Research438 is preserved and actual final capsule records, raw outcomes, cleanup, build logs and updater evidence are added. Saved source/input snapshots and profile directories are omitted with explicit hashes/reasons. Manifests and direct unselected references are disclosed without claiming recursive closure. Earlier omission/external disclosures remain applicable. Existing model/native correspondence and final proof logs are already in the438-file selection. No Q/115 or zero-axis research is newly selected.

Both signed expected_head fields remain null, ready_for_execution remains false, and only signed-parent prerequisites remain pending. The exact native commit stays five paths (two Gecko plus three WPT files), patch95d01b…. The finalizer source was syntax checked only; future-result gates have not been executed. If final schema/path requirements differ, review a successor rather than modify this sealed tool or fabricate inputs.

V2 adds repeatable --research-extra MANIFEST SHA256. Each explicit extra capsule is fully authenticated and selected using the same saved-source/input/profile omission rule; direct unselected references remain disclosed. Root should supply the actual restoration checker, installation checker, root phase replay, installation preflight and selection review capsules. The finalizer's own sealed capsule, including its source, is selected automatically so this verification tooling precedes the native commit. This is explicit selection, not recursive closure. All earlier acceptance/runtime/live-body/signing-parent gates are unchanged. V1 remains immutable.
