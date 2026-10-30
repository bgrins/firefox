# Installed overridden-dependency observation

Disabled observer for nine cases on one page: six color-scheme cases and three font-size cases. It serves the frozen fixture and harness unchanged, appending only a completion-report script. The reporter copies already captured values and WPT statuses; it performs no style reads or assertions.

The runner reuses the executed initial-independence observer. Only the record validator, result labels/control selection and temporary-directory prefix change. Localhost transport, nonce/run ID, raw requests, exclusive report collection, watchdog, fresh profiles, scoped Firefox relaunch handling, joined HTTP shutdown, installed-application checks and owned cleanup remain unchanged. Saved Firefox 158 and portable Chrome 156 pins are reused; root rechecks them at execution. No user.js, CSS preference override, native application, Git or control write is introduced.

REPORT retains all nine callback names, statuses and messages, the harness status, initial registration values and both phases of captured custom-property samples. The validator independently checks the fixed case/phase metadata and recalculates registration, grammar, literal winner and reference calibration. Sample equality is a separate expectation. The no-loser and literal cases are controls. Unexpected computed values remain evidence; they are not rejected as malformed reports. Setup failures can produce null records or partial phases, which remain incomplete rather than fabricated observations.

RESULT distinguishes transport/cleanup completion, observation completeness, calibration, control expectations, callback passes and harness success. A suite pass requires complete observations, all nine callback passes and harness OK. Ordinary test failures can still have successful transport and cleanup. No policy or native-acceptance verdict is assigned by this wrapper. Later computed-winner/reference reads are sequential diagnostics, not simultaneous snapshots of the first custom-property read.

Root must wait for the native owner to restore, preserve the disabled policy/manifest, activate and reseal, then execute Firefox and Chrome serially:

```
python3 -I -S -B artifacts/css-registered-overridden-color-scheme-installed-v1/run.py --browser firefox --run
python3 -I -S -B artifacts/css-registered-overridden-color-scheme-installed-v1/run.py --browser chrome --run
```

Outputs use css-registered-overridden-color-scheme-{firefox,chrome}-runtime-1. Without --run, the runner authenticates saved inputs only. The fixture result and native candidate result are not assumed or bound during preparation. check.py uses a DOM-free completion bridge, synthetic records and an in-memory receiver; it launches no server or browser and removes its owned scratch directory.
