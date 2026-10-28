# Directly referenced Round history inventory

Only Round capsule directories directly referenced by `css-round-numerical-prior-art-reconciliation-v1/REFERENCES.json` and `css-round-special-knowledge-repair-v3/REFERENCES.json` were read: **15 capsules, 205 manifest-listed plain files**. All referenced hashes and local manifest payloads authenticate.

At signed HEAD `995e0d2df8d7439fbd1a38f6d6fc46af247034e1`:

| State | Files |
| --- | ---: |
| Exact current path and body already committed | 31 |
| Body committed under another path only | 18 |
| Already selected by the current v40 preparation | 15 |
| Body absent from the signed HEAD tree | 141 |

`RESTORE-PRESENT-PATHS.json` supplies **159 exact path→SHA256 pins**, approximately 1.43 MB, for the small historical source/report/proof/evidence bundles still absent at their referenced locations. It includes the 18 alias-only bodies so those original references become reproducible. `GENUINELY-ABSENT.json` is the 141-body subset. No binaries, build products, caches or symlinks were found among these manifest entries; nothing outside this bounded capsule set was read for content.

Alias discovery compared locally calculated Git blob IDs with signed HEAD tree metadata. The initial artifact-tree-only check found 142 absent bodies; a full-tree metadata crosscheck found one additional exact alias outside artifacts, correcting the final count to 141. No unrelated tree bodies were read. The full inventory records matching alias paths, exact hashes, sizes and manifest pins. It does not traverse references recursively or claim an exhaustive audit of every historical ignored artifact.

Checks: 6b6158/0 authenticated the bounded capsule payloads and selected-set exclusion; 6e9fb8/0 completed the metadata-only full-HEAD alias crosscheck. The signed current HEAD was independently verified by the immediately preceding untracked audit. This artifact writes only its own inventory and report. No source, index, staged selection, canonical ledger or runtime was modified. The signer owns inclusion and commits.
