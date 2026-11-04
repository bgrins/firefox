# Supplemental rollback raw-event audit

The actual 80-callback baseline passes this supplemental audit: 74 PASS, 6 FAIL, complete observation, no infrastructure or fixture setup/runtime exceptions. Audit command `4775d2` exited 0. This does not make the six assertion failures passes or constitute fix acceptance.

The audit replays the sealed browser package's exact callback/lifecycle assessment, checks its saved assessment and preservation/cleanup records, rejects suite/test aborts, abnormal child exits and assertion-count violations, and binds the emitted browser BuildID to the pinned copied application metadata. It retains full callback/page signatures for later comparison.

For this baseline, `run_info.browser_build_id` and `application.ini` both identify BuildID `20261104094052`. `run_info.revision` matches the supplied harness HEAD `a6f39620516a4cf76a5dbf5208960adc79068cf1`. The application has no SourceStamp and `browser_changeset` is null. Therefore the source-build revision remains dependent on root's actual completed-build/source receipt; it is not discovered from application metadata or inferred from the harness revision.

Reusable interface:

```python
audit(runtime: Path, pins: dict) -> dict
```

CLI: `python3 -I -S -B audit.py --runtime RUNTIME --pins RUNTIME/PINS.json --output NEW_RESULT.json`. Supply the baseline runtime, or the candidate native runtime's `browser` subdirectory. The caller-provided pins must exactly match the recorded run binding, including the baseline/candidate source role and unchanged `stylist.rs`. Use a new result path; this package and the sealed browser package remain unchanged.

This audits saved evidence; it does not assert that a historical candidate application is still installed or independently verify current process absence. Native source-to-binary provenance, restoration, candidate acceptance, preservation of baseline PASS callbacks, and separate control-suite comparison remain root's responsibilities. The full emitted run_info and 83 callback/page signatures are retained in `BASELINE.json`.

`e0328f` exited 0 after accepting the actual baseline and rejecting eight independently mutated controls: suite abort, test abort, nonzero child exit, excessive assertion count, wrong browser BuildID, wrong harness revision, wrong browser changeset, and wrong application SourceStamp. No browser, build, Git command, live source change, or existing-package modification occurred.
