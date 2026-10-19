# Registered keyframe substitution repair

The defect is numeric keyframe interpolation after substitution. The directory
name records the initial investigation; no animation-taint defect is established.

`Servo_GetComputedKeyframeValues` already resolves a custom-property map, but its
old output iterator reparses original raw `attr()`/`var()` expressions and can
produce Universal endpoints. The repair uses the map for typed Unparsed custom
declarations. Explicit CSS-wide, Parsed, universal and other declarations retain
the existing conversion path.

## Results

The final same-test browser pair changes eight failures/eight passes to sixteen
passes. Six adjacent passes and one expected-failure status remain; the latter
reaches a later assertion and has different diagnostic values. All 27 candidate
checks meet expectations. Both builds exit 0; their existing monitor `KeyError:
'export'` diagnostics are retained. Scoped format and lint exit 0; lint reports
one ignored-WPT warning and no errors.

The exact three-file patch applies and reverses on upstream and branch snapshots.
Runtime testing uses the shared macOS tree, not an isolated upstream build.
`ROOT-SCOPED-ACCEPTANCE.json`, `FINAL-PAIR.json`, `FINAL-OUTCOMES.json` and
`FINAL-APPLICABILITY.json` record the gates and their limits. Independent frozen
source, standalone-dependency and candidate reviews live in the corresponding
`css-registered-keyframe-*review-v1` / `*static-v1` artifact directories.

Discovery was source analysis and browser reproduction during verifier work.
The separate Lean identity proof does not prove numeric payload correctness.
Dynamic animated dependencies and fallback-produced CSS-wide wrappers remain
separate investigations. Initial invalid taint probes and all earlier outcomes
are retained without counting them as bugs.

Research/evidence precedes the native/WPT-only fix commit. The management ledger
will record its final hash. The pair driver is a historical reproduction recipe:
it requires its original sources to match the selected baseline HEAD before
swapping only those two files; it should not be run blindly on a later HEAD.
