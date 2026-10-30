# Registered animation-taint scope: complete comparison

Both installed Firefox 158 and portable Chrome 156 completed the corrected four-case fixture with successful registration, inheritance/syntax, animation-driver and literal controls. Each mode records four reads before and four after an ordinary underlying-value mutation.

| Source | Firefox writing-mode, all eight reads | Chrome writing-mode, all eight reads |
|---|---|---|
| Unregistered | vertical-rl | vertical-lr |
| Registered universal `*` | vertical-rl | vertical-lr |
| Registered `<custom-ident>` | vertical-rl | vertical-lr |
| Literal control | vertical-lr | vertical-lr |

The animated token is vertical-rl; the noninitial var fallback is vertical-lr; the initial underlying value is horizontal-tb. The initial phase distinguishes fallback from ordinary input even though the later ordinary mutation also uses vertical-lr. Results describe outputs, not an independently observed internal engine route. Firefox has three WPT FAIL and one PASS; Chrome has four PASS. Both harnesses end OK. The API calls and separate non-animated inheritance/multi-ident checks establish that both registrations took effect.

This exposes a coverage gap in the current candidate's unregistered-only producer. Registration exclusion was an experimental scope restriction, not an established specification exemption. The deciding specification sections are linked in ../css-animation-taint-registered-scope-v1/README.md. The broader name/value taint policy remains unresolved, and these browser comparisons do not prove native candidate behavior. A broadened producer needs exact registered tests and preservation checks before acceptance. No new independent fix is counted.

Firefox V1 remains an incomplete observation: three cases completed but the literal control and harness timed out. V2 only hides the diagnostic pre; JavaScript, assertions and timeout are unchanged. V2 completed, but this does not prove the timeout's cause. Raw V1 evidence remains frozen separately.

Firefox V2: session48509, launchf54c8a, terminal922fa0/0, independent cleanup74e02e/0. Chrome V2: session71944, launch7d098e, terminale3db75/0, independent cleanup161e85/0. Root independently recalculated all comparisons from raw records (60f4c6/0); peer replays2b6087/0 and98f03e/0 reconstruct the pinned reporter output. Both owned process groups and temporary profiles are absent. No preference overrides or existing user profiles were used. These are not performance measurements.
