# Native feedback trace result

The clean V2 run supports repeated rendering-stage readiness followed by finite timeline-rebind roundtrips. It does not demonstrate indefinite work within StyleDocument. This is a bounded observation of the current branch, not a proof that an arbitrary drain loop terminates.

The parser accepted all 4,486 native records as 2,243 balanced scopes across six PIDs, with sequences contiguous from one and no cap/error marker. Exact native schemas, object/scope identities, StyleDocument depth/call IDs, and changed-rebind candidate/return correspondence passed. The four expected callbacks passed with an OK harness; build and WPT exited zero and the runner's restoration receipt passed. ANALYSIS.json authenticates the raw log and completion/restoration receipts.

Primary counts are independent of stdout QF marker ordering:

| Method restoring start/hold from both unresolved | Style depth zero | Nonzero style depth |
| --- | ---: | ---: |
| MakeReadyAndMaybeTrigger | 54 | 0 |
| AutoAlignStartTime | 54 | 0 |
| Tick | 28 | 0 |

Nested methods can describe the same restoration, so these counts must not be added. There were 106 changed associations, and all returned the requested candidate. Fifty style calls contained two changed associations; six contained one. No recorded style call contained more than two. These counts describe this completed run and these instrumented entry points.

Secondary attribution by QF armed windows:

| Fixture | Changed associations | Style calls containing changes | Readiness restorations | Sampling scope |
| --- | ---: | ---: | ---: | --- |
| Opposed offsets | 50 | 25, two per call | 24 | 12 stale, 12 refresh |
| Aligned offsets | 50 | 25, two per call | 24 | 12 stale, 12 refresh |
| Constant query | 1 | 1 | 1 | stale |
| Stable underlying value | 1 | 1 | 1 | stale |

All attributed readiness restorations occurred at style depth zero. QF stdout and native stderr cross-stream ordering is not proved; mode attribution is contextual and the global depth result above does not depend on it. Object pointers are used only in active intervals, and animation index is not treated as allocation identity.

For a concrete native-only interval in PID 39606, style call 13 contains changed rebind pairs at sequences 44–45 and 46–47, both ending with start and hold unresolved. Outside that call, a stale scope encloses ready sequences 58–63; the next pair of changes occurs in style call 15. Refresh then encloses another ready pair at 85–90 before another finite style call. This demonstrates hidden readiness between snapshots, rather than an animation that remains continuously unresolved. The actual trace retains the full ordering; ranges here identify parser records, not source positions.

Neither nullness nor repeated pointer patterns prove equal full machine states. The result does not establish a settled-pixel oracle, a conformance bug, or a performance measurement. Aligned offsets producing the same pattern show that opposite sampled progress is not necessary for this fixture's pending/base-value handoff.

Native1 is rejected due to four records containing interleaved CSSFB prefixes. It contributes no complete-trace verdict. V2's logger uses one bounded write per record and was independently reviewed. The parser itself has finite validation controls: a positive four-mode trace, a positive restoration inside a style call, and 17 rejection controls. No independent parser review or formal parser verification is claimed.

Recommended next step: retain the no-readiness-inside-style-update boundary as an explicit hypothesis when evaluating the held drain candidate. If that candidate is tested, rerun this exact diagnostic and compare native ordering rather than inferring convergence from the repeated JavaScript snapshots. No new production patch follows from this run alone.
