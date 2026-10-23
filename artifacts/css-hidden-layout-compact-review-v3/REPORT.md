# Compact hidden-layout runtime review

Verdict: **ACCEPT_SCOPED_RUNTIME_EVIDENCE; HOLD_COMPLETE_NATIVE_REPAIR**. Six correctness phases, two trace phases and historical restoration are authenticated. Four column/column-group failures remain; combined timing is incomplete.

## Correctness observations

| Phase | PASS | FAIL |
|---|---:|---:|
| Baseline | 29 | 29 |
| Principal only | 47 | 11 |
| OOF only | 36 | 22 |
| Both | 54 | 4 |

Independent reconstruction from raw events checks exact ordered 58-key rosters, six OK file ends, one suite end, stable inputs/binaries, selected source roles and prepared resource hashes. All 50 selected cases inherited from the prior 686-row corpus preserve that phase's prior status; the other eight are new table observers. Matching is by unique original subtest identity, retaining old and new file paths.

The four-phase matrix has 29 all-pass controls, 18 FAIL/PASS/FAIL/PASS principal repairs, seven FAIL/FAIL/PASS/PASS OOF repairs, and four all-fail column/column-group observers. Every baseline PASS remains PASS; no newly failing test appears in these four phases.

The remaining principal-route col/colgroup queries retain width 50/100 instead of 25/ 50 after append. OOF-route col/colgroup retain x=110 instead of 60. Each is a target mismatch after visible calibration. The corresponding td/table controls pass with the relevant repair. These are unresolved candidate-coverage failures, not malformed-fixture evidence or grounds to discard assertions.

## Cost evidence

The independent analyzer authenticates all parent/runner/WPT source and binary joins, six cost input hashes, complete group cleanup, exact query ordering and visible full-rectangle calibrations. It independently reconstructs distributions and geometry mismatches and compares those with the producer summaries. Each completed phase has 84 measured batches and 13,440 query records; two warmup rounds are excluded.

Baseline and principal-only each contain 3,213 geometry mismatches, exclusively hidden OOF: 427 at count 1 and 1,393 each at counts 32 and 256. OOF-only has zero. Thus baseline and OOF-repaired timings do not represent equally correct work. Principal-hidden full rectangles happen to be correct even in baseline for this fixture; its extra work is measurable but the fixture does not demonstrate why every extra operation is required for other histories.

For 256 hidden principal branches, the first-query batch median rises from 0 ms to 10 ms with the principal repair (samples 10,11,11,10,9,10,9). For 256 hidden OOF branches, first-query median rises from 1 ms to 8 ms with the OOF repair (9,8,7,9,7,5,9). Each batch sums 16 first queries after separate mutations and outer flushes. Repeat, distinct, second-pass and no-mutation medians are 0 ms in those repaired cases. The cost is concentrated in the first recovery query; this supports, but does not directly count, the intended forced-layout mechanism. A 0 ms timer observation is not zero work.

These are integer-millisecond local observations, seven batches per configuration and one browser run per phase, with rotating configurations but fixed build/phase order. No statistical-significance, broad performance, or no-regression claim follows. Distinct-query buckets at count 1 execute no reads and are not useful performance controls.

## Combined timing timeout

The combined runner reached its 75-second deadline with no observations. Its source/binary pins stayed stable; terminal/noLiveGroup, removed profile and empty cleanup-error receipts pass. This is a safely retained measurement failure, not an accepted combined timing result. The parent correctly continues later correctness phases.

The fixture fetches/parses CONFIG before its try/catch. Its 45-second deadline is checked between configurations, not during synchronous layout or startup. There is no request/progress log or partial-post stream. With no observation and no discriminating stack in the browser log, startup/config-fetch failure, long synchronous work and reporting failure remain indistinguishable. No native-hang or systematic combined-candidate defect is established. The older v1 fixture completed 84 observations with both repairs before its separate cleanup failure; that fact neither explains nor invalidates this timeout.

## Replay and limits

`analyze.py` is read-only apart from a required fresh output path. It imports no producer code and reconstructs the selected observations from retained raw receipts. Source reports/formal models remain conditional on their stated tree, provider, dirty-history and lifecycle premises. Full native acceptance remains held for the column boundary and cost decision; final runtime authentication and historical restoration passed.

## Original-key and trace checks

The original-key pair changes from 33 PASS / 25 FAIL to 47 PASS / 11 FAIL: exactly 14 FAIL→PASS improvements, with all 44 other status/message pairs unchanged. This retains evidence that the principal repair addresses failures under the original computed-size cache key as well as the current cache key; it does not certify all historical source variants.

Each trace phase contains 26 adjacent raw process-output triples. They join using the actual child-process identifier and frame pointer within each before/return/commit triple, not the log wrapper's parent PID. All returned and committed sizes are zero; no observed frame has a next continuation. Baseline has 22 dirty-preserved triples and four 0→0→0 clean-overwrite triples. OOF repair has 22 dirty-preserved triples and four 0→1→1 dirty-retention triples. The twelve instrumented WPT status/message pairs exactly match the respective uninstrumented phase (baseline 7 PASS / 5 FAIL; repaired 12 PASS).

Source diff inspection binds before to the point before candidate marking/ReflowInput construction, return to immediately after the child Reflow, and commit to after SetRect and DidReflow. These observations directly support clean-zero publication in baseline and retained dirty query eligibility in the repair. They do not log PresShell's force-query decision or the recovery callback. Correlation with repaired WPT outcomes supports that mechanism, while the full query→forced-layout identity/provider join remains a source/model obligation. No pointer identity across destruction/reuse or hidden-return branch outside the observed noncontinuation family is inferred.

## Final seal and restoration

Authenticated all 474 payloads under runtime manifest `d61460eb681158d98c6299d3b6605fd066cd6ae9a388039659674180c2daf019`, including the closed roster. Parent terminal exit 0 means its restoration/control flow completed successfully; it does not mean the combined cost measurement succeeded. All six correctness and two trace builds succeeded. Restoration build returned 0, no recovery errors remain, and INPUTS.before, BEFORE and FINAL match exactly, including historical HEAD/index/source identities. Root's sealed final check records 26 source hashes and nine absent temporary tests. This review does not require the live tree to remain at that historical HEAD after handoff.

No browser, build, compiler, production source or Git operation was run by this reviewer. The fresh verifier only authenticates retained artifacts and independently reprocesses raw JSON in a disposable directory, then removes its temporary outputs.

```
python3 -I -S artifacts/css-hidden-layout-compact-review-v3/verify.py --runtime artifacts/css-hidden-layout-compact-runtime-v3 --prior artifacts/css-hidden-flex-combined-runtime-v1
```

The evidence supports the measured principal and OOF corrections and preserves their original-key controls. It does not support calling the whole hidden-descendant repair complete: the selected column observers still fail. No extra assertion was weakened or removed. Cost adjudication must retain the actual geometry differences and absent combined sample. An ordinary-block/release follow-up owned by root is outside this capsule and has no inferred result here.
