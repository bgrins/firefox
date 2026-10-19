# FontFace provider integration v2

Root execution package for the reviewed conditional-clone candidate. No native build or browser run is performed by this packaging. The harness retains every v1 byte except its stronger dependency-authentication function. All eight fixed JSON files (tests, resources, regressions, metadata, config, context, case names and commands) are byte-identical to v1. Only NATIVE-PINS.json changes to candidate-v2. Original source hashes remain identical.

## Authenticate and replay

Pin FREEZE.json externally, then run:

```sh
python3 artifacts/css-fontface-provider-integration-v2/check.py
```

This authenticates v2 and both sibling dependencies before executing their checkers. V1 contributes complete original context/test/resource sources, exact test installation and 68 registered names; candidate-v2 contributes the 16-file formatted repair and exact apply/reverse checks. Neither replay compiles Gecko or executes test callbacks. Keep integration-v1 and candidate-v2 beside this directory when relocating. Python 3, Node and patch are required. Generated CHECK-RESULT.json, BASELINE-*.json and root result directories are not authenticated source inputs.

The candidate's sole behavioral adaptation and formatting were source-reviewed in `css-fontface-provider-macos-compile-review-v1/v2-addendum`. Passing this checker means the source package is consistent, not that the repair works.

## Root build and run sequence

Install the exact candidate-v2/native.patch against its pinned originals; keep the v1 proposed tests already installed. The harness never installs or changes sources and does not invoke a native build. Root must run the actual build and retain its terminal status and complete log.

1. Before the candidate build, capture exact inputs:

```sh
python3 artifacts/css-fontface-provider-integration-v2/harness.py \
  --repo /Users/bgrins/code/firefox --phase candidate \
  --out artifacts/css-fontface-provider-local-validation-v2/candidate-build-before
```

2. Run the unchanged RUN.json build command separately, retaining the entire output and the actual terminal exit code:

```sh
/Users/bgrins/venvs/firefox/bin/python ./mach build binaries \
  > artifacts/css-fontface-provider-local-validation-v2/candidate-build.log 2>&1
```

3. Only after a successful terminal build, run the matrix:

```sh
python3 artifacts/css-fontface-provider-integration-v2/harness.py \
  --repo /Users/bgrins/code/firefox --phase candidate --suite matrix --execute \
  --build-before artifacts/css-fontface-provider-local-validation-v2/candidate-build-before/before.json \
  --build-log artifacts/css-fontface-provider-local-validation-v2/candidate-build.log \
  --build-exit-code 0 \
  --out artifacts/css-fontface-provider-local-validation-v2/candidate-matrix
```

4. Repeat with `--suite regressions` and a fresh `candidate-regressions` output directory, using the same candidate build-before/log. The matrix retains the same 12 DOM + 28 window + 28 dedicated-worker cases, and the same seven regression sources/eight harness endings. Candidate matrix acceptance requires all 68 subtests PASS, three harnesses OK, terminal zero, exact case multiplicities and stable pins. Regression failures are retained for comparison, including existing failures.

The inherited harness rejects a v1 build-before snapshot for a v2 candidate run because package identity differs. Capture a new v2 candidate snapshot; do not edit old baseline records or bypass pin checks. A before-build pin set, a log hash and root's terminal attestation do not prove every compiler read, nor exclude unobserved intermediate edits. Root independently reviews build provenance. No broad working-tree or all-platform stability claim is made.

## Compare the existing v1 baseline

Run separately for each suite:

```sh
python3 artifacts/css-fontface-provider-integration-v2/compare.py \
  --baseline artifacts/css-fontface-provider-local-validation-v1/baseline-matrix \
  --candidate artifacts/css-fontface-provider-local-validation-v2/candidate-matrix \
  --output artifacts/css-fontface-provider-local-validation-v2/matrix-pair.json
```

Use analogous regression paths and a new output filename. Without `--candidate`, compare.py validates an old baseline offline and reports no candidate result. It authenticates package/dependencies, validates receipt hashes against full raw logs and before/after snapshots, checks exact commands/case identities, and permits only reviewed native pins, binary outputs and package manifest identity to differ. It reports every changed status/expected tuple and keeps messages. It never rewrites expected results or calls an existing failure a new regression merely because it persists. Build logs remain root's separately retained evidence; this tool checks the recorded successful-build attestation, not compiler semantics.

Do not interpret comparison success as repair acceptance. Review matrix success, all regression transitions and the existing open gates: macOS compilation/runtime, native-loaded/DOM-loading completion, shutdown/reentry, peer isolation, local-resource lazy behavior and other platform builds. Existing baseline failures stay explicit until the paired run establishes their fate.
