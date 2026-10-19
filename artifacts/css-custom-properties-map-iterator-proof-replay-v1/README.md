# Independent-location replay receipt

The final source capsule was authenticated, copied by its closed manifest to a new directory, and replayed with Python `-I -S` and the pinned Lean installation. `relocated-command.json` records the exact command and source pins; `evidence/` contains all module/audit/mutation logs and the compiled-model source used for finite discrimination. `RESULT.json` reports exit 0 and post-replay source authentication.

All 50 named theorem audits used only the standard permitted Lean axioms. Four compiled model mutants changed the expected observations; no Rust or browser was executed. Eight corrupted capsules were rejected before output creation: changed proof, changed native source, unexpected module, unexpected directory, symlink input, duplicate JSON key, unsafe manifest path and missing input. Exact errors are retained in `authentication-challenges.json`.

The first development replay's Lean source-root error is retained under `development-evidence/`; it preceded compilation. Final replay used authenticated source copies inside its fresh build directory. The source capsule is immutable; completed generated output was removed only after retaining the evidence listed in `CLEANUP.json`. The relocated source copy is retained at `/private/tmp/map-iterator-proof-relocated-final-v1/capsule`.

`replay.py NEW_ABSOLUTE_WORK_DIRECTORY` is the exact driver, invoked with `python3 -I -S`. It writes receipts in its own directory; for a fresh replay, copy this driver into a new sibling receipt directory while retaining the unchanged source capsule sibling. Do not rerun into this sealed receipt directory. The source capsule's own `check.py --output NEW_ABSOLUTE_DIRECTORY` is the ordinary review command.
