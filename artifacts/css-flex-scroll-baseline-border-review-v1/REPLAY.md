# Replay

Run `python3 verify_artifact.py` in this directory for a read-only complete seal and nested input check. Compare the supplied external FILES/FREEZE pins as well.

To replay compiler work, copy only `check_native.py`, `verify_inputs.py`, `PROVIDERS.json`, `facade.hpp`, `main.cpp`, `Kernel.lean` and `inputs/` to a fresh directory outside this sealed artifact. Run `python3 check_native.py` there. It authenticates inputs, compiles exact source variants/mutants and compares with the independent oracle. It removes each owned executable after its terminal result. Run the Lean executable recorded in TOOLCHAIN.json on Kernel.lean and require exactly12 standard-axiom audits, no errors and no sorry/custom axioms. The final source-only replay matched22 native streams.

`check_evidence.py` may be copied with the same inputs into a fresh directory under the checkout to repeat raw-log recount and patch apply/reverse against the retained Git objects. It writes its own receipt and removes its disposable patch directories. No browser or build is required. These scripts produce outputs and should not be run directly in the sealed artifact.

The initial failed kernel log and false/custom-axiom controls are expected negative evidence, not successful results. Full formal producer acceptance is outside this native-review seal.
