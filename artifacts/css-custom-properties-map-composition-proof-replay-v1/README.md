# Composition replay receipts

The closed 134-input source capsule was externally authenticated, relocated by manifest and replayed from fresh outputs. The resulting 32 new and 105 inherited theorem audits passed using only permitted standard Lean axioms. Eight inherited semantic model mutants and three new compiled wiring mutants were discriminated. All native source bindings and exact final source identity checks passed.

`relocated-command.json` records the executable command and source pins. `evidence/` retains complete compile/axiom/mutation logs, definitions/drivers and CHECK/RESULT records. `authentication-challenges.json` preserves eight deliberate corruptions, each rejected before output creation. `RESULT.json` records post-replay source reauthentication. `development-evidence/` preserves intermediate compile errors and successful predecessor/full replays separately from final results.

Completed owned generated outputs were removed after evidence capture; exact removals are in `CLEANUP.json`. The relocated source capsule remains at `/private/tmp/map-composition-relocated-final-v1/capsule`. No installed Lean/toolchain or shared targets were removed. No native Rust, browser or Firefox build was executed.

`replay.py` is the exact relocation/challenge driver, called with `python3 -I -S replay.py NEW_ABSOLUTE_WORK_DIR`. It writes receipts into its own directory: copy it into a fresh sibling receipt directory before replaying; do not mutate this sealed receipt set. Ordinary independent replay should use the source capsule's checker with a fresh external output.
