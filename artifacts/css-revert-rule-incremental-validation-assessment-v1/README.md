# Incremental rollback validation assessment

The incremental C candidate preserves the earlier C correctness roster, passes the six occurrence fixtures, and avoids the large single-trigger cost observed with the previous whole-source index. Dense rollback chains still have a material measured cost. These are local diagnostic results, not release performance acceptance or new bug counts.

Candidate cascade SHA-256: `d32913bd213ebaf1e5bbff4ed7117ec8af0003990807f6a3f2c3f5ed7ded41f1`; candidate stylist: `fd5ded7d96e15b16caacd03bc758da255333bdbed9b99bb4bc65bc6a1900b9b3`. Baseline is committed A+B+D with the Arc changes, not an unmodified release browser. Full recorded native pins are retained in the underlying packages and timing replay evidence.

## Correctness and occurrence

| Evidence | Result | Meaning |
| --- | --- | --- |
| Earlier C roster | 190 PASS; six pages OK | All 196 callback/page-end signatures exactly equal the historical cold-C candidate in `css-rollback-c-candidate-runtime-v1`. This comparison preserves a previously passing candidate; it is not 190 newly fixed bugs. |
| Four regression controls | 5 PASS, 2 known FAIL; four pages OK | All 11 signatures exactly equal the historical controls, including messages and expected-field presence. |
| Occurrence baseline | 6 FAIL; complete observation | Each fails the independent-source absolute assertion during initial rollback. Twelve shared/independent reads completed, all returning 17px/19px. |
| Occurrence incremental | 6 PASS; complete observation | All 48 shared/independent reads completed: twelve each for initial rollback, small value, large value, and return to rollback. |

The two retained cycle failures are “Cycle between revert-rule !important and revert-layer resolves to unset instead of lower layers” and “Multi-layer chain cycle with revert-rule !important resolves to unset instead of lower layers” in `revert-rule-cycle.tentative.html`. They are not silently recategorized as passes.

The occurrence baseline never reached the later mutation phases. Candidate success establishes the six fixtures' assertions, including later mutation behavior; it does not establish baseline behavior for those phases. Selector-list, cached-clone, and implicit-scope cases do not prove native allocation sharing, occurrence identity, or the general safety of quotienting occurrences by source-block pointer. No instrumented pointer trace was collected. The exact diagnostic fixtures remain research evidence; promoting a cleaned WPT requires the separate semantic/spec adjudication. These six failures are not six new bugs.

## Fresh A–B–B–A timing

Each cell below is the range of the two observed run medians, in microseconds per update. A is the baseline before and after the candidate; B is two fresh-process candidate repetitions. These ranges are descriptive, not confidence intervals.

| Workload and count | Baseline | Incremental candidate |
| --- | ---: | ---: |
| Dense chain, Rule 32 | 5.94–6.33 | 8.38–9.65 |
| Dense chain, Rule 64 | 6.52–7.15 | 11.58–12.13 |
| Dense chain, Rule 128 | 7.95–8.18 | 16.99–17.34 |
| Dense chain, Rule 256 | 10.41–10.92 | 28.48–29.22 |
| Dense chain, literal 256 | 10.25–10.66 | 10.35–10.55 |
| Dense chain, Layer 256 | 11.25–11.43 | 11.21–11.74 |
| Single trigger, 256 payload blocks, Rule | 8.11–8.36 | 8.83–9.24 |
| Single trigger, 256 payload blocks, literal | 8.12–8.22 | 8.59–8.63 |
| Single trigger, 256 payload blocks, Layer | 8.26–8.32 | 8.75–8.93 |

At 256 dense Rule declarations, candidate medians span approximately 2.61–2.81 times the baseline medians, while literal/Layer controls are close. This remains a substantial cost in the intentionally dense workload and should remain visible in the delivery decision. Finite counts do not prove an asymptotic bound.

The single-trigger axis counts matched custom-only payload blocks. Rule mode has exactly one Rule even at zero payload; zero is not the identical-CSS/no-Rule floor used by the dense-chain workload. At 256 payload blocks the candidate Rule range is only approximately 1.06–1.14 times baseline, and all modes show some candidate-versus-baseline shift. The prior whole-source-index comparison recorded Rule 16.50–16.52 versus its own baseline 8.87–8.96 microseconds, with literal/Layer close to that baseline. The fresh incremental result supports removing that large payload-sensitive penalty. This historical comparison spans separate sessions and baseline levels; it is not a controlled precise speedup measurement between index implementations.

Both fresh workloads use 1,024 measured updates per sample, seven samples, four warmups, rotated mode order, and exact computed-opacity checks. Samples span 4.56–31.64ms for the dense chain and 4.52–11.76ms for single trigger, substantially longer than the earlier short batches. Reports still lie on an approximately 20-microsecond batch clock grid despite the identical local `privacy.reduceTimerPrecision=false` preference. The timer uncertainty is amortized, not eliminated. Timings include custom-property writes, computed-style reads, and loop/bookkeeping costs. Setup is recorded separately. No statistical-significance claim, native-entry counter attribution, real-world distribution, release-default behavior, or performance pass threshold follows from these tests. Machine load, scheduling, warmup, and baseline drift remain confounders.

## Evidence and closure

`COMPARISON.json` is the newly replayed single-trigger comparison. `LONG-REPLAY.json` replays the prepared long-chain comparator and is structurally identical to its existing `COMPARISON.json`. Both comparators authenticated recorded package/source/application pins, callback/raw-log checks, run-info bindings, cleanup, exact report roster and correctness, and report extraction before producing summaries. These are saved-data checks; no browser or native process was launched by this assessment.

`ASSESSMENT.json` contains exact correctness/control signatures, occurrence phase reads, timing rows, and saved owner/restoration receipts. `INPUTS.json` pins direct assessment inputs; comparison records additionally pin their detailed runtime inputs.

The candidate native owner closed with launch chunk `69374f`, session `43025`, terminal chunk `43be49`, exit 0. Its saved independent restoration audit verifies the original source/application/index state and process cleanup. Long A2 has a retained terminal receipt. Single A2 does **not** have a recovered terminal exit: the original poll output was truncated and a resumed poll reported an unknown session. Its internal result, raw/report replay and cleanup gates pass; root separately checked owned PIDs/groups 97322 and 97197 and matching owner commands absent, source/application pins matching and lock absent (root check `cf0301`, exit 0). `RESUME-CLOSURE.json` explicitly leaves terminal chunk/exit null. Do not substitute internal WPT exit 0 for the missing external owner receipt.

## Commands executed for this assessment

```sh
python3 -I -S -B artifacts/css-revert-rule-incremental-single-comparison-v1/compare.py --a1 artifacts/css-revert-rule-incremental-single-a1-v1 --b artifacts/css-revert-rule-incremental-native-runtime-v1/browser/single_timing --a2 artifacts/css-revert-rule-incremental-single-a2-v1 --output artifacts/css-revert-rule-incremental-validation-assessment-v1/COMPARISON.json
python3 -I -S -B artifacts/css-revert-rule-incremental-long-comparison-v1/compare.py --a1 artifacts/css-revert-rule-incremental-long-a1-v1 --b artifacts/css-revert-rule-incremental-native-runtime-v1/browser/long_timing --a2 artifacts/css-revert-rule-incremental-long-a2-v1 --output artifacts/css-revert-rule-incremental-validation-assessment-v1/LONG-REPLAY.json
```

Single comparison receipt: `fb19c6`, exit 0. Long replay receipt: `796abc`, exit 0. Offline signature/phase extraction and comparison receipt: `94d69f`, exit 0. No live source, Git index, commit, native build, or browser changes were made.
