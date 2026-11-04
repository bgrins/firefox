# Private cold-C timing capture

Prepared only. No browser, build, live WPT, native source or Git state was changed. The standalone benchmark is copied byte-for-byte from `css-revert-rule-cold-cost-benchmark-v1/benchmark.html`. A same-origin iframe wrapper sets counts 0,32,64,128,256, seven samples and sixteen updates/sample. It does not alter the benchmark script or stylesheet generator.

```python
run(root: Path, output: Path, pins: dict, cancelled: Callable[[], bool]) -> dict
active_processes() -> tuple[int, ...]
```

Use the reviewed C source-role bindings: baseline is exact A+B+D; candidate is exact A+B+D+coldC. `SOURCE-ROLES.json` contains three native paths with both hashes. Pins require `execution_enabled: true`, `source_role`, relative executable `binary`, completed-build `build_revision`, current `harness_revision`, and a SHA256 `files` map containing the three native files, executable, sibling XUL and application.ini. Include other completed-build inputs as needed. Runtime metadata cannot substitute for root's source-to-binary receipt.

`pins['repetitions']` accepts 1 or 2 and defaults to 2. Each repetition launches a separate WPT process with a fresh private temporary profile and output directory. The first must finish cleanly before the second starts. An incomplete observation stops the invocation. Use one repetition for A1, two for B1/B2 on the candidate build, then one for A2 after restoring/rebuilding baseline. Compare the baseline runs for drift before interpreting the candidate difference.

CLI example, after root has supplied fresh pins and authorized execution:

```sh
python3 -I -S -B artifacts/css-revert-rule-cold-cost-wpt-v1/run.py --pins FRESH-PINS.json --output artifacts/NEW-OUTPUT --repetitions 1 --execute
```

Root owns execution and source/build restoration. The module retains the reviewed owned-process-group cleanup, cancellation, private profiles, source/application/HEAD/index checks and direct raw-stream/native metadata assessment. `active_processes()` stays populated if cleanup cannot prove group absence. Existing sealed runners remain unchanged.

The private wrapper has one named correctness callback. It waits up to ten seconds for the iframe and forty seconds for completion; the standalone page retains its thirty-second run and one-second sample guards. A WPT long timeout and 180-second external runner deadline bound each repetition. Synchronous browser calls cannot be interrupted by page timers. A timeout is an incomplete measurement, not evidence of a conformance defect.

All roles explicitly set `layout.css.revert-rule.enabled=true`, `dom.window.dump.enabled=true`, and `privacy.reduceTimerPrecision=false`. These appear in `SETTINGS.json` and the actual command. Disabling precision reduction is a local measurement choice, not release-default behavior. No timing value has a pass/fail threshold; finite zero-duration samples remain valid and must not be used as ratio denominators.

The wrapper emits the entire report after the benchmark finishes, in bounded JSON chunks prefixed `CSS_ROLLBACK_COLD_COST_V1 `. A unique run identifier, exact chunk count and contiguous indices bind capture. Missing, duplicate, malformed or mixed reports fail assessment. No report is logged inside timed samples.

The report assessor requires exact mode/count pairs, exact generated CSS, 105 complete samples, 1,680 measured updates, zero computed-value mismatches, and exact setup/warmup/measured counters. It checks all timing fields are finite/nonnegative and their units agree. BuildID, harness revision, optional SourceStamp/browser changeset, native hashes and raw infrastructure faults are checked by the runner. Getter correctness and workload counters are not measurements of native lookup counts.

Top-level `RESULT.json` exposes `complete_observation`, `safe_to_continue`, `supplemental_audit_passed` and `all_pass`, plus repetition records and report paths. `all_pass` means correctness and report integrity, never acceptable performance. Each repetition retains raw events, full stdout/stderr, benchmark payload and timing summary in `BENCHMARK-REPORT.json`, application metadata, pins, expected callback, command, process identity, cleanup and assessment. No synthetic supplemental report can satisfy runtime gates.

`CHECK.json` records syntax/inert registration, isolated manifest/config loading, exact fixture bytes and report-validator negative checks. None executes benchmark callbacks or measures timing. `FILES.json` seals this package.
