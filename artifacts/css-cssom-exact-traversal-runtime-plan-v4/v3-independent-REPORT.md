# Independent actual-runtime review: exact traversal v3

**Finite correctness PASS; performance gate remains UNRESOLVED for transformed paths.** Do not advertise a no-regression result or grant an unqualified landing GO from this experiment. V3 does not reproduce v2's substantial ordinary-path slowdown, and its ordinary shallow case improves. The remaining transformed-path signal is smaller and mixed; this review does not label it a statistically established or browser-wide regression.

## Authentication and correctness

The independent preparation verified the 700-pin INPUTS record, HEAD `99a9ca84f08370c1797720db8688bcb3747f6985` against BEFORE, the already reviewed scripts, retained original/candidate source roles, fixed DOMRect identity and 23 unique test paths. It did not read partial timing results or poll during timing. Final artifact identity is recorded separately in `ROOT-AUTHENTICATION.json`.

After root reported terminal completion, `review_runtime.py` independently reconstructed both raw WPT event streams and all six timing records. Each WPT run has 74 unique subtest keys and 23 completed file outcomes. Baseline matches the retained DOM-only calibration. Two large untransformed rectangle cases change from unexpected FAIL to PASS; their two small controls remain PASS. The other 70 subtests are unchanged: 68 PASS and two expected FAIL. The latter are rotated SVG text element-versus-Range rectangles and Range trailing-surrogate indexing. All file outcomes remain 22 OK and one PASS reftest. Baseline exit 1 and candidate exit 0 agree with these expected-status records.

The reviewed four-file source variant matches each runtime phase. DOMRect and the other pinned native inputs remain fixed. This is the shared build including DOMRect fix102; isolated upstream execution or v3 execution without fix102 was not performed. Source/test/binary pins are stable within each WPT and timing process; each pair of timing processes shares its phase's binaries. Initial baseline and candidate timing binaries match their respective WPT binaries. All three build receipts report exit 0, as do formatting and WPT lint. Final records establish original source restoration, unchanged other native inputs and unchanged HEAD/index.

Restored baseline binary hashes differ from the initial baseline's hashes. This is exact source restoration and a successful restoration build, not byte-identical binary restoration. Historical binary identities are supported by contemporaneous receipts, not independently archived or rebuilt here.

## Timing observations

Each entry below gives two process medians in ns/call. A process median contains eleven 100,000-call batches. Phase order remains explicit.

| Case | Before | Candidate | Restored |
|---|---:|---:|---:|
| Ordinary, depth 8 | 150 / 150 | 130 / 120 | 140 / 150 |
| Transform near leaf, depth 8 | 190 / 200 | 200 / 200 | 200 / 190 |
| Transform near root, depth 8 | 200 / 190 | 200 / 210 | 190 / 200 |
| Ordinary, depth 128 | 330 / 330 | 320 / 310 | 310 / 330 |
| Transform near leaf, depth 128 | 360 / 370 | 400 / 370 | 360 / 370 |
| Transform near root, depth 128 | 370 / 390 | 390 / 390 | 370 / 380 |

All 36 case/process geometry calibrations, warmup checks and before/after geometry checks pass. The independent analyzer reconstructs all 396 rotating batch positions, positive elapsed times and expected checksums, totaling 39.6 million measured calls. Visibility, viewport, device-pixel ratio and user-agent records are consistent.

The ordinary shallow result is consistent across the two candidate processes: both medians are below all four surrounding baseline process medians. The deep ordinary distributions overlap; candidate medians are slightly below the initial baseline and within the restored range. This directly supports removing v2's *ordinary-path* cost objection for this tested v3 implementation, rather than simply reusing v2's HOLD.

The transformed cases do not support an unqualified performance pass:

- Near-leaf depth 8 candidate medians equal the slower baseline medians. Batch ranges overlap extensively; the 5 ns difference between phase centers is smaller than one 10 ns timer step.
- Near-root depth 8 has one candidate median equal to the slower baselines and one 10 ns higher. Its candidate batches are shifted somewhat toward 200–210 ns but overlap baseline ranges.
- Near-leaf depth 128 varies across candidate processes: one has median 400 with eight of eleven batches at 390–410, while the other has median 370 with a broad 350–410 range. Both baseline phases have medians 360/370. Treating the 400 process as the entire result would overstate the evidence; discarding it would also be unjustified.
- Near-root depth 128 has candidate medians 390/390. That equals the slowest initial baseline process, and exceeds the restored 370/380 pair. Most candidate batches lie at 380–420; baselines overlap, with most at 350–400. This is a residual cost signal, not clean distributional separation.

For descriptive comparison only, centers of the two process medians put transformed cases about 2.6–5.5% above the corresponding surrounding phase centers. Ordinary depth 8 is about 13.8–16.7% lower, and ordinary depth 128 about 1.6–4.5% lower. These numbers are not population-effect estimates or statistical significance claims. The raw per-process arrays are retained in `INDEPENDENT-RESULT.json`; no aggregate speed score weights unrelated topologies to conceal tradeoffs.

## Decision and limits

The previous large ordinary-path concern is materially improved. However, all four transformed phase-center comparisons point upward, and the deeper transformed routes are relevant fallback paths. I would keep native acceptance pending an explicit treatment of this remaining cost rather than certify a blanket no-regression gate. That is an **unresolved performance gate**, not a claim that v3 failed correctness or a requirement to discard its precision improvement.

A useful next step is to identify whether specialization/code generation adds work on transformed routes, or explicitly evaluate the small cost/precision tradeoff under the project's performance criteria. These data alone cannot identify the cause or set that policy. Do not run a broad new corpus simply to increase counts; preserve the six discriminating topologies and the source/domain contracts if investigating a follow-up.

The increased batch size improves quantization from 50 to 10 ns/call per integer-millisecond tick. It does not remove fixed phase order, builds between phases, differing rebuilt binaries, system drift or the small number of browser processes. Eleven repeated batches in a process are not independent users. Direct numerical speedup claims against the earlier v2 experiment would also mix different batch configurations and separate builds. No p-values or broad Firefox performance conclusion are offered.

The review did not execute compilers, browsers, main-tree mutations or Git commands. Root's full build resolves the immediate header/caller compilation gate for this candidate, while finite browser success does not prove all graphics, frame-lifetime, numerical-restart or CSSOM behavior. The source review's legacy-UB exclusion and original full safe-origin F1–F12 obligations remain explicit.

## Recheck

The review verifier authenticates the final runtime capsule and retained proposal before invoking `review_runtime.py --check`. That independent analyzer reads raw events and batches; it does not import or execute root's analyzer to derive its verdict. The final evidence and seal pins are recorded with this report.
