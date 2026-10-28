# Untracked-file audit — 28 October 2026

At HEAD `a1f28b1578df604a67c45e2d23ab54f246941561`, all 563 non-ignored untracked paths match the prior inventory. No unexpected paths or unsaved project files were found.

| Files | Count | Disposition |
|---|---:|---|
| Project WPT experiments and validation controls | 53 | Pending/research files; exact bodies already preserved in signed recovery commit `0197d1c8e8fd` |
| Project native and gtest prototypes | 15 | Pending prototypes; exact bodies already preserved in that signed recovery commit |
| Tabcanvas dependencies and test output | 183 | Existing unrelated files, left untouched |
| Docker/dead-pref research | 286 | Existing unrelated files, left untouched |
| Other agent tooling, performance data and test output | 26 | Existing unrelated files, left untouched |
| **Total** | **563** | |

For all 68 project files, verified content hashes, lengths, modes and filesystem identities against the preceding audit, and exact bytes against committed recovery copies. Verified recovery and current HEAD signatures. For the 495 unrelated entries, compared names and recorded fresh filesystem metadata; did not read their contents or claim content equality. Nested CSS Lean has only the previously recorded untracked `.DS_Store`.

The index is empty. The sole tracked source modification is the held custom-property provider prototype, with unchanged SHA-256 `2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774`. It remains unfinished and unaccepted. Keeping its recovery copy in history does not make it an accepted native fix.

Ignored research artifacts are outside Git's ordinary untracked listing. The checkpoint separately selects newly completed sealed research packages. Build products and caches are not blanket-staged. No source, index, build or canonical runtime state was changed by this audit.
