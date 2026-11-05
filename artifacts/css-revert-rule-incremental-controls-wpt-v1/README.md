# Frozen cold-C browser comparison

Prepared only: no browser/build execution or live-tree/Git changes. The caller owns two reversible builds and supplies fresh pins. The role names deliberately differ from the earlier A+B+D experiment:

- `baseline`: exact A+B+D applicable-declarations/cascade plus unchanged stylist.
- `candidate`: exact A+B+D+coldC, including the reviewed cold-membership cascade/stylist bodies.

`SOURCE-ROLES.json` pins all three native files for both roles. Both packages use the same descriptors. No old source/build/signing authority is loaded.

```python
run(root: Path, output: Path, pins: dict, cancelled: Callable[[], bool]) -> dict
active_processes() -> tuple[int, ...]
```

Use `python3 -I -S -B`, without optimization. Pins require `execution_enabled: true`, `source_role: baseline|candidate`, repository-relative `binary`, 40-character `build_revision` and `harness_revision`, and a `files` SHA256 map containing the executable, sibling XUL, `Contents/Resources/application.ini`, and every native path in `SOURCE-ROLES.json`. Include other source/library files needed to bind the completed build. The runner checks the supplied association; it does not prove build provenance. CLI execution requires `--pins`, fresh `--output` under artifacts, and `--execute`.

Each package retains exact copied fixtures/resources, an isolated manifest and empty Mozilla manifest, and a prepared `staged/wptrunner.ini`. Each actual run stages a fresh private copy into its output directory. Automatic server ports, existing WPT tools/testing profiles, and explicit `layout.css.revert-rule.enabled=true` are used. This is a local harness environment, not a hermetic dependency bundle. Live/untracked WPT pages and real metadata/manifests are untouched.

Both runners have identical code. They use one headless process, a 180-second deadline, explicit cancellation, owned-process-group cleanup and temporary-directory identity checks. Source/application hashes, HEAD and index semantics are checked before and after. Failed group cleanup leaves `active_processes()` populated; do not restore inputs while owned processes remain.

Direct assessment requires each exact callback once, one page start/end, one complete suite and an advertised roster identical to selection. It rejects malformed raw events, suite/test aborts, crashes, nonzero or missing process exit status, assertion counts outside bounds, ERROR/CRITICAL logs, process-output fault markers and fixture setup/runtime exceptions. BuildID is compared to pinned application metadata; suite revision to the harness binding; SourceStamp and browser_changeset, when present, to the completed-build binding. Absent source metadata leaves provenance dependent on the owner’s build receipt. These checks are implemented directly here, without the old 80-case supplemental audit.

Raw events, full stdout/stderr, application metadata bytes, pins, expected names, policy, command, process identity, cleanup, preservation and assessments remain in the runtime directory. Assessments include diagnostic events and callback/page signatures with expected/intermittent field presence. `complete_observation` is separate from successful outcomes. `supplemental_audit_passed` requires the direct checks plus complete, preserved execution; it never comes from a synthetic report. CLI zero means complete observation, not all assertions passed. `native_fix_acceptance` is always false; paired acceptance belongs to root.

Only pinned staging/raw-parser and process-cleanup helpers are imported. No signing, restoration, build or capture entry points are called. `CHECK.json` records browser-free checks; `FILES.json` pins the package. Existing sealed packages remain unchanged.

## Regression controls

Four pages: `revert-rule-basic.html` (four PASS callbacks), `revert-rule-custom-property.html` (one PASS), `revert-rule-cycle.tentative.html` (two named historical FAIL), and `inline-style-revert-layer-crash.html` (crashtest PASS, no callbacks/reference). The three testharness pages must end OK. Fixtures, support scripts and cycle metadata match the earlier controls byte-for-byte.

The cycle metadata has exactly two FAIL entries. `POLICY.json` retains names and exact historical green-expected/red-observed failure messages. Different failures, unexpected passes, missing/duplicate/new callbacks or a failed crashtest cannot count as unchanged. Both cycle callbacks stop at their first color assertion; later assertions have no inferred result. Unrelated directory metadata and platform timeout allowances are not copied.

An unchanged run has five callback PASS, two cycle FAIL, three harness OK and one crashtest PASS; process exit zero. `controls_unchanged` is the comparison field; `all_pass` remains false for retained cycles. No normative cycle-policy resolution is claimed.
