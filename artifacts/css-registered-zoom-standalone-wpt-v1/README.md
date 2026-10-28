# Standalone zoom paired WPT experiment

Run the same 29 captured pages against committed sources and the seven-file zoom proposal, with the two admission-repair files restored to committed sources in both phases. The roster is exactly 636 named subtests and six reftests: broad A104 + held B16 + 446 regression assertions, followed by 56 zoom assertions and 14 animation/style-query assertions. All fixture bytes, metadata, resources and individual real WPT manifest entries match the three preceding capsules.

The original phase records outcomes without expecting all assertions to pass. The candidate rejects missing/duplicate identities, broad PASS-to-FAIL changes, and changed unresolved broad failure signatures (including complete B16 messages). A broad FAIL-to-PASS change is an observed repair and is allowed, including B. The 70 zoom assertions are observations rather than an all-PASS gate. Every row retains its original, standalone candidate, and historical combined-nine signature. Combined-nine-only passes identify possible dependence on the admission repair; three separate historical runs do not establish an independent causal proof.

The inherited headless WPT lifecycle creates private temporary profiles, uses automatic server ports, keeps raw logs, and verifies complete root/nested/index/source/resource/binary preservation before and after execution. Application metadata binds both symlink-entry and regular-target identity, bytes and BuildID. No metadata is rewritten. Cleanup removes only owned processes and temporary directories. A terminal successful build receipt, exact saved build epoch and externally supplied current epoch must agree; phase native dirt is exactly zero or seven, with all nine source bodies inspected. Both phases keep the same committed HEAD.

`POLICY.json` is enabled only for `original-1`, bound to the successful original build RESULT and saved EPOCH authenticated in `PHASE-BINDING-CHECK.json`. A separately sealed candidate successor will retain identical experiment, input, parser and comparison bodies, bind its successful build, and bind the exact completed original runtime inventory through `BASELINE.json`. Baseline adoption replays its raw log and authenticates its original build receipt. Signing or other HEAD changes require a reviewed successor; no implicit descendant allowance is implemented here.

Preparation checks are recorded in `MANIFEST-CHECK.json`, `INPUT-CHECK.json`, `CONTROLS.json`, `BINDING-CONTROLS.json` and `METADATA-CONTROLS.json`. They validate the real manifest, historical raw evidence, comparator rejection behavior and phase/metadata guards. They are not new browser executions or native acceptance. `RUNNER-DELTA.patch` records the lifecycle adaptation from the reviewed number capsule v5. `adoption.py` remains pending validation against the actual completed standalone original run.

After binding and sealing, root invokes:

```
python3 -I -S -B artifacts/css-registered-zoom-standalone-wpt-v1/run.py CAPSULE_SHA original-1 ABSOLUTE_CURRENT_EPOCH EPOCH_SHA ABSENT_ABSOLUTE_OUTPUT
```

Output must be an absent directory directly under `artifacts` whose name begins `css-registered-zoom-standalone-wpt-runtime-`. Candidate invocation adds the absolute original assessment path and its externally supplied SHA. Root owns execution; this preparation does not install source or tests, run Mach, or change Git/index/runtime state.
