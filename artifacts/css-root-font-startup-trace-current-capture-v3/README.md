# Queue startup trace capture: ownership category correction

This successor preserves failed capture-v2 and its root-owned failure evidence. Actual v2 capture a2077b/session96823/a01cc7/1 stopped in observe because ServoStyleSet.cpp was incorrectly listed in canonical source_preimages despite lacking installed_identity. No capture output was produced. This package makes no claim that v2 succeeded.

The production baseline.py and capture_current.py are byte-identical to v2. BINDINGS removes only ServoStyleSet.cpp from canonical source_preimages, retaining its base capture/hash in the four ordinary additional claims. EffectCompositor remains canonical. Existing observe canonical hash/identity/HEAD checks and additional-source base/hash/HEAD/fresh inode checks remain unchanged. The actual capture script repeats ordinary claims and checks equality before emitting output. No guard is weakened and no observer routing is added.

Actual saved check8d892d/session70231/5fd1a9/0 passes1525 references, whole epoch/snapshot equality, ten source roles and26 rejecting controls. The added category assertions require all canonical source_preimages to have installed identities, no overlap with additional claims, and union coverage of all ten source roles. The original ServoStyleSet misclassification is explicitly rejected. Four real inode replacement controls use an explicit Git double and removed owned scratch. Neither live observe nor capture ran during these checks.

Bindings retain source a433f953, actual frozen refresh a0c2e94f/epoch2927fa02/raw5a182222, e86/085f native authority and authenticated nonrouting role leaf. Root alone executes the actual capture:

```sh
python3 -I -S -B artifacts/css-root-font-startup-trace-current-capture-v3/capture_current.py FILES_SHA artifacts/css-prioritary-declaration-capacity-publication-capacity-runtime-1/COMMIT-RESULT.json 085fcdc6576fea84ef9e43fbc0d0c7f1111d9e7899d8d42f6040442e49d91d16 artifacts/css-root-font-startup-trace-current-v3.json
```

The disabled queue-trace native owner must bind this actual output and root terminal before activation; no future capture result is fabricated. Logging remains absent for capture and cancellation8 smoke, explicitly enabled only for later standalone archived diagnostics.
