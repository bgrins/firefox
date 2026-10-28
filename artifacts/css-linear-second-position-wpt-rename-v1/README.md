# Exact test-path relocation

Root-only transaction: rename the untracked, owned linear-contextual-second-position-crash.html to linear-contextual-second-position.html with identical bytes and inode. The old suffix is reserved for WPT crashtests, so the testharness page must use the corrected landing name. Historical paired fixtures and their explicitly assembled manifests stay immutable; they are not evidence of natural WPT classification. The final runner must round-trip the renamed page through the real parser and execute it.

Only the pins and installed_identities keys move in the canonical epoch, with any separately recorded raw-index observation refresh; counts, compiled source/binaries, accepted overlays and provider remain unchanged. OWNED moves the same claim and updates its path. ROLE stays byte-identical. The actual promoted build remains recorded under its pre-rename epoch; no rebuild or forged build receipt occurs.

Exclusive hard-link creation followed by unlink preserves the inode and refuses an existing destination. Both steps run with interrupt signals blocked. Rollback restores the old name and exact OWNED bytes, then fully verifies the restored epoch and nested/index flags. A failed recovery retains the lock. No main was executed during preparation. Failed lint records remain intact.
