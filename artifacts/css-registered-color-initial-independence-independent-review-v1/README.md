# Registration initial-value observations

Installed Firefox 158 and portable Chrome 156 both accepted all three tested `CSS.registerProperty()` initial values without an exception. Each run produced one PASS, two FAIL and an OK harness ending. The red control and all syntax/reference calibrations passed. Observation collection and owned cleanup completed successfully; the tentative rejection assertions failed.

| Initial value (`<color>`, `inherits: false`) | Firefox | Chrome | Tentative assertion |
| --- | --- | --- | --- |
| `red` | Accepted; no exception | Accepted; no exception | PASS: accept |
| `CanvasText` | Accepted; no exception | Accepted; no exception | FAIL: expected `SyntaxError` |
| `light-dark(red, blue)` | Accepted; no exception | Accepted; no exception | FAIL: expected `SyntaxError` |

The complete transported registration records and WPT messages are equal across engines. The two failures explicitly report that the registration call did not throw. These are shared implemented outcomes in these installed builds, not evidence of a Firefox-specific interoperability defect. They disagree with the narrow JS registration-rejection expectation derived in the sealed [initial-value trace](../css-registered-color-initial-spec-trace-v1/README.md). That trace retains the current draft/published-text distinction and open issues; this observation does not settle specification interpretation, justify a native change, or replace conditional default-preservation research. It says nothing about later computed/used palette values or the separate `@property` path.

`replay.py` authenticates both frozen runtime payload sets, the active observer, exact fixture and served-resource hashes. It compares each raw request with REPORT.json, executes the pinned reporter in a DOM-free Node VM from transported records/callbacks/harness/UA, and requires exact emitted-envelope equality. An independent Python calculation checks calibration, acceptance/exception projections and RESULT aggregates. No registrations or browser operations run during replay.

The reporter replay establishes projection consistency, not independent recovery of the browser's source observations. Exception constructor identity and the rejected-name retry are asserted by the fixture but are not transported as separate fields. Here the contextual registrations threw no exception, so those later checks were not reached; the full WPT failure diagnostics remain preserved. The test's ordinary color syntax support check does not by itself establish computational independence.

Both RESULT files keep `all_callbacks_pass` and `suite_pass` false, while `execution_complete`, `observation_complete`, `harness_ok` and calibration/control booleans are true. Policy verdicts remain null and native acceptance remains false. Both cleanup receipts retain an initial group-operation PermissionError followed by successful direct-process reap/census, empty owned-group/profile lists and removal of the private temporary directory. Root terminal/freeze receipts establish the completed executions; this replay does not repeat live process, profile or installed-app reads. Browser paths and binary pins are the authenticated owner/runtime admissions, not a new live installation attestation.

Actual Firefox session 81304 launched at 770ecd and completed at da081e with exit 0; Chrome session 4630 launched at b97df2 and completed at aba37a with exit 0. Frozen manifests are recorded in REPLAY.json. Saved replays a618a0/0 and final 34c911/0 authenticated the raw data and exact reporter output. No native source, browser profile, runtime output or sealed predecessor was modified.
