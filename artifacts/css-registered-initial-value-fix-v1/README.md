# Computed registered initial values

The initial-defaulting helper stored the original registration text as a universal computed value. It now copies the selected entry from the existing computed initial-value cache. Both explicit inherited initial and substitution-produced initial use the helper; no keyframe conversion change is required.

The standalone patch contains two Rust files and one twelve-case WPT. Registered length initial `1in` must compute to `96px`; the baseline fails three cases. Universal-syntax and missing-initial controls distinguish retained raw values from typed normalization and clearing.

## Local validation

- Paired shared-tree macOS builds both exit 0. Each retains four existing build-monitor `KeyError: 'export'` diagnostics despite successful build completion.
- New ordinary WPT: baseline 9 PASS / 3 FAIL; candidate 12 PASS.
- Existing initial-value WPT: 29 PASS in both runs; CSSPropertyRule CSSOM: 40 PASS; previous typed-keyframe WPT: 16 PASS.
- Supplemental keyframe fallback diagnostic: 4 PASS / 1 FAIL becomes 5 PASS. This test relies on fix 70 and is retained only as an artifact, outside the standalone native/WPT commit.
- All 102 candidate subtests pass, all five test ends are OK, and the suite ends normally. Selected source/test and binary pins remain stable within each run.
- Scoped formatting and lint exit 0. Lint reports one warning that ESLint ignores the WPT HTML.
- Exact three-file patch applies and reverses on branch and retained upstream snapshots. This is source applicability, not an isolated upstream build.

`FINAL-PAIR.json`, raw logs, source snapshots, `FINAL-OUTCOMES.json` and `STANDALONE-PACKAGING.json` retain the evidence. The cascade source snapshots contain preexisting unrelated working changes; `final.patch` excludes them and the packaging record distinguishes staged and live source hashes.

Discovery came from source inspection and browser reproduction during the animation provider audit. There is no Lean-discovered counterexample or universal proof of this repair. Provider cache freshness and registration selection use existing Stylist scheduling; the fix preserves descriptor text and clones the complete computed provider value.
