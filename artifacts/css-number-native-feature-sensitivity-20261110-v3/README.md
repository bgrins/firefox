# Native numeric feature and sensitivity gate

Status: v3 source preparation; no v3 native execution yet. V2 resolved dependencies and built, but Cargo reused the plain binary for the instrumented source and the unchanged comparator rejected missing traces. V3 gives every plain/instrumented variant its own initially absent target directory. The actual v2 failure is preserved under `origin/` and in its original execution artifact. V1 stopped before builds because `generate-lockfile` disregarded the seed lock required by the vendored Git source; its failure receipts remain unchanged and are copied under `origin/`.

The preceding native experiment passed 196 cases and 284 lexical comparisons using 180 retained Lean model rows, with cssparser's fast dispatch features disabled. Those actual model rows have the expected JSON types. Its comparator could nevertheless accept malformed external observations because Python equates Boolean/integer and integer/float values. This capsule preserves that comparator and all previous evidence; the new wrapper validates exact row types before calling it.

`python3 -I check.py --repository /path/to/firefox --out /new/preparation` performs source-only checks. It authenticates 18 inputs, reconstructs 19 dependency crates from 437 pinned Git objects, checks their vendor manifests/checksums, verifies the actual model rows, and rejects 18 malformed model/schema inputs plus four synthetic Cargo metadata changes. Nine schema controls demonstrate values equal under Python equality that exact-type validation rejects. The temporary source tree is removed. This checker never invokes Cargo, rustc or the native driver.

After source review, root may run:

```
python3 -I run.py --repository /path/to/firefox --out /new/execution
```

The runner creates its vendor tree, Cargo home and eight distinct Cargo target directories in a temporary workspace outside Firefox. Each label gets an initially absent target directory before its build; no target cache is shared across source amendments. The ineffective package-clean calls are removed. Every command receipt records its working directory and Cargo target directory; every binary receipt records its target and binary paths. It seeds a lock from Firefox's pinned dependency records, runs `cargo metadata --offline` against that seed, audits the actual resolved source/features, retains the resulting lock, then repeats metadata with `--frozen` and checks identical features and lock bytes before compilation. The preserved v2 artifact’s `resolution/REPORT.json` records this unchanged metadata-only recipe succeeding; it created no target directory. `resolve.py` reproduces that bounded validation without compiling anything. Every dependency must retain its pinned name/version/source and live in the isolated vendor directory. The entire 437-file source set is checked before and after each variant. No checkout source or existing build target is modified.

The gate builds baseline and three mutant variants, each plain and instrumented. Each process must finish the full corpus. Baseline must pass the unchanged lexical comparison; each mutant pair must agree on all public observations and then fail that comparison at its specified first witness. Compilation failures, driver crashes, trace inconsistencies and arbitrary comparison errors do not count as mutation detection. Temporary build outputs are removed on success or exception; full command output and binary/source hashes remain in the requested output directory.

| Mutation | First witness | Required changed model fields |
| --- | --- | --- |
| Report `has_sign = false` after scanning | `legacy-2-single`: `-0` | `hasSign` |
| Omit exponent's integer-type clearing | `legacy-8-single`: `1e0` | `isInteger` |
| Require two following bytes before exponent recognition | `legacy-8-single`: `1e0` | `consumed`, `rest`, `exponentDigits`, `isInteger` |

The frozen corpus order places no signed case before the sign witness and no exponent case before the other witnesses. The runner checks the exact first-failure message and exact changed fields. Instrumentation is applied after mutation; it observes the mutated source's own offsets and classification. No synthetic native result is substituted.

## Feature and build scope

Pinned Firefox commit `ec467c0219d3d5daf70f42fcc53677cf8a262173` specifies cssparser 0.38.0 from rust-cssparser revision `9f3ceddf398f5ce4ab76fdad1b42ccb6c578a926`. The standalone build uses Firefox's Git-source-to-vendor replacement pattern, not a rewritten path dependency. The style crate enables cssparser defaults. The checked default feature set is exactly `default`, `fast_match_byte`, `fast_match_color`; actual resolution must include cssparser-macros and phf. Optional serde packages are available in the pinned root-lock closure but serde is not an allowed cssparser feature for this gate.

This matches those dispatch features, not Firefox's entire Cargo feature union, allocator, LTO, link configuration or browser execution. The explicit development profile uses optimization level 1, debug information 0, debug assertions/overflow checks off, 16 codegen units, no incremental compilation, and unwind panic handling. The historical direct-rustc run also used optimization level 1; the build routes are distinct. Actual feature metadata and feature-tree output are retained. Rust/Cargo binaries are hash-pinned; the host SDK, linker and inherited host environment are not fully pinned.

The baseline compares lexical/public state against the historical feature-disabled run. Float bits and numeric-token Debug strings are excluded only from this cross-configuration comparison: Debug embeds the numeric payload, which is not an oracle here. Non-numeric Debug strings remain checked. Within each new plain/instrumented pair and each reset history, all public observations, including float bits and Debug, must match exactly. Changed float payloads across configurations are recorded separately, not judged against the exact-number model.

## Proof and provenance limits

The 180 model rows are copied from the accepted actual-JSON/Lean execution, not regenerated by this gate. Their source model, input and source-manifest pins are included. The proved seven-field bridge and its normalized-ASCII numeric-caller restriction remain unchanged. Sixteen legacy cases outside that restriction retain native transparency/reset checks but do not acquire model correspondence. Numeric core remainder is distinct from full token remainder and units.

This gate adds executable protocol validation and proposed sensitivity checks, not a new theorem about Rust, floating-point conversion, CSS prose translation, full scanning or browser behavior. The existing compensated-exponent source repair is part of the pinned baseline, not a new finding here. Input `commit: null` records explicitly identify preserved filesystem evidence; committed native/dependency inputs identify their Git objects. No prior artifact or execution receipt is rewritten.
