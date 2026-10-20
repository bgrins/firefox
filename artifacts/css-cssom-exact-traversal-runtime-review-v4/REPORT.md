# Independent actual-runtime review: exact traversal v4

**Correctness PASS; qualified advancement recommended.** The remaining deep root-transform cost is small but should be disclosed. It does not, on these results, justify continuing the native performance HOLD. This is not a no-regression conclusion or final landing approval: the standalone runtime without DOMRect fix 102 is still required if this repair is to be presented as independent.

## Authentication and restoration

Authenticated the sealed runtime FILES `7f836b9399f9098e0717e369c3ee51fa2df5002ae261d711f176ab9e6422f021` (224 payloads) and the reviewed v4 source proposal (62 payloads). The independent analyzer checks all 378 INPUTS hashes against retained snapshots or immutable sibling artifacts. Four source variants match the authenticated proposal; fixed native inputs include DOMRect fix 102. Every available per-WPT input snapshot is checked against its recorded hash.

INPUTS, BEFORE and FINAL agree on HEAD `99a9ca84f08370c1797720db8688bcb3747f6985`, staged-diff hash and full stage-entry hash. Original four-file sources and all fixed native hashes agree before/after; FINAL records temporary-test removal. This verifies the retained source/index-content receipts, not a fresh Git read or raw index metadata. All baseline/candidate/restoration builds, format and WPT lint receipts are exit 0. Root retained known build-monitor errors and warning observations; equal warning counts alone are not a warning-category equivalence proof.

All six timing runs have stable source/script/binary pins, removed fresh profiles and successful driver receipts. Two processes within each phase use identical binaries. Initial baseline/candidate timing binaries match their WPT binaries. Restored binaries differ from initial baseline binaries despite restored source. Historical executables are identified by contemporaneous hashes, not archived or rebuilt by this review.

## Raw correctness reconstruction

Independently parsed both raw WPT streams: each contains 74 unique subtest keys, 23 unique file completions and one suite end, exactly matching retained RUN rows. Baseline matches the historical DOM-only calibration. Results change from 70 PASS / 4 FAIL to 72 PASS / 2 expected FAIL.

Only the horizontal and vertical large untransformed-edge cases change from unexpected FAIL to PASS; the two small controls pass throughout. The other 70 outcomes are unchanged: 68 PASS plus expected failures for rotated SVG text Element/Range equivalence and trailing-surrogate Range indexing. All 23 file outcomes are unchanged (22 OK, one PASS reftest). Baseline exit 1 and candidate exit 0 are consistent with these records. No expected failure has been normalized into a success claim.

This is the shared build with fix 102 in both phases, not isolated upstream execution and not v4-without102 execution. Source patch applicability is a separate result.

## Raw timing reconstruction

Each cell below contains two browser-process medians in ns/call. Each process median summarizes eleven batches of 100,000 calls per case, following 10,000 warmup calls. The review independently checks all 396 rotating batch positions, elapsed values, geometry, checksums and 39.6 million measured calls. All 36 case/process geometry calibrations pass; visibility, viewport, DPR and user agent agree.

| Case | Before | Candidate | Restored |
|---|---:|---:|---:|
| Ordinary, depth 8 | 140 / 150 | 130 / 120 | 140 / 160 |
| Transform near leaf, depth 8 | 190 / 200 | 190 / 190 | 200 / 190 |
| Transform near root, depth 8 | 200 / 190 | 200 / 190 | 200 / 190 |
| Ordinary, depth 128 | 310 / 320 | 330 / 310 | 330 / 320 |
| Transform near leaf, depth 128 | 370 / 360 | 340 / 340 | 360 / 350 |
| Transform near root, depth 128 | 380 / 360 | 380 / 390 | 380 / 370 |

Ordinary depth 8 improves in both candidate processes relative to all four surrounding baseline medians. Deep ordinary candidate medians span the surrounding baseline range; their center 320 equals the center of the four baseline medians. Deep leaf-transform candidate medians340 / 340 are below every surrounding baseline median,350–370. Shallow transformed medians are unchanged or at the favorable end of the baseline range. These findings remove the broader cost pattern that motivated the previous hold, within this experiment.

Deep root-transform remains a tradeoff. The candidate process center is 385 versus pooled baseline 375: +10 ns/call, about 2.7%, descriptively. Relative to the separate baseline phase centers it is +15 ns versus before and +10 ns versus restored. Candidate batches are concentrated at 380–400ns: the first ranges 380–420, the second 370–400. Baseline batches overlap substantially but have more 350–370 observations; baseline ranges are 350–400 except one restored 480 outlier. This is a plausible small residual cost signal. It is not appropriate to erase it by labeling everything noise, or to average improvements in unrelated topologies into an overall score.

The timer produces integer-millisecond batches, equivalent to 10 ns/call per tick. The residual pooled-center difference is one such tick; two processes per phase and overlapping distributions do not establish a population effect. Fixed phase order, rebuilds, differing restored binaries and system drift limit attribution. Eleven batches within one process are repeated measurements, not eleven independent browser instances. V3 is historical context, not a paired comparison to v4. No significance or general Firefox speed claim is made.

## Decision

Recommend **qualified advancement** to the remaining native/package gates, with the root-transform result disclosed. The tested correctness gain is concrete, ordinary deep cost is within surrounding baseline variation, deep leaf-transform improves consistently, and the remaining deep-root center shift is one timer increment. Continuing an unconditional performance HOLD solely on that residual would overstate these data. This is an engineering recommendation to accept the measured bounded tradeoff, not evidence of zero cost.

Still required before claiming a standalone repair: runtime validation without fix 102 against its applicable source baseline, plus normal final packaging/review requirements. Existing provider/lifetime/numeric-restart admissions and full safe-origin F1–F12 obligations are not closed by these finite tests. The source review's known legacy-UB exclusion remains explicit.

No compiler, browser, native mutation or Git operation was performed in this review. The verifier authenticates the sealed runtime/proposal and re-runs this independently adapted raw analyzer; it does not import root's timing analyzer or use its summaries as the outcome oracle.
