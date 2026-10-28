# Provider candidate comparison with preserved staging

This observer reuses the exact 775 assertions and six reftests from the completed expanded accepted-build baseline. It binds the actual successful provider-default-candidate-build-2 and the unaccepted v4 source bodies. It does not change or rebuild the browser.

The first research commit is staged after two 1Password failures. STAGING.json records that exact artifact-only patch, its payloads and index. OBSERVATION-EPOCH.json differs from the real saved build epoch only in the recorded Git index state and staged payload map. bindings.py verifies that complete delta; epoch.py preserves every original state check and replaces the empty-index requirement with exact staging checks. The saved build epoch, runtime epoch, native sources, binaries, metadata and accepted zoom repair are unchanged. There is no signing process running during observation.

Full assertion messages must be compared, particularly the conditional color-context controls. Same FAIL status does not establish unchanged behavior. Completion of this observer does not accept the native fix.
