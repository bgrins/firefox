# Validated native feedback trace

The same four-mode diagnostic completes with 4 PASS / 1 OK. The corrected logger
produces 4,486 accepted native records across six processes, with contiguous
per-process sequences, 2,243 balanced call pairs, and no cap or trace error.
Root independently replayed the strict parser and its controls.

The trace resolves the main ambiguity in the earlier JavaScript observations:
the animation becomes ready between style calls, then later style calls reset
its timing by rebinding the timeline. It is not continuously stuck pending in
this execution. All 80 recorded readiness entries occur at style depth zero.
The parser identifies 54 readiness operations that restore previously unresolved
timing; none restores timing inside `StyleDocument`. Nested align/ready/tick
counts refer to overlapping operations and must not be added.

| Contextual mode window | Readiness restorations outside / inside style | Actual timeline changes |
| --- | --- | --- |
| Opposed offsets | 24 / 0 | 50 |
| Aligned offsets | 24 / 0 | 50 |
| Constant query | 1 / 0 | 1 |
| Stable underlying | 1 / 0 | 1 |

Mode windows use captured output order between JavaScript markers; ordering
across stdout and stderr is not independently proved. The whole-native-trace
readiness/depth result does not depend on those windows. Actual association
changes are matched entry/exit pairs whose returned timeline equals the
requested different timeline. Addresses identify live objects, not permanent
allocation identities; animation index is ordering metadata.

This supports the conditional pending barrier for the tested case. It does not
prove global scheduling convergence, full-state recurrence, a performance cost,
or conformance of every intermediate observable value. Diagnostic I/O itself
adds overhead. No new production defect or fix is counted; repair #160 remains
held for its broader native causal-closure obligations.

The exact patch is
`1fc04b711c6dbfdd6453e97b4974a04c02dd9be8d2b6b14396ce2b6febd8c576` from
`../css-style-query-feedback-instrumentation-v2-20261110-v1`. Only the logger
changed from the first diagnostic; the fixture and original native behavior
were preserved. Each complete native record is assembled before a single
bounded write. Failed writes, truncation, caps, sequence gaps, and malformed
records invalidate complete-trace analysis. Completely absent transport cannot
be detected from the log alone.

`../css-style-query-feedback-trace-analysis-20261110-v1/ROOT-ANALYSIS.json`
contains the root parser replay. Its positive control detects a restoration
inside a style call, and 17 negative controls reject corrupted traces. These
are finite parser checks, not a formal proof of the analyzer.

`ROOT-RESTORATION.json` independently verifies all four native sources, full
application bundle and extras, current-build binary hashes, unchanged HEAD and
index, terminated process groups, and removed fixture/backups. Your retained
testing build still includes the committed query-handoff fix. There are no
temporary production edits from this experiment.
