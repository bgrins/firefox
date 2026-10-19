# Worker font removal

Workers retain removed fonts in their user-font families. The repair detaches
existing family entries before reinserting the current FontFaceSet membership,
matching the document rebuild strategy. It preserves the existing notification
and generation logic.

The standalone patch is `fix-candidate-v2.patch`: four native lines and one WPT.
Keep this evidence/proof companion before that two-file commit.

## Evidence

- Four worker failures become passes; all 16 new window/worker checks pass.
  Both buffer and URL Ahem sources exercise delete, clear, existing contexts,
  and fresh contexts. Same-family ordering controls pass before and after.
- Nine existing regression files retain 10 passes and one expected failure.
- The native build succeeds. Lint has zero errors and one ignored-WPT ESLint
  warning. The warning-visible lint invocation exits 1 because warnings are
  enabled; its ordinary predecessor exits 0. Earlier failed invocations are
  retained as environment/argument diagnostics, not verification results.
- Only the worker source and two binaries differ between each browser pair.
  Two spec metadata comments were added afterward; executable test content is
  byte-identical to the tested version. See `WPT-METADATA-v2.json`.
- The patch applies and reverses at the original base and recorded HEAD.
  There is no isolated clean-base build claim.

`check_evidence.py` authenticates the recorded build and raw paired WPT logs.
The browser drivers and complete non-binary input snapshots are in
`../css-fontface-provider-probe-v1/removal-*`.

## Formal scope

`../css-worker-font-removal-proof-v1/REPORT.md` contains independent native,
specification, lifetime and WPT review. Its 18 Lean theorems establish membership,
shared-entry retention, duplicate suppression and matching order under explicit
admission premises. Root replayed them from a fresh relocated source-only copy.
The model does not prove all C++ heap, concurrency, font-provider or shutdown
behavior. Discovery came from static audit and browser isolation, not Lean.

Replay the proof with:

```
python3 artifacts/css-worker-font-removal-fix-v1/replay_proof.py \
  --freeze-sha 05669d44b30b226eb99db88b2def604b5152c00441a87d3e75b32fbc23146918 \
  --output /private/tmp/worker-removal-proof-replay
```

The pinned external Lean distribution is required. No build outputs are inputs
to the proof. `FREEZE-v2.json` disambiguates the checker and replay-receipt hashes;
the original capsule bytes and manifest were unchanged.

The separate loaded-descriptor/provider repair remains in progress.
