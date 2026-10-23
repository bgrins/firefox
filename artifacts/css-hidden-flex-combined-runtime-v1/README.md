# Combined hidden-flex correctness and diagnostic experiment

Prepared source only. Do not run `experiment.py` until root authorizes the exact prepared INPUTS hash. No native files, browser, build or Git/index state have been changed by assembling these files.

## Plan

All 21 write targets are restored byte for byte in `finally`, followed by a restoration build if any native write was attempted. They are the previous 20 pending-prototype files plus AbsoluteContainingBlock.cpp. The other five guarded native files stay unchanged: 26 source guards in total. All six temporary WPT paths must be absent at preparation and execution entry, and are removed during restoration. HEAD, index digests, tracked layout/dom/servo diff digest and all 26 source hashes must match the original snapshot afterward.

Four uninstrumented source roles always install both flex and absolute files, preventing contamination from the preceding phase:

| Phase | Flex | Absolute |
|---|---|---|
| baseline | reviewed HEAD baseline | original |
| principal-only | one-line principal subtree mark | original |
| oof-only | reviewed HEAD baseline | selected v2 hidden OOF mark before RI construction |
| both | principal subtree mark | selected v2 OOF mark |

The baseline bodies must exactly equal the post-commit HEAD blobs; preparation rejects rather than adapting a different baseline. Root supplied post-research HEAD `0cff98532aacd6a4843572d9b49b933d356b1781`. No stale prior HEAD is pinned in CONFIG. `prepare.py` requires the requested actual HEAD, an empty index, immutable draft source pins and fresh output paths. It performs read-only Git queries and artifact writes only. It never installs native files or tests.

## Test roster

The original 15 files/656 subtests remain intact (124 new plus 532 prior regression subtests). Additions are eight OOF leaf-first tests, four real fragmentation tests and sixteen provider/owner/fragment boundary tests. Four bounded existing regressions add two more subtests and two reftests:

- `css-break/block-end-aligned-abspos-with-overflow.html`: tall bottom-aligned absolute child with fragmented overflow.
- `css-anchor-position/position-try-fallbacks-multicol-001.html`: fallback with a fragmented anchor.
- `css-anchor-position/position-try-fallbacks-no-fit-after-fit.html`: previously fitting fallback followed by no fitting option without an intervening rendering update.
- `css-anchor-position/anchor-fallback-scroll-axis.html`: scroll-triggered fallback reevaluation.

Total: **22 files, 686 subtests**, including 19 harness files and three reftests. CONFIG records each exact ordered subtest name. Every phase must produce every file-end, exact subtest rosters, unique identities and exactly one suite_end; normal diagnostic test failures and process exits 0/1 are retained. There is no all-PASS acceptance assertion. Calibration assertion text, extra zero fragments and the original static OOF failure are preserved, not normalized or filtered.

Additional regression discovery used Searchfox `--get-file` and path searches; local and fetched snapshots are retained under regression-discovery. Failed redirected sandbox fetches are recorded, followed by successful read-only network fetches. Preparation pins the actual reviewed local files; source discovery is not an upstream identity assertion.

## Optional traces

`--with-traces` adds separate baseline and OOF-only trace builds after all four uninstrumented phases. Flex is baseline in both. The selected `baseline-trace-v2.cpp` and `candidate-trace-v2.cpp` include the three before/virtual-return/commit observation seams and, for the latter only, the pre-RI mark. The 44 skipped-position and eight OOF-leaf tests run in each trace phase. Trace rows and counts are stored only under `traces`, not mixed with the uninstrumented result matrix. All three trace stage tags must appear; actual clean/zero/dirty causal sequences still require inspection, not a claim from mere tag presence.

## Preparation and execution

1. Root reviews DRAFT-FILES.json and its externally reported SHA.
2. After all signing, prepare with `python3 -I -S prepare.py --draft-sha EXTERNAL_DRAFT_SHA --expected-head ACTUAL_POST_COMMIT_HEAD`.
3. Inspect the emitted INPUTS hash and snapshots. All original/HEAD bytes, selected variants, scripts, fixture bytes and current test/metadata/resource pins are bound. The static draft's reviewed regression sources must still match.
4. Only root, after independent review, invokes `python3 -I -S experiment.py --inputs-sha EXTERNAL_INPUTS_SHA [--with-traces] [--with-timings]`.

Every native phase uses `mach build binaries`, then the exact WPT roster. No compiler/browser action is performed by preparation. Phase source and HEAD/index guards run before and after build/test. WPT snapshots record source, binary, test, resource and expected-status metadata pins, including metadata absence. HTML-linked resources are discovered recursively; arbitrary dynamic JS/CSS/network dependency discovery and whole SDK capture are not claimed.

Restoration continues across individual source/test restoration failures. Receipt-writing failure cannot prevent later restoration or rebuilding. A failed restoration-log open still attempts the build with inherited output. Any source, HEAD/index or resource integrity failure aborts the phase loop and enters restoration. The driver never stages, resets, checks out, commits or signs. It does not claim byte-identical rebuilt binaries, full-upstream execution, universal dirty-history correctness or native acceptance.

## Optional cost measurements

`--with-timings` invokes the separately authenticated timing capsule after each uninstrumented WPT phase, before installing the next source role. Each fresh profile serves only its loopback fixture; output is `timing-<phase>`, a sibling outside `timing-capsule`, satisfying the runner's output guard. No timings run on trace variants. Raw observations and summaries remain separate from correctness counts and are not a speedup claim.

A benchmark-only calibration failure or timeout with completed cleanup and stable pins is recorded and the remaining correctness phases continue. Missing cleanup/result evidence, any cleanup error, a missing reaped browser exit code, a surviving profile, or any source/binary/resource drift aborts and restores. Failure before browser launch is an infrastructure failure and also aborts; only a completed, cleaned-up measurement failure is nonfatal. The runner's reported before/after fixture/binary/pin identity and parent's full source/binary/resource/metadata pins must agree. Compiler/browser activity outside this experiment would undermine timing interpretation; root coordinates that window.
