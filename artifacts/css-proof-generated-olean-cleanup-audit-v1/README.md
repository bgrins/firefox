# Generated Lean output cleanup audit

The exact 178 `.olean` files listed in AUDIT.json are small cleanup candidates. They occupy 74,206,032 logical bytes and 74,559,488 allocated bytes (about 71.1 MiB). No deletion was performed.

Each file has a SHA-256, byte count, filesystem identity, and exactly one preserved matching module source with its own hash. Both containing directories have zero Git-tracked files and are ignored; the read-only commands and outputs are retained. The six `.lean` files inside the language output directory are excluded and must remain.

The retained `css-hyphenation-ownership-proof-v1/check-lean-filter-development.py` demonstrates the pinned Lean compiler's `-o` regeneration route. This audit does not recompile modules or establish byte-for-byte rebuild equivalence. Removing outputs requires rebuilding them before historical local replay. Keep source, logs, manifests, compiler, dependency caches, and all other files.

A successful point-in-time `lsof` scan found no open paths in either candidate directory. The earlier `ps` check was sandbox-denied. Recheck consumers and exact file hashes/identities immediately before any deletion; do not delete either containing directory recursively. APFS sharing can reduce actual reclaimed space. This housekeeping does not supply the headroom needed for the native retry.

The larger development-build and Creusot trees mix archived proof/session evidence with generated content, so no wholesale disposal boundary was approved. Aeneas toolchain and dependency caches are excluded.
