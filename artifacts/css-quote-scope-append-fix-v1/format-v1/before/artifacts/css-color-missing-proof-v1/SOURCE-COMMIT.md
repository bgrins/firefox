# Source-only companion

Commit these files, before the native fix:

- Missing.lean
- README.md
- REVIEW.md
- SOURCE-COMMIT.md
- SOURCE-v1.json
- SPEC-v1.json
- interpolation-missing.html
- check.py
- controls.py
- source_check.py
- materialize.py
- freeze.py

Do not commit generated native snapshots, Lean compiler outputs, executable
binaries, probe profiles, discovery runs, gate logs or frozen execution capsules.
The latter remain local evidence. The source files and pinned parent revision
are sufficient to reconstruct the two native snapshots per file and replay the
proof in source-only mode. The Lean executable is an external prerequisite at
the versioned path specified in check.py.

Run from any directory:

    python3 artifacts/css-color-missing-proof-v1/materialize.py
    python3 artifacts/css-color-missing-proof-v1/check.py /tmp/color-mask-check --snapshots-only

Choose a new output directory. After the native fix is applied, omit
`--snapshots-only` to additionally authenticate the current native source.
