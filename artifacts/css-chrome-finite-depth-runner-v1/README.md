# Portable Chrome finite-depth comparison

Disabled four-callback successor to the executed `css-chrome-same-element-runner-v1` (root-reported 29017/86e1e8/0). It copies the exact six resources, genuine manifest and four record mappings from sealed `css-contextual-duration-finite-depth-probe-v1`; no HTML, CSS, JavaScript or receiver changes. Depths are 1, 2, 4 and 8 intermediate nodes plus the leaf dependency. No Chrome depth outcome exists yet.

The direct WPT launcher, generated/effective Chrome argument filter, record collector and import checker are byte-identical to the executed predecessor. Browser/driver version156.0.8078.80, executable hashes, root admission, no experimental-feature switches, HTTP-only private server, fresh profile, 240-second watchdog and cleanup are unchanged. All failed publisher-signature checks remain documented; official CfT admission does not claim a publisher signature or alter OS protections. Root owns the portable application and future launch.

`run.py.diff` changes two exact cardinality checks and adds separate calibration reporting. `assess.py.diff` changes two→four callbacks and six→eight lifecycle events. `POLICY.json.diff` changes only the disabled gate, exclusive output, fixture/manifest, page, names and records. No Firefox expectations/preferences are copied. Five synthetic ordinary outcomes (zero through four FAILs) all retain their actual child exit/verdict; fifteen invalid streams reject.

`calibration.py` copies `expected_snapshot` and `require_original_calibration` verbatim from the reviewed Firefox depth-candidate comparison. It validates both literal-initial and contextual-initial snapshots plus the literal final samples/details/membership. The contextual first/follow-up values are not substituted or separately judged here: the unchanged fixture's WPT assertions remain the outcome. `CALIBRATION.json` reports each complete schema-valid record independently. Calibration failure is visible as `literal_initial_calibration_passed: false`, never converted to a contextual repair or hidden by a complete process lifecycle. Actual original Firefox records exercise four positive calibration cases; twenty mutations reject.

As in the predecessor, setup FAIL may prevent posting a record. The raw FAIL is retained and missing records are explicit; no observation or calibration is fabricated. Missing PASS records or malformed posted records fail the wrapper after preserving the collection receipt. Complete four-record collection and successful literal/initial calibration are required to use this run as a later contextual comparison baseline, even if `execution_complete` is true for an ordinary assertion failure. Unsupported CSS remains an observed test outcome.

The wrapper writes exclusively to `artifacts/css-chrome-finite-depth-runtime-1`. Root first reviews and activates `POLICY.execution_enabled`, then runs:

```
/Users/bgrins/venvs/firefox/bin/python -B artifacts/css-chrome-finite-depth-runner-v1/run.py --run
```

Without `--run`, it authenticates saved pins only. `check.py` and `import_check.py` completed without launching Chrome or installing dependencies; the latter repeats actual Chrome import/argument admission against private scratch copies. Unused Firefox/Safari registration warnings remain in the log. No native/Git/index/canonical state, user profile, browser settings, downloaded application or earlier sealed record is changed by preparation. No pass-count, CSS cycle-policy, native-correctness or acceptance claim follows from this runner.
