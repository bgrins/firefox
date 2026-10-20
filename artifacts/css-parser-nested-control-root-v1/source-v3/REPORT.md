# Nested parser control checkpoint v3

Producer correction checkpoint; independent acceptance remains with the parent reviewer. V1 is retained as historical evidence and is not accepted: review demonstrated local json.py execution before the unsupported-mode guard. V2 moved the explicit mode guard immediately after builtin import sys in all three runnable entrypoints. Independent review additionally identified v1/v2 roster gaps: nested seal basenames, empty directories and nonregular entries could evade enumeration. V3 retains the pre-import guards and uses a recursive lstat roster with exact root seal exceptions, inferred expected directories, no symlink traversal, and no nonregular entries. It reauthenticates after replay. Mathematical and native inputs are unchanged; V1-TRANSFER.json and V2-TRANSFER.json record the exact deltas. V1 and V2 remain historical, unaccepted capsules.

## Results

- 39 new theorem declarations cover raw recovery, pending-none safety, nested and until-before control, program composition and six concrete LinkParameters empty-value paths. The audit permits only Lean's standard propext/Classical.choice/Quot.sound axioms; no sorry or native-decide axiom.
- Initial calibration: 16 cases and 79 snapshots matched the Lean driver and exact full cssparser debug/release execution. Three compiled native mutants changed 10, 25 and 3 snapshots respectively.
- Final preflight: 18 cases / 91 snapshots agree in Lean, native debug and native release. All 59 Lean modules compile; all 39 audits use only the permitted standard axioms. Three compiled native mutants change 10/25/5 rows; three Lean mutations are rejected by failed proofs. Two added callback-after-read cases distinguish Consume from Stop with a pending function block. Exact receipts are in evidence/final-preflight. A final checker gate additionally rejects model stderr; the passing preflight model emitted no stderr. Fresh sealed replay is retained separately.
- No new production defect found. No production edits, browser runs, Firefox builds or Git operations.

## Interpretation

The model computes raw token reads, nesting-stack recovery, cache effects, observer transitions and comment-directive writes. It does not assume an observer trace. Native compiler tests use the full retained cssparser; the LinkParameters callback is a source-derived empty-value projection, not compiled full Stylo.

SOURCE-CONTRACT.md distinguishes general conditional model theorems, finite kernel-checked paths, source-reviewed grammar/provider bridges and native calibration. parse_until_after, universal LinkParameters grammar/loop termination, all lexical families, full declaration scanning and security provenance remain open.

## Replay

Authenticate FILES.json and FREEZE.json externally, then run:

```
python3 -I -S check.py --output /absolute/new/output-directory
```

The output must be outside this capsule and absent. The checker validates every retained input and toolchain before compilation, compiles the Lean closure, audits the 39 named theorems, compares native debug/release states, and challenges three native plus three Lean mutations. It rejects Python optimization mode before output creation or producer-code dispatch. Retained compiler versions and paths are in TOOLCHAIN.json.
