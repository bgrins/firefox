# Pending registered-number native validation

Run only after restoring the full prototype, applying the live numeric proposal and the one-file pending GTest overlay, and completing a native build for that exact source state.

The runner requires an externally supplied current epoch hash and capsule manifest hash, the compiled candidate/prototype-overlay role, twenty source pins, and all preserved source/index/nested-repository roles. It selects the exact 22 GTests in ROSTER.json. The existing controlled Mach runner supplies a deadline, disk guard, owned process cleanup, and four binary fingerprints after the GTest build. The mutable epoch is marked uncertified before launching GTests. Only successful cleanup, preservation, assessment and terminal artifact publication restore its compiled-state claim; an exception leaves the in-flight claim false.

Invocation from the repository root:

```sh
python3 -I -S -B artifacts/css-registered-number-pending-validation-v1/run.py gtest-1 EPOCH_SHA CAPSULE_SHA
```

Redirect output to a separate artifact log. Each label must be unused. Never run concurrently with a native build, browser comparison, source transition, or Git mutation.

The assessment requires every selected name exactly once, one PASS per test, four complete suites and a matching final summary with zero failures or disabled tests. Its preparation check replays the actual previous twenty-test log and checks a synthetic twenty-two-test report against 78 corruptions. This validates report handling, not new native execution. The 34 pending resolver calls are expected source counts; there is no dynamic call trace. No ordinary browser producer or standalone native fix is accepted by this test overlay.

Preparation did not build, launch Firefox, modify native sources, change the index or update the mutable runtime epoch.
