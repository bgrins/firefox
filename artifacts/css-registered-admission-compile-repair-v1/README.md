# CSS-wide parser lifetime repair

The first selected-token candidate build failed with Rust E0502: the universal CSS-wide parser still borrowed substitution text when the extracted helper needed mutable computed context. Proposal v3 restores the original parser scope, dropping it before calling that helper. The cascade file is unchanged. This artifact applies exactly that single source-file change from sealed v2 to sealed v3.

The transition is derived from the reviewed source-transition-v3 implementation. DELTA.patch contains every controller change. Only the candidate-to-candidate route is enabled, and it requires the exact failed-build epoch/result, preserved terminal build evidence, absent owned build/WPT/observer process groups and uncompiled/unaccepted state. The existing 50-file ownership inventory, six unchanged collector guards, exact signing-successor chain, 140 recovery pins, full preservation checks, journal, same-inode writes and owned rollback remain.

Use the failed build directory as evidence and a fresh head-candidate label. The transition records no successful native compilation or browser acceptance. Rebuild after applying it. Machine/storage failure can still interrupt publication; inspect the journal and ownership before attempting recovery.

Static checks authenticate all packages and references, require exactly one changed native path, reject a second changed path and reject every other mode. They do not execute the live transition. Original WPT evidence remains a run of capsule v3 and must not be relabeled; a later capsule may adopt it only through explicit exact-evidence and unchanged-original-experiment checks.
