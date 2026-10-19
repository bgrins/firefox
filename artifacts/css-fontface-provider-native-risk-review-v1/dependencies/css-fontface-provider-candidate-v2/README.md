# FontFace provider candidate v2

Source package for root's controlled integration; not a compiled or runtime-accepted repair. Root authored the existing candidate, preformat snapshots, preparation script and patches. This packaging adds original snapshots, dependency pins and a source-only checker without rerunning prepare.py or changing those bytes.

The sole behavioral adaptation from integration-v1 is to retain GetData() without cloning when no user-font entry exists. Existing entries still use a detached rule and the existing transactional provider preparation. The corresponding intent comment changes. All remaining preformat bytes equal v1; final differences from preformat are reviewed indentation and line wrapping. The source/API review is `css-fontface-provider-macos-compile-review-v1/v2-addendum` and its exact seal is retained in DEPENDENCIES.json.

## Replay and authentication

Pin FREEZE.json externally, then run:

```sh
python3 artifacts/css-fontface-provider-candidate-v2/check.py
```

The checker authenticates this INPUTS.json and all inputs, then the sibling integration-v1 dependency using fixed FREEZE/INPUTS hashes and all its 108 inputs. No dependency code is imported before authentication. It checks the exact conditional clone transformation, all 16 original/candidate identities, recorded formatting ranges and input/output hashes, regenerates both patches, and applies/reverses native.patch with zero fuzz in a disposable artifact-local tree. It does not run prepare.py, clang-format, a compiler, Mach or a browser. Python 3 and patch are required. The external formatter binary/config identity is recorded in TOOLCHAIN.json; replay verifies recorded command provenance and exact source deltas, not execution of that tool on another machine.

The original files are embedded. The authenticated v1 sibling remains required to establish the adaptation's provenance. A portable move must retain those two sibling directories; this is not a standalone browser distribution. Check output receipts are excluded from the input manifest; neither a self-consistent hash manifest nor a recorded exit status establishes runtime correctness.

## Next stage

Use `css-fontface-provider-integration-v2/harness.py` for candidate before-build pins and unchanged 68-case matrix/regression runs. Root installs native.patch and invokes the pinned build command separately. Baseline results from v1 are compared explicitly by integration-v2/compare.py, allowing only these reviewed native files, binary outputs and package identity to differ. Do not transfer baseline failures or acceptance from old candidate bytes.

MacOS compilation, worker shutdown/reentry/native-loaded publication, shared provider isolation and other backend builds remain gates. The no-entry branch preserves the original parse-entirely-before-assignment behavior; no performance measurement is claimed.
