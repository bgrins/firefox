# Configured contextual easing typecheck: current binding

Enabled successor of the reviewed v1 preparation after root review. `run.py` and
`SOURCE-ROLES.json` are byte-identical. The sealed six-source candidate is
unchanged. `POLICY-DELTA.patch` contains only the current signed HEAD, canonical
epoch hash, v44 final receipt, predecessor manifest, new runtime output, and
pending-review wording.

Current binding is HEAD `5d9487828523b7086f1b425ed18caa550f8b3b61` and canonical
epoch `99d49e5263d23797041e961877e9d9ddc92bac2e51a4840efcc69bd87a52f445`.
All six source bases match that signed HEAD. All 14 current accepted bodies and
identities match their existing claims. The only permitted accepted overlay
remains specified easing (143); generic arithmetic (145), all other accepted
payloads, the held provider and the app remain preserved.

The runner composes the existing configured Gecko Rust graph's Cargo
`check --offline -j2`, reusing `objdir-full.noindex`. It references the same
unchanged 30 GiB admission/15 GiB running-stop phase helper and process cleanup.
It creates no new target directory and performs no linked browser build or
browser test. Full epoch verification remains in memory; only compact digests,
actual command/process results and exact source-restoration records are saved.

The read-only preparation check found no raw-index drift: current index bytes
match the canonical observation. Execution will independently verify again.
If the check itself later changes only the raw index while preserving semantic
state, the runner records that fact without modifying CURRENT, ROLE or OWNED;
any required refresh is a separate root-owned operation.

No source overlay, compiler, index or canonical write has been executed by this
preparation. Compilation does not establish Servo configuration support,
selected-keyframe scope transport, lifecycle correctness, browser behavior or
activation readiness. Parser guards remain closed.

Root-only invocation:
`/Users/bgrins/venvs/firefox/bin/python -I -S -B artifacts/css-contextual-easing-integration-typecheck-v2/run.py --run FILES_SHA256`.
The `--check` mode authenticates bindings without source writes or compilation.
