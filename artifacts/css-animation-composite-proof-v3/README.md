# Composite-only keyframe updates

Formal and extracted-native companion for adding `mComposite` to `KeyframesEqualIgnoringComputedOffsets`. This artifact does not contain a production or WPT edit.

Read [REPORT.md](REPORT.md), [BRIDGE.md](BRIDGE.md), the approved [SCOPE.md](SCOPE.md) and [scope clarification](SCOPE-ADDENDUM-v1.md), and [v3 correction boundary](SCOPE-CORRECTIONS-v3.md). `FREEZE.json` supplies externally checkable hashes. `replay-v3/replay/RESULT.json` and `replay-v3/replay/RECEIPTS.json` are the canonical replay receipts.

## Replay

Use the manifest and checker hashes in the externally supplied freeze receipt. Verify the checker hash before executing it. Then run:

```
python3 -I -S -B check.py --manifest-sha <external INPUTS.json SHA-256> --output /private/tmp/animation-composite-fresh-replay
```

The output directory must not exist. The checker authenticates every source, adapter, proof, oracle, corpus and specification input before importing project modules. It verifies the pinned Lean/compiler/SDK settings, rebuilds all native variants, runs the Lean kernel/axiom audit, compares complete native observations, executes 20 semantic mutants and records bounded costs. Existing executables are never reused. No Firefox build, browser, network or Git operation is part of replay.

The toolchain paths in `TOOLCHAIN.json` refer to this workstation. The compiler executable and SDK settings are pinned; the entire compiler, SDK and Lean library installation is not claimed to be hermetic.

`development/` contains exploratory failures and superseded receipts and is excluded from the freeze. Only `replay-v3/` is canonical. The source capsule contains only authenticated inputs; output trees are never placed on its import path.

[READINESS-BRIDGE.md](READINESS-BRIDGE.md) specifies raw provider/dispatch readiness and the admitted equal-step/prefix contract. Frozen v1/v2 evidence is retained separately and unchanged.
