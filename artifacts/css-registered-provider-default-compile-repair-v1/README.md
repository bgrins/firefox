# Provider-default compile correction

Applies exactly one changed native file from sealed repair v4 after the preserved failed v3 build. The only source delta is `drop(state)` after the final cycle check. Cascade remains unchanged. This experiment is not acceptance.

The adapter authenticates the prior installer, its recovery inventory and saved ledger preimages, the new proposal and terminal failed-build records. It binds exact source/control bytes and identities, verifies current epoch/index/flags and quiescence immediately before writing, authenticates replacement and rollback buffers, and reuses existing owned writes and rollback. Only the raw index observation may refresh after full semantic preservation checks. No tests are installed and no Git action is performed.

Root supplies the FILES.json SHA and POLICY.json epoch SHA to `python3 -I -S -B apply.py`. After successful application, root runs:

```
python3 -I -S -B artifacts/css-registered-number-native-runtime-v1/build.py provider-default-candidate-build-2
```

The existing guarded helper runs `mach build binaries -j2`. Preparation ran syntax and saved-artifact/hash checks only, not the updater, live preservation guards, compilation or browser tests. The compiler rebuild validates the lifetime correction. The CSS-rule cached-initial policy remains unresolved.
