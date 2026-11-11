# Clip auto runtime experiment v2 (prepared, not run)

V1 completed the baseline and restored the tree/browser, but its parser incorrectly required Mochitest harness endings to be OK. Actual Mochitest endings were PASS. This version changes only that flavor-specific harness adapter and its synthetic controls; it does not weaken lifecycle, callback, crash or restoration checks. The original capsule and all runtime evidence remain unchanged. Root will rerun baseline under these exact inputs before running candidate.

This capsule prepares a reversible comparison for the copied candidate `5e85b5ad7ab7279cf2d7a1594cd5bf0aa32fbce495c28d7d65e466837c5040f5`. No browser test, native build, live source edit or Git mutation was performed while preparing it. Root owns execution after review.

The source/HEAD gate is `0dcfe7c2e7a8cd9924894449dd1d97d3c604d79c`. The three native originals are identical to the candidate's d68b16b source basis. Baseline uses the retained browser described in runtime-inputs/retained-build.json; its three sampled binary hashes were verified locally. That browser's receipt names90e0949346b5. Root established that production source has not changed since that build; subsequent composition-extraction runtime restored the original sources and complete application. The baseline intentionally does not rebuild.

Run from the checkout, with no other native builds, browser tests, Git changes or edits to the affected files in progress:

```sh
python3 -I artifacts/css-clip-auto-runtime-20261110-v2/run.py baseline baseline1
python3 -I artifacts/css-clip-auto-runtime-20261110-v2/run.py candidate candidate1 baseline1
```

The candidate requires a successful, restored baseline with the same frozen runner input digest. Each output directory must be new. Candidate mode temporarily installs the three copied source files and runs a real `mach build binaries -j6`, timeout2400s. WPT and Mochitest use the explicit application binary and run sequentially, each with full text and structured JSON logs. WPT permits exit0/1 while callback comparison decides its result. Mochitest must exit0 as well as pass its parsed callback gate; expected todo failures normally retain exit0. No nonzero Mochitest exception is silently accepted.

## Test gate

WPT uses only three explicit pages: the exact nine-case proposed CSS WPT; the existing38-callback iteration-composition page; and a separate local SVG diagnostic page. The CSS gate expects exactly four FAIL→PASS callbacks: three new matching-auto composition cases and the existing mixed-clip iteration case. All other callback names/statuses and harness statuses must remain identical. In particular the unrelated align-content and calc-size expected failures must remain unchanged.

The separate SVG diagnostic emits12 `CLIP_SMIL_OBSERVATION` JSON records: numeric/mixed repeat samples with accumulate none/sum at0.5/2.5s, numeric/mixed sandwich addition, and numeric/mixed by-only. Each case first pauses at0 and checks its static underlying clip before appending the animation. It asserts numeric positive controls are active, but makes no conformance assertion about the unresolved mixed-auto SVG additive behavior. Candidate observations, including exact clip strings and fixed inputs, must equal the baseline. These observations are not counted as12 WPT assertions or as a new normative test suite.

Four existing Mochitest pages run unchanged: CSS and mapped-attribute from-by/from-to. Full raw assertion results are retained, including repeated assertion labels distinguished by occurrence. The shared SMIL harness can use todo(false) for skipped bundles/cases; baseline therefore allows matching expected FAIL results, rather than demanding every callback PASS. mozlog removes the expected field when it matches status (pinned source excerpt and discovery receipt retained), so absent expected means expected=status. Explicit unexpected FAIL/PASS results stop the baseline. Candidate requires the exact same SMIL callback inventory/statuses. WPT pages must finish OK and Mochitest pages must finish PASS, and crashes or incomplete lifecycles fail parsing.

The observation parser rejects missing, duplicate and malformed records, duplicate JSON keys, changed case IDs/inputs and unpaused snapshots. It does not infer meaning from cross-stream output order: observation IDs pair samples, while harness lifecycle records identify tests. Browser raw logs are the evidence; the parser's source-linked gate is not a formal proof of browser behavior.

## Restoration and receipts

The wrapper reuses the reviewed bundle/process helpers from css-pseudo-animation-compose-extraction-20261110-v1 unchanged. It backs up every regular file in the complete Nightly.app bundle and the three explicit build/test extras before mutation. It records symlinks, modes, hashes and the Git index fingerprint. Two temporary WPT fixtures and their metadata must be absent initially; it installs only the fixtures and removes only those exact owned bytes afterward. Unexpected concurrent source/fixture edits cause a restoration failure rather than overwriting them silently.

On completion, timeout, test failure or cancellation, the wrapper first makes its process group quiescent, then restores source, full application and extras. It verifies original source, retained binary hashes, Git HEAD/index/clean tracked diff, mozconfig,61 test/harness source pins, and fixture/metadata absence. Successful restoration deletes only its owned backups. If a process survives or restoration cannot be verified, it retains backups and emits RESTORATION-FAILURE.json. Build intermediate objects are not claimed to be rolled back; the restored source mtimes force a later rebuild as needed.

BUILD.json records source/config/binary identities and build status; SAMPLED-BINARIES.json binds tests to the sampled binary. TEST-RESULTS.json and COMPARISON.json carry the exact callback gate and SVG observations. RESULT.json distinguishes test failure from restoration failure. Any unexpected baseline result is retained for review; no metadata is rewritten or exception silently waived.

## Preparation checks and remaining limits

The changed Python sources pass AST checks. Copied JavaScript inputs are byte-identical to the previously syntax-checked v1 inputs. Read-only replay of the v1 raw logs with the corrected adapter passes:48 WPT callbacks,5061 Mochitest callbacks (5002PASS/59expectedFAIL), and12 SVG observations; V1-ADAPTER-REPLAY.json records their hashes. This is not a v2 browser run. PARSER-CONTROLS.json records a positive synthetic four-improvement comparison, repeated Mochitest labels/expected FAIL support, and25 rejected malformed or changed-result controls. These are parser checks, not browser execution. Command help confirms --appname/--log-raw/--headless and --setpref support. Root already linted the exact nine-case proposed WPT in its separate candidate-capsule receipt; this diagnostic page is local tooling and not part of the eventual landing test.

RUN-INPUTS.json freezes all executable inputs, plans, native copies and test inputs. Do not edit those inputs once baseline starts. The mozconfig is optimized; debug/assertion coverage remains unrun and is not claimed by this experiment. The independent [gate reassessment](../css-clip-auto-candidate-review-20261110-v1/GATE-REASSESSMENT.md) identifies no new assertion-sensitive clip path: later component work is scalar arithmetic/clamping, while existing variant guards remain intact. Root permits this optimized real build plus focused comparison to support bounded local acceptance. This does not relax the separate missing-pseudo CSSOM debug gate. Direct count-zero FFI behavior remains covered only by the candidate model/independent proof, not by a browser repetition call which normally skips count0. No full SMIL, animation, release or security claim is made. A successful run is evidence for root review, not an automatic commit or acceptance of the fix.
