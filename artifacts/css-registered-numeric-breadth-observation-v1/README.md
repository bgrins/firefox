# Registered numeric breadth observations

This standalone browser probe records **60 cases and 72 snapshots** without a native-fix acceptance gate. Open `observation-only.html` directly to inspect its JSON, or use the controlled paired runner below. It does not need WPT scripts or an external page resource. The existing 58-test normative WPT capsule is unchanged.

| Family | Cases | Inputs |
| --- | ---: | --- |
| Direct registrations | 30 | Ten syntaxes, each with literal calibration, ready primary with unused 1em fallback, and missing primary with selected-invalid 1em |
| Scalar provider to exact number | 18 | Six scalar syntaxes with the same triplet; provider initial 3UNIT, consumer initial 7 |
| Direct admitted math controls | 6 | Scalar calc with em/px ratio, fixed target font 20→30px |
| Typed math provider to exact number | 6 | Corresponding provider chain, fixed target font 20→30px and consuming width 20→30px |

The ten direct syntaxes are number, integer, angle, time, resolution, percentage, number-or-angle, angle-or-number, space-separated numbers and comma-separated numbers. The six scalar provider types are the first six. Alternatives and repetitions use a single numeric member here; later list-member math and composite-syntax provider chains remain outside this probe.

Each fallback triplet uses identical registration and consumer arithmetic. Direct percentages use font-size:var(--x) with a 100px parent, avoiding an unnecessary percentage-division prerequisite. Angle/time/resolution consumers divide by 1UNIT before multiplying by 1px. Provider chains convert to a registered number whose initial 7 distinguishes accidental consumer invalidation from the provider's legitimate initial 3. All registrations are non-inheriting. CASES.json records complete declarations, initial values, unique registration names, proposed expectations, mutations and calibration dependencies.

For noncyclic math, the target font is explicitly 20px then 30px, independent of either custom property. Direct math controls inspect the registered scalar and font; their width remains auto. Provider chains separately use the same literal conversion calibration and their matching direct math control before a downstream disagreement is considered calibrated. This addresses the source audit's earlier provider computation lead, not an assertion that an owned cache is corrupt. No disputed self-font numeric-cycle expectation is added.

RAW.json retains every registration error, actual custom value, consumer number, font size, width, specified CSS and parent font size. RESULT.json adds differences against proposed values and original/candidate differences. Literal or direct-math calibration failures block downstream entries from the calibrated_disagreements list. They remain visible in raw rows and calibration_failures: a failed calibration is not automatically proof of unsupported syntax, and a calibrated disagreement is not automatically a dependency bug. No CSS outcome causes execution failure; only incomplete capture, broken input bindings or failed cleanup/preservation do so. Every result states native_fix_acceptance:false and normative_verdict:not evaluated.

The runner reuses the reviewed self-font observation machinery with only its owned output prefix changed. It requires the corresponding completed/preserved WPT phase, identical epoch/native source and application metadata bindings, and strict compiled committed-HEAD original/candidate roles. Source roles remain the reviewed numeric preparation/collector pair used by normative capsule-v2. If those roles or the normative capsule change, create a new artifact version. Never run during a build, source transition, Git mutation or another browser phase.

```sh
python3 -I -S -B artifacts/css-registered-numeric-breadth-observation-v1/run.py MANIFEST_SHA original-1 ABSOLUTE_EPOCH_PATH EPOCH_SHA ABSOLUTE_ORIGINAL_WPT_ASSESSMENT WPT_SHA /Users/bgrins/code/firefox/artifacts/css-registered-numeric-breadth-runtime-original-1
python3 -I -S -B artifacts/css-registered-numeric-breadth-observation-v1/run.py MANIFEST_SHA candidate-1 ABSOLUTE_EPOCH_PATH EPOCH_SHA ABSOLUTE_CANDIDATE_WPT_ASSESSMENT WPT_SHA /Users/bgrins/code/firefox/artifacts/css-registered-numeric-breadth-runtime-candidate-1 /Users/bgrins/code/firefox/artifacts/css-registered-numeric-breadth-runtime-original-1/RESULT.json ORIGINAL_RESULT_SHA
```

Supply externally verified hashes and absolute evidence paths. Outputs must be absent. Redirect outer output to an owned artifact log and retain actual outer session/terminal exits. The browser has a fresh default profile, not the WPT preference configuration. Results describe that diagnostic environment under the same pinned binary. If preference differences affect behavior, synchronize the diagnostic configuration in a new version before comparing it with normative WPT outcomes.

The browser process group, profile and loopback server are owned and cleaned up. The browser is intentionally terminated after capture, so its recorded signal-related exit is distinguished from a natural exit. Full pre/post source/index/nested-repository, epoch, binary, application metadata and immutable helper preservation remain enforced. See the pinned predecessor for lifecycle details. Successful capture is not native acceptance or an additional bug count.

The source/spec basis is `css-registered-numeric-breadth-audit-v1`, especially CANDIDATES.json and REPORT.md. It identifies shared source paths and unrun hypotheses. This probe adds browser inputs, not new formal verification coverage or proven parser correspondence. The Firefox desktop frontend skill was applied. Static validation checks all 60 identities, 72 snapshots, unique registrations and explicit noncyclic font setup. Synthetic report tests preserve changed values, block failed-calibration attribution and reject incomplete captures. No browser, server, native build, live source, Git or epoch mutation occurred during preparation.

Interpretation details: snapshots obtain the target computed-style object, then read the parent font size before reading target value, consumer number, font size and width. This fixed order is recorded in queryOrder; it is not a no-prior-style-read experiment. Proposed-value comparisons use exact serialized strings. Inspect equivalent serialization or small floating-point differences, especially percentage math, before drawing a semantic conclusion.
