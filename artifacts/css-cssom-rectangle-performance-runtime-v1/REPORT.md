# Integer rectangle helper: local performance review

Decision: **HOLD_INTEGER_NATIVE_REPAIR**. The deep transformed-ancestor case shows a repeatable directional cost in these six local runs. This is enough to withhold this implementation while exploring a single-walk design. It is not a CI performance result or evidence of a browser-wide 37.5% slowdown. The independent DOMRect-only correction is outside this hold.

## Recount

Each value below is the median of seven batches, in nanoseconds per getBoundingClientRect call. Each batch makes 20,000 calls. Columns follow actual execution order; builds occurred between the three source phases.

| Case | Before 1 | Before 2 | Integer 1 | Integer 2 | Restored 1 | Restored 2 |
|---|---:|---:|---:|---:|---:|---:|
| ordinary, depth 8 | 150 | 150 | 150 | 150 | 200 | 200 |
| transform near leaf, depth 8 | 250 | 200 | 250 | 250 | 250 | 250 |
| transform near root, depth 8 | 250 | 250 | 250 | 250 | 250 | 200 |
| ordinary, depth 128 | 350 | 300 | 250 | 250 | 350 | 350 |
| transform near leaf, depth 128 | 400 | 400 | 400 | 350 | 450 | 400 |
| transform near root, depth 128 | 400 | 400 | 550 | 550 | 400 | 400 |

The deep transform-near-root median rises from 8ms to 11ms per 20,000-call batch: 400 to 550ns, descriptively +37.5%. Every candidate batch in this case takes 11–15ms, versus 7–10ms in all four baselines. This separation is consistent with the added rejected-helper walk before the original transform traversal; no profiler or native visit counter establishes exact attribution. Ordinary depth-128 improves to 250ns from 300–350ns. These benefits and costs concern different source branches and must not be averaged into a general win.

All 36 before/after case geometries match their independently recomputed small-coordinate expectations. All 252 measured batch checksums and all 36 warmup checksums match. Six runs contain 5,040,000 measured calls. Reported medians, batch order, sample indexes, call counts and per-call timing conversions are independently recomputed, not trusted from the JS summary.

## Identity and restoration

`probe.html` and `benchmark.js` match the sealed microbenchmark producer exactly. `SOURCE-BRIDGE.json` reconstructs the preceding sealed native proposal by reversing one exact function-signature whitespace change; no semantic difference is claimed from formatting. The retained original and candidate full nsLayoutUtils.cpp files match every corresponding runtime pin. Retained original DOMRect.cpp matches all six runs: this campaign measures **integer-only**, with the float DOMRect implementation unchanged.

All six runs record identical before/after hashes for their binary pair, scripts and tracked source files. All tracked native files other than nsLayoutUtils.cpp are identical across all runs. The two runs within each phase use the same binary pair. The original baseline, candidate and restored baseline have three different executable/XUL hash pairs; rebuilding the baseline did not recreate byte-identical binaries. Source restoration is exact for the tracked set. `COMPARISON.json` records these pairs per run. The build and restoration receipts both report exit 0, formatter reports zero problems, and the root driver reports unchanged HEAD/index.

This review hashes retained source/input bytes and authenticates internal consistency of contemporaneous binary receipts. Historical binaries were not archived here and are not independently rehashed or rebuilt by the reviewer. HEAD/index restoration is a retained driver assertion, not a present-time Git inspection. The browser processes were intentionally terminated after their result POST (exit -15); driver exits are 0 and profiles are removed. No malformed or missing observations were excluded.

## Limitations

All runs used a local macOS Firefox/160.0 development browser in **headless** mode, fresh profiles, DPR 1 and viewport 1366×683. They report document visibility `visible`; this does not establish a foreground graphical session. This differs from the proposal's preferred foreground run. Browser logs retain SWGL framebuffer and sandboxed cpuinfo warnings; they are not hidden or counted as successful graphics calibration.

Every elapsed batch duration is an integer number of milliseconds, with values 2–15ms. A 1ms difference corresponds to 50ns/call here. These data establish observed quantization, not a measured implementation timer resolution. The sample is small and has fixed phase order: baseline, candidate, restored baseline. Builds between phases can affect machine state, temperature and code layout. There is no randomized variant ordering, isolated native timing, confidence interval, process-level statistical test, CI harness, or cross-platform result. Allocations, garbage collection, JavaScript checksum and DOM API/flush-check overhead remain included. No further run is required for the current hold decision.

## Reproduction and scope

Run `python3 -I -S -B analyze.py --check` in this directory (or with an absolute path). It recomputes COMPARISON.json from the six raw results and checks source/input provenance, formatting bridge, configuration, identities, restoration receipts and all arithmetic checks. Run `python3 -I -S -B verify.py` to authenticate the closed sealed roster and replay the comparison. Neither command invokes a browser, build, Git, or main source mutation.

`NEXT-OPTIMIZATION.md` is a source-only direction, not an implemented or accepted successor. The preserve-3d WPT assertion typo remains a separate, unfiled possible good-first-bug in the earlier split review.
