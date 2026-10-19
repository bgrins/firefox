# Working-directory audit

The v1 failure is retained at `css-hyphenation-measurement-offset-probe-v1/root-coordinate-replay-v1`: baseline/check.py passed an absolute relocated Lean source while inheriting repository cwd. Lean rejected that source before compilation.

Only the outer replay orchestration changes in v2:

- Resolve the Lean argument before changing cwd.
- Run the copied baseline checker with cwd equal to its baseline root. Its module sources, build audit files, nested consumer module sources/development-build files and generated MeasurementMachineDriver are all descendants. Nested Python scripts derive paths from __file__ and use absolute arguments. Their inherited cwd is therefore suitable, including the complete consumer and final whole-machine driver.
- Copy the authenticated guard capsule into output/guard. Run its checker under output, the common ancestor of guard/lean and guard-result audit files. This also preserves the guard checker's requirement that its output be outside its source capsule.
- Run native compiler/executables under the explicit output root. Compiler input/include/output paths are absolute and unchanged. Record cwd for each subprocess.

No nested manifests, sources, proof statements, case counts, fixtures or comparison predicates change. No generated binary is used as input. The complete root replay remains the acceptance gate. This correction is not evidence of a native or formal theorem defect.
