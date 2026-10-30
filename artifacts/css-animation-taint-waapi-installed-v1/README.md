# Disabled installed-browser WAAPI observation runner

This runner serves the exact sealed standalone fixture and appends a reporting-only script. It reuses the executed partial-base installed-browser owner: authentication, HTTP receiver, browser commands, watchdog, process census, owned-group cleanup, Firefox relaunch handling, and final application authentication are unchanged. RUN-DELTA.patch records the schema, temporary-directory label and result-label changes. The bridge changes only the exported report name and performs no style or timing reads.

Execution is disabled. Root must authenticate the actual installed Firefox or owned portable Chrome inputs and activate the policy. No preferences, user profile, experimental feature flag or sandbox change is introduced. Existing pinned application binaries and hashes are runtime admission requirements, not a new live check performed during preparation.

Root-only commands after activation:

```
python3 -I -S -B artifacts/css-animation-taint-waapi-installed-v1/run.py --browser firefox --run
python3 -I -S -B artifacts/css-animation-taint-waapi-installed-v1/run.py --browser chrome --run
```

Run the two installed observers serially. They may run alongside a native compile at root discretion: they use separate installed/portable binaries, ephemeral loopback ports, private profiles and owned process groups, and make no native HEAD/index/epoch or restoration claim. No other observer should use the same portable directory concurrently. CPU contention may change wall-time/frame scheduling; this is not a performance measurement. Outputs are separate `css-animation-taint-waapi-{firefox,chrome}-runtime-1` directories. Exact resources, raw request and validated report are retained. Wrong sink values, false reference checks, partial exceptions and explicit nonfinite encodings remain observations. CSS and WAAPI sink values at every phase have no asserted policy result. `execution_complete`, `observation_complete`, and `reference_checks_pass` remain separate; `animation_taint_policy_verdict` is null. Root should independently recompute the reference checks using the pinned fixture JavaScript after execution.

The 180-second external watchdog does not guarantee transport of a hung page's partial state. Cleanup uncertainty retains the private profile and is reported as failure. This preparation ran no browser, listening HTTP server, process census, application authentication, native operation or Git command.

Saved validation: schema/transport checks 10718b/0, bridge 892c1d/0, fixture syntax be1bbe/0 and calibration dcbe1d/0. Twelve malformed schemas and three duplicate/foreign transport controls reject; wrong observations and partial failures survive. AST checks establish unchanged authentication/receiver/cleanup functions. Independent core review 3e2654/21e97e/375c42/25f19c is clear. These checks do not establish browser integration.
