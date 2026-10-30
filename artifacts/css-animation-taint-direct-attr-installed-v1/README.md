# Disabled direct-attr installed-browser runner

This is a minimal successor to the executed WAAPI installed-browser observer. RUN-DELTA.patch changes only the four-mode schema/activeExpectation validation and temporary-directory label, and reports the separate active control result. Authentication, application pin checks, commands, HTTP receiver, watchdog, profile/process cleanup and result lifecycle are unchanged. The reporting script only reads the completed exported JSON and adds no style/timing/membership queries.

Execution is disabled. Root must activate/reseal the policy and run the installed observers serially. They may coexist with the native compile: each uses a fresh private profile, ephemeral loopback port and owned process group, and authenticates only installed Firefox or the owned portable Chrome inventory plus saved fixture/helper receipts. No HEAD/index/epoch or native restoration claim is made; another process must not share the portable directory. Browser input pins are reauthenticated during actual execution, not during this preparation.

```
python3 -I -S -B artifacts/css-animation-taint-direct-attr-installed-v1/run.py --browser firefox --run
python3 -I -S -B artifacts/css-animation-taint-direct-attr-installed-v1/run.py --browser chrome --run
```

Raw requests, exact effective resources and full reports are saved separately for each browser. Complete collection, cleanup/lifecycle success, reference_checks_pass and active_control_expectations_pass are separate fields. The last requires both untainted and literal active control expectations, so a failed untainted substitution cannot hide under green reference calibration. Active expected-value comparisons remain in each raw row and are not a wrapper gate; wrong values and false comparisons survive validation. Before/cancel var-sink policy has no expected value. The result's animation_taint_policy_verdict is null. Root should recompute calibration and activeExpectation with the exact saved fixture JavaScript after execution.

The unchanged 180-second watchdog does not guarantee a hung page's partial report. Cleanup uncertainty retains the owned profile and fails execution. No settings, user profile, preferences, feature flags, browser sandbox or installed package are changed by preparation. No listening server/browser/live process census/application scan/native/Git action was run here.

Saved checks: 166a26/0 accepts wrong/partial/nonfinite observations, rejects thirteen malformed schemas and three duplicate/foreign transports; AST equality covers inherited lifecycle functions. Bridge 1a2f70/0 confirms completion-only export and no extra queries. These do not prove live browser integration. Fixture docs record pure calibration tests separately.
