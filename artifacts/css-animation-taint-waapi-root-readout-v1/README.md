# CSS and script animation provenance observations

Installed Firefox 158 and portable Chrome 156 completed the same isolated diagnostic. Root independently recalculated every lifecycle/calibration check from the fixture and checked the raw request against the saved report. All checks pass. Both browser process groups and temporary profiles were independently verified absent after cleanup.

| Producer | Firefox active writing-mode | Chrome active writing-mode |
|---|---|---|
| CSS keyframes | horizontal-tb (animated value) | vertical-lr (fallback) |
| Script-created keyframes | horizontal-tb (animated value) | vertical-lr (fallback) |
| Literal control | vertical-lr | vertical-lr |

Each active observation was stable for the first read and three subsequent frames. Both variable-driven cases returned to ordinary vertical-rl after cancellation. The literal control stayed vertical-lr throughout. The fixed effect was paused at 750ms of a 2000ms duration; its animated custom-property value was horizontal-tb in both engines.

These are interoperability observations, not a normative policy verdict or candidate-native result. They support treating CSS and script animation producers alike for an active-value implementation. The current specification's @keyframes wording and property-name versus value-taint distinction remain unresolved; see ../css-animation-taint-waapi-scope-v1/README.md. No feature preferences or existing user profiles were used. Concurrent native compilation means these runs are not performance measurements.

Firefox: session 82087, launch 835320, terminal 667f1a/0, independent cleanup 4c90fa/0. Chrome: session 58909, launch 85a6d9, terminal 74eea5/0, independent cleanup 198562/0. Exact requests, reports, resources, application pins and cleanup receipts are in the corresponding css-animation-taint-waapi-*-runtime-1 directories.
