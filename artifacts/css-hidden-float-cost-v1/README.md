# Float geometry query cost

Source-only local cost fixture. No browser measurement, geometry calibration, native acceptance, or performance conclusion has been performed. Root owns execution after review. The fixture is separate from the standalone float WPT controller; it does not install code or tests, build, stage, or commit.

## Workload

Direct floats and floats wrapped in two inline spans share the skipped subject's block owner. Each shape has 1, 32, or 128 floats and visible/hidden states: 12 configurations. Each float is 50% wide and 16px high, with an 8px-high full-width leaf. The timed target is the leaf of the last float. There are two floats per row at both outer widths, 160 and 168px. Expected leaf rectangles are `[10 + (index % 2) * width / 2, 10 + floor(index / 2) * 16, width / 2, 8]`.

The subject has a fixed 64px height and no nested block owner, text, margins, borders, padding, or fragmented container. Its lower floats overflow that fixed box; they stay in the same ordinary float owner. Fresh fixtures calibrate every leaf visibly at 160 → 168 → 160 before hiding. This extends the retained one-float diagnostic; calibration of the multi-float geometry is a prerequisite, not an observed result. Any calibration failure invalidates the measurement.

One warmup and five measured rounds rotate configuration order. Every batch uses fresh fixtures. The default receipt contains 60 measured rows, 148 acknowledged progress events, and 1,968,000 timed geometry queries. Warmup work is additional and excluded from reported timings. Fixed counts avoid adaptive work changes between variants.

Recovery performs 16 outer-width alternations. Mutation plus outer-only layout flush is timed as `prepare`. The first leaf query after that flush is timed as `first`, and its immediate repeat as `repeat`. Every full rectangle, target index, width, and individual elapsed time is retained. The validator reports correct/incorrect geometry separately for first/repeat in each configuration. Restoring visibility and the original width must recover every leaf.

A separate fresh fixture supplies clean-query controls. All leaves are calibrated visibly, then calibrated again after hiding if applicable. `hotSame` reads the last leaf 16,384 times; `hotCycle` cycles all leaves for the same number of reads. No DOM/style changes or event-loop yields occur during either batch. Every read checks all four rectangle components and contributes them to a deterministic checksum. Both batches are followed by another full geometry calibration.

## Interpretation

`SUMMARY.json` contains raw per-round samples, median, minimum, maximum, nearest-rank p90, and zero-sample counts for each bucket. Recovery samples sum the 16 individual measurements per round; raw individual times remain in `RESULT.json`. With five measured rounds, p90 equals the maximum and is not a tail-latency estimate. Hot timings cover a fixed full batch and include JS loop, comparison, checksum, and DOMRect overhead. No subtraction of that overhead is attempted.

A stale baseline answer performs different work. Its recovery time must not be compared as a speed advantage over a correct candidate answer. Geometry failures are retained, never reclassified as passing to make timings comparable. `recoveryGeometryCorrect` and `cleanGeometryCorrect` are geometry classifications, not claims of equivalent native work. Visible recovery failures or any hot mismatch invalidate the intended control. Candidate recovery should have no mismatches before its cost is interpreted. First-query timer quantization can yield zero; distributions and raw zeros are retained.

Clean hidden controls can show whether repeated queries become more expensive. These are bounded local, headless observations, subject to scheduling, warmup, browser-phase order, and timer resolution. They cannot establish CI performance, isolate the native traversal's cost, or establish a general no-regression claim. The float sweep can still repeat on separate `ReflowDirtyLines` invocations; this benchmark does not count native invocations or prove once-per-frame traversal. There is no fragmentation here. The separate multicol placement WPTs are not proof of the native pushed-float bit or branch being exercised.

## Execution contract

`run.py` and `cleanup.py` are byte-identical to the sealed hidden-query-cost predecessor. DEPENDENCIES.json records that manifest and exact preserved payloads. The runner verifies this capsule's external manifest and closed roster before behavior, pins Firefox, colocated XUL, execution inputs and every supplied source, launches a fresh profile against its loopback server, validates the progress roster, retains result/failure receipts, and authenticates bounded cleanup of its original process group/session. It retains the predecessor's limits concerning processes escaping that group/session. The runner deadline is 75 seconds and the fixture checks its 45-second deadline between bounded batches. Timeout or missing output is not evidence of a native hang.

After review, root can run:

```
python3 -I -S -B artifacts/css-hidden-float-cost-v1/run.py --manifest-sha FILES_SHA --binary ABSOLUTE_FIREFOX_BINARY --output ABSENT_OUTPUT --label baseline --pin ABSOLUTE_NATIVE_SOURCE
```

Repeat `--pin` for all 29 guarded native inputs in the parent campaign. Output must be new and outside the fixture capsule. The controller must independently join the runner's BEFORE/AFTER hashes to its known source phase, binary, successful build, and ownership guards. Labels do not establish source identity. In the standalone comparison, baseline means all saved HEAD source bodies and candidate means that same baseline plus the float-only patch, with none of the three accepted overlays. The fixture does not enforce that source interpretation itself. Keep execution sequential with builds, other browsers, and measurements.

A complete run preserves `RESULT.json`, `SUMMARY.json`, `REQUESTS.jsonl`, `BEFORE.json`, startup/spawn receipts, and browser log. Correctness and cleanup failure details must remain available even when the command exits unsuccessfully. No unrecorded URL configuration is accepted. Changes to CONFIG.json require a newly frozen, reviewed capsule; sizes are fixed at 1/32/128 and all other work counts have bounded validation.

## Static validation

Python parsing, JavaScript syntax checking, independent coordinate spot checks, the synthetic 60-row receipt, and eight rejection controls pass. A deliberately wrong recovery rectangle is retained with the geometry-correctness gate false. These checks validate the fixture and receipt handling only; no native, browser, build, compiler, Git, or index mutation was performed.
