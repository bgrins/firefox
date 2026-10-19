# FontFace provider integration capsule

## Decision and provenance

Ready for root's controlled local integration of the existing reviewed proposal. This capsule does not add a native algorithm, change a test oracle, compile Gecko or run a browser. It does not accept the native fix. All 16 live edited source files exactly match the proposal's complete original files; all candidate bytes exactly match its complete candidate files. Eight additional context files match the prior review, including the worker-removal repair and updated Servo glue. The ninth reviewed contextual file, gfxFontEntry.h, is already counted among the 16 edited sources.

The common proposal's 55 inputs and WPT v2's 12 inputs were authenticated before using their contents. The embedded backend patch is required; the earlier standalone backend draft is not interchangeable. Original producer, second-pass producer review, independent review, and root readiness remain separate records under `evidence/`. This capsule supplies integration mechanics, not another lifetime proof.

## Patch and source inventory

- `native.patch` concatenates exact `common.patch` and `backend.patch`: six common plus ten backend files, with no unrelated deltas.
- `test-install.patch` changes the captured live canvas test to the exact reviewed v2 canvas bytes. The DOM test already equals v2 and therefore has no patch hunk. Both complete tests are immutable under `tests/` and `proposal/`.
- `NATIVE-PINS.json`, `TEST-PINS.json`, and complete original/candidate/live-test snapshots bind the transformations.
- No Git/index inspection occurred. Root must derive the eventual HEAD-to-final submission patch, including add-file treatment for any untracked tests. The test-install patch is an integration patch against captured live bytes, not that submission patch.

No native source mismatch required adaptation. The known live canvas mismatch is recorded explicitly and corrected only in the artifact patch. Root must install v2 before the baseline: 12 DOM tests, 28 window canvas tests, 28 dedicated-worker canvas tests. Old canvas baseline results are not this fresh pair.

## Source-only replay

Run `python3 check.py`. Python 3, Node and patch are required. The checker authenticates all current inputs, binds every original/candidate file to the producer manifest, applies both integration patches in a temporary tree with zero fuzz, compares complete bytes, reverses both, checks JS syntax and registers all 68 names without executing callbacks. It never reads the live checkout, builds or starts a browser.

`CHECK-RESULT.json` is an excluded receipt, not an input. Pin FREEZE.json externally before trusting the capsule. The manifest also authenticates `harness.py`; its own entry-point authentication occurs before any execution proposal is used.

## Root execution sequence

`harness.py` is a proposal for root to review and execute. It never installs sources, changes Git, formats or invokes a native build. Without `--execute` it only records authenticated current pins. With `--execute`, it invokes the fixed Mach WPT command and preserves the full console and raw JSONL.

1. Authenticate the capsule. Install the exact proposed test files, preserving the worker-removal fix. Keep all 16 native files at original pins.
2. Capture baseline build inputs using the command shape below, then run a cheap baseline `mach build binaries` separately. Retain the exact build command, exit code and full log.
3. Run the matrix and regressions using that build-before snapshot and successful build log. Record baseline failures as observations; a nonzero WPT result is not itself an invalid baseline if all expected tests complete.
4. Apply `native.patch`. If formatting changes bytes, inspect and retain the formatting delta and establish a new reviewed candidate manifest before using the harness; it intentionally rejects changes from the sealed proposal. Do not bypass that rejection.
5. Capture candidate build inputs, run the native build separately, then run the same matrix and regression suites. All 68 matrix subtests must pass and all three harnesses must be OK. Compare regressions by exact test/subtest/status/expected tuples, preserving existing expected failures rather than relabeling them as new passes.
6. Independently compare the full root run/build receipts. Inputs between phases must differ only in admitted native files and expected binary outputs. Test, resource, metadata, configuration and unchanged context pins must be identical. This harness does not inspect every repository file or attest unrelated working-tree stability.

Example commands, run by root with distinct output directories:

```sh
python3 artifacts/css-fontface-provider-integration-v1/harness.py \
  --repo /Users/bgrins/code/firefox --phase baseline \
  --out artifacts/css-fontface-provider-local-validation-v1/baseline-build-before
```

Run the build command recorded in `RUN.json` with its entire output redirected to a retained build log. Then:

```sh
python3 artifacts/css-fontface-provider-integration-v1/harness.py \
  --repo /Users/bgrins/code/firefox --phase baseline --suite matrix --execute \
  --build-before artifacts/css-fontface-provider-local-validation-v1/baseline-build-before/before.json \
  --build-log artifacts/css-fontface-provider-local-validation-v1/baseline-build.log \
  --build-exit-code 0 \
  --out artifacts/css-fontface-provider-local-validation-v1/baseline-matrix
```

Repeat with `--suite regressions` and a new output directory. Use analogous candidate paths after source application and its build. A root-supplied exit code is an explicit attestation, not a success conclusion parsed from arbitrary log text. Root must independently retain and verify the actual build terminal result. The before-build snapshot is compared with pre-run fixed inputs; binaries are freshly pinned before and after each WPT run. Snapshot/log hashes alone do not prove that a compiler consumed every file, nor exclude unobserved intermediate changes.

## Harness coverage and pinning

The matrix requires exact registered `(test ID, subtest name)` multiplicities, exact three harness endings with OK status, and suite_end. Candidate acceptance additionally requires exit zero and all 68 PASS. Raw actual statuses, expected statuses and messages are retained. Regression completion requires suite_end and all eight expected harness IDs, including both window and dedicated-worker wrappers for the existing worker-removal test. Regression failures remain visible for root's paired comparison.

Every snapshot checks the 16 phase-specific source files; eight invariant contextual sources; both exact proposed tests; seven regression source files; Ahem/framework and referenced regression resources; mozconfig, object-directory .mozconfig.json and mozinfo.json, and WPT config.json; per-test metadata (including absent files) and every metadata ancestor __dir__.ini down to the WPT metadata root. The build/config snapshots are source integration constraints, not portable settings to install elsewhere. The actual Firefox executable and XUL are hashed before/after, together with the Mach launcher and runner Python identity. Both wrappers of each .any.js are expected explicitly.

WPT-generated wrappers, runner implementation, server behavior, OS libraries and installed fonts remain external runtime premises. Capturing the concrete resources and configuration narrows those premises; it is not a self-contained browser distribution. The matrix only uses URL/buffer fonts. Some existing reftests permit local Ahem first; their unchanged baseline/candidate result is a regression gate, not a controlled local-font provider test.

## Scope and open gates

Local macOS compile/browser validation is the next step. Windows DirectWrite, Android FT2, Linux/fontconfig (including Fontations configurations), controlled installed local fonts, native-loaded/DOM-loading scheduling, shutdown/reentry, full ownership/lifetime and broad provider/formal correctness remain open. The legacy non-loaded in-place path and CSS-connected setter exclusion remain unchanged. Retained lazy resources are not a guarantee of immutable bytes after external font replacement. Each loaded descriptor update may allocate a fresh provider and rebuild caches; no performance neutrality is claimed.

Root is separately assessing unnecessary descriptor cloning when no wrapper exists. This capsule preserves the reviewed candidate exactly; any such adaptation needs a separate source revision and review before integration. No old acceptance or browser result is silently transferred to changed bytes.
