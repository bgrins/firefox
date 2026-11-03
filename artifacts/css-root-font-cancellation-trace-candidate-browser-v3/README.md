# Bound cancellation trace build/archive owner v3 — disabled

This successor fixes two preparation failures in v2 and replaces recursive saved raw-refresh validation with the separately reviewed direct-equivalence helper. Failed v2 remains unchanged. It is diagnostic preparation, not a repair or acceptance result.

V2 terminated `15846c / 74508 / 54b321 / 1` in its full policy checker before runtime creation: an ORIGINS object was treated as a path. Its `run.py`/`baseline.py` origin records also named different bases from their diff headers. The earlier extracted v2 checks did not execute that failing complete checker. Root's actual independent verification `92ffd8 / 7504 / 2f72d6 / 0` confirms the capture, five source identities plus glue, app/extras/binaries, flags/controls, runtime absence, lock absence and process-group absence. Both receipts are pinned and checked. The successful original trace capture `da0e0cf7…` remains the admission observation; no new capture is fabricated.

## Exact changes

- All 15 origin records use `{path, sha256}` consistently, including the checker. Every `.diff` is regenerated against that exact authenticated recorded base in failed v2. The production checker verifies the complete origin set, path shape, source hash, exact delta and unchanged driver restoration tail.
- `admission.direct_evidence` authenticates the sealed `css-native-epoch-direct-equivalence-v1` package (`0c427240…`) and calls its pure saved verifier. It binds the exact native receipt, current capture and terminal, native HEAD and epoch controls. Saved admission retains the capture adapter's pinned role/binding checks, signed V114 parent receipt join, actual completed-refresh POST snapshot join and all source/app/metadata claims. It does not call `native_head_view` or `validate_refresh`.
- `baseline.observe` obtains the native HEAD directly from the unchanged authenticated native receipt and the expected epoch digest from direct equivalence evidence. It does not fabricate a research receipt or internal head-view object. The existing fresh Git signature/ancestry/native-parent/exact-path checks remain, with only the HEAD variable expression changed. All remaining live observation, source/HEAD-byte/inode, flag, control, app/binary/resource, lock, quiescence and guard checks remain unchanged.
- The 12 unchanged origin bodies—including `run.py`, the archiver and build/WPT phases—are byte-identical to v2; the entire restoration/failure-accounting tail is unchanged. Full semantic preparation still executes once before any runtime/source transition. The two reviewed full manifest/POLICY/consumed-closure readiness checks remain; no cache is introduced.

The five-source instrumentation-v3 capsule stays `e88c9c53…`: data/traversal use additional captured identities; matching/EffectCompositor/GeckoBindings use canonical captured identities. Original glue and custom-properties bytes remain context guards. The exact eight cancellation WPT callbacks remain unchanged; full original 22 callbacks are replayed before the 2 FAIL / 6 PASS / 1 ending projection. Complete FAIL outcomes remain observations rather than a false success assertion. The owner performs a real native build and the eight-case lane, then creates the independently verified standalone archive before restoring the original source/app state. The later 34-case connector probe is outside this owner.

## Actual saved validation

`3aede4 / 3508 / 8256f0 / 0` executed the **entire production `validate_policy`**, not extracted prefixes: 1,107 references, 1,195 consumed inputs, five source roles and full original replay. That call took about 0.60 seconds on this run; this is not a native-build or total-runtime performance claim. Ten negative controls exercise the original dict/path error, structured origin/path/hash checks, an authentic but wrong diff base, direct-equivalence/current/terminal/control bindings and a boolean-to-integer native-receipt substitution. Exact source comparison protects the unchanged fresh live-check body and driver/finally. `CHECK-SAVED.log` contains the result; `CHECK.json` records execution/review attribution.

No live guard, native build, browser, canonical/index mutation or unchanged stream/staging/archive suite was executed in preparation. Earlier suite evidence remains pinned. The final flat manifest is checked separately with the actual unchanged production `inputs.bind_inputs`, including wrapper/self-entry/wrong-digest rejection.

## Root-only handoff

Both execution gates are false. Root preserves the disabled POLICY/FILES, enables only `execution_enabled` and `candidate_execution_enabled`, and regenerates the flat manifest. Before launch, root runs the pure production consumer with the resulting active manifest digest:

```sh
python3 -I -S -B artifacts/css-root-font-cancellation-trace-candidate-browser-v3/check_manifest.py ACTIVE_MANIFEST_SHA256
python3 -I -S -B artifacts/css-root-font-cancellation-trace-candidate-browser-v3/run.py --run ACTIVE_MANIFEST_SHA256
```

No separate `--check` is needed: `--run` executes the same full preparation prefix, then every unchanged live guard. Runtime remains `artifacts/css-root-font-cancellation-trace-candidate-browser-runtime-v1`, absent after failed v2. Actual future terminal/build/WPT/archive/restoration evidence is not supplied or predicted here. Independent post-run verification must bind the actual v3 owner/terminal and all five roles before any archive browser use.

Peer `1a57d1/d7db05/b42f42` independently read all three executable deltas and authenticated the 1,107 references, 15 structured origins/diff bases, 12 unchanged bodies, ten tested inputs and actual saved result. After sealing, the public disabled `run.py --check` and final production flat-consumer receipts are saved externally; they are not retroactively inserted into this immutable owner.
