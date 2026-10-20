# Hidden measurement/query state-machine proof

Read REPORT.md and SCOPE.md before interpreting results. This is a scoped proof and source calibration for the provisional direct-item dirty mark. It is not acceptance of a complete hidden-subtree repair.

Verify the outer capsule with its externally supplied FILES pin:

```sh
python3 -I -S verify.py --manifest-sha <outer FILES sha256>
```

Replay source and kernel evidence into a fresh directory outside `capsule`:

```sh
python3 -I -S capsule/replay.py --manifest-sha a4dc6e88cf8bd4f431875a619017339a2d4ac658d0588ba3585def2d9e419c8c --out /absolute/fresh/output
```

For relocation, copy only the 30 payloads listed in `capsule/FILES.json`, plus its FILES.json and FREEZE.json. The runner rejects extra files/directories, wrong source roles, proof escapes, optimized/non-isolated Python, and output inside the capsule. The compiler and Lean executable paths/bytes are pinned in TOOLS.json; this is a local toolchain capsule, not a portable toolchain distribution. The installed standard libraries and SDK remain dependencies.

`input/source-review-FILES.json` and `source-review-FREEZE.json` are provenance records for an earlier artifact; they are not a claim that `input` contains that entire artifact. `SOURCE-PINS.json` is the exact copied-input roster.

Native executable and olean products are deleted after replay, while generated source, command records, stdout/stderr, counterexample rows and summaries remain. Development failures are retained separately.
