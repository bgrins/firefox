# Independent actual-runtime review: exact traversal v2

**HOLD v2 for landing on the observed local performance cost. The bounded correctness experiment passed.** This supersedes neither the earlier source review's permission to experiment nor its arithmetic/provider limits. No production changes, compiler, browser or Git commands were run by this review.

## Correctness and experiment identity

The final root capsule contains 222 authenticated payloads, FILES `15c0026dd6c9a4c87dbe5b1abdac7788054d78714fc3c9400456c97f88f439b2`. This review agrees with its final HOLD decision. The root's additive retained-input analyzer correction and its first failed attempt are preserved: committed DOMRect was not in the per-WPT changed-file snapshot, so its bytes were later copied from the already frozen proposal and reconciled to the original live and six timing-run pins. This is a documented source transfer, not a new contemporaneous capture.

I independently reconstructed outcomes from the two raw WPT event streams, rather than accepting the summary counts. Each run contains exactly 74 unique subtest keys and 23 file outcomes. Baseline matches the previously retained DOM-only run. Candidate results are:

- Four new untransformed precision tests pass; the two large horizontal/vertical cases change from unexpected FAIL to PASS, and the two small controls remain PASS.
- The other 70 subtests are unchanged: 68 PASS and two expected FAIL. The expected failures are rotated SVG text element-versus-Range rectangles and Range trailing-surrogate indexing.
- All 23 file outcomes are unchanged: 22 OK and one PASS reftest. Baseline exit 1 is explained by the two unexpected precision failures; candidate exit 0 is consistent with the raw expected outcomes.

The four changed native source snapshots match the independently reviewed proposal in each phase. DOMRect's already committed precision change and the remaining fixed native inputs stay pinned. Before/after source, test and binary pin records match within each WPT run and each timing process. Baseline/candidate timing binary hashes match their corresponding WPT binaries. Each phase's two timing processes use identical binaries. Historical binaries are identified by contemporaneous hash receipts, not independently archived or rebuilt by this review.

Baseline, candidate and restoration builds exited 0. Actual-path clang-format and WPT lint each report zero errors and zero warnings. Final receipts establish original source restoration, unchanged other native sources, and unchanged HEAD/index. **Restoration is not byte-identical binary restoration:** initial and rebuilt baseline binary hashes differ. The restored source identity is exact; the independent analysis retains that build-level qualification when interpreting timing drift.

## Individual timing runs

Numbers below are per-process medians of seven 20,000-call batches, in nanoseconds per call. Each pair is two fresh-profile processes. This table preserves phase order rather than merging the surrounding baselines into one apparently independent sample.

| Case | Before | Candidate | Restored |
|---|---:|---:|---:|
| Ordinary, depth 8 | 150 / 150 | 150 / 150 | 150 / 150 |
| Transform near leaf, depth 8 | 200 / 200 | 250 / 200 | 200 / 200 |
| Transform near root, depth 8 | 200 / 250 | 250 / 200 | 200 / 200 |
| Ordinary, depth 128 | 350 / 350 | 400 / 400 | 300 / 300 |
| Transform near leaf, depth 128 | 350 / 400 | 450 / 400 | 400 / 350 |
| Transform near root, depth 128 | 350 / 400 | 450 / 450 | 400 / 350 |

All 36 case/process combinations passed exact geometry before and after timing, visibility and warmup checks. The independent analyzer checks all 252 batch positions, rotating case order, positive elapsed times and expected checksums, totaling 5,040,000 measured calls. It recomputes the reported medians from raw elapsed times.

The ordinary deep case is the clearest reason to hold: both candidate process medians exceed both initial and restored baselines. Candidate batches are five at 350 and nine at 400 ns/call; restored batches are twelve at 300 and two at 350. Initial baseline has five at 300, six at 350, plus three slow outliers at 500/550/600. Thus the conclusion does not rely on one extreme slow candidate batch or on pooling away initial outliers. The restored ordinary baseline itself improves from 350 to 300, so using only one baseline would materially change the apparent cost.

Near-root transforms at depth 128 also move upward: candidate batches are four at 400, six at 450 and four at 500; the surrounding baselines mostly occupy 350–400. Near-leaf depth 128 has overlapping distributions and one candidate run equal to the slower baseline runs. Shallow ordinary medians are unchanged. The report does not claim every case regressed.

Descriptively, using the midpoint of each phase's two run medians, the ordinary deep candidate is 14.3% above the initial baseline and 33.3% above the restored baseline; near-root deep is 20% above each surrounding phase; near-leaf deep is 13.3% above each. These are summaries of this experiment, not estimates of a population effect or statistical significance.

## Why this supports a hold, and what it does not prove

Avoiding a duplicate walk did not remove measurable costs in this tested implementation. Repeated higher deep-case medians around both baseline phases are sufficient to withhold landing while the separate optimization proposal is evaluated. They do not identify which instruction, branch or code-layout change caused the cost.

Limits are material: elapsed batches are integer milliseconds, giving 50 ns/call quantization; there are only two fresh processes per phase; phases run in a fixed order with builds between them; and repeated batches within one browser process are not independent users. Hardware/system drift and differing rebuilt binaries remain possible contributors. No p-values, broad Firefox performance claim or universal no-regression assertion is warranted. The shallow and deep distributions are retained individually in `INDEPENDENT-RESULT.json`.

A successor must preserve the reviewed v1-domain inclusion, old-defined matrix behavior and final coordinate checks while addressing the hot-path cost. It needs its own source review and paired correctness/timing experiment; current v2 passing browser tests cannot be transferred to untested v3 code. Additional repetitions of this unchanged v2 experiment are not a prerequisite to recording this bounded hold.

## Reproduction and scope

`review_runtime.py --check` independently reconstructs this review's result from the authenticated runtime raw logs and retained proposal snapshots. `verify.py --files-sha256 PIN` authenticates the closed review and runtime artifact before invoking that comparison. Root's own analyzer is retained as evidence but is not imported or executed to produce the independent result.

The source review's admitted frame/matrix/lifetime boundary, legacy numeric restart outside the supported domains, and full safe-origin F1–F12 open obligations remain unchanged. This review accepts finite experiment integrity and tested correctness outcomes, and recommends a performance hold on v2—not a complete CSSOM or whole-engine correctness verdict.
