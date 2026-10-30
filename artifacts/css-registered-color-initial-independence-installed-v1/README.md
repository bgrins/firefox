# Installed registration-initial observation

Disabled observer for the sealed three-case registration fixture (83820957). The exact HTML and shared harness are served with only an appended completion-report script. The reporter reads already captured registration outcomes and WPT results; it adds no style getter, registration, animation, or assertion. Existing preservation42 and the active native trial remain untouched.

This adapts the executed installed ColorScheme observer. Executable/inventory pins, localhost-only transport, nonce/run ID, raw request retention, exclusive report receipt, watchdog, fresh private profiles, scoped Firefox relaunch handling, joined HTTP shutdown, process cleanup and installed-application preservation remain unchanged. Main-body differences are the temporary prefix, red control selection and result labels/explicit WPT aggregates. Preparation reads saved admissions only. Root execution reauthenticates installed Firefox158 and the retained portable Chrome156; changed installations cause a stop. No user.js or CSS feature preferences are created, and no native application is used.

REPORT retains all three named WPT statuses/messages, harness status, syntax support, independent red calibration, and actual acceptance or exception name/message. Missing records from setup failures remain null and mark observation incomplete; no exception is fabricated. Schema validation independently recomputes calibration and expected acceptance/exception-name matches from those records. The latter is a diagnostic projection, not a substitute for the WPT assertion: the WPT also checks the iframe DOMException constructor and successful same-name registration after rejection, which are not additional fields in the frozen producer record.

RESULT separates transport/cleanup completion, observation completeness, calibration checks, red-control expectation, all callbacks passing and harness success. `suite_pass` requires complete observation, all three callback statuses PASS and harness OK. Complete ordinary FAIL observations still return owner exit0 when transport and cleanup succeed. Incomplete acquisition can also be transported successfully; inspect observation_complete and WPT messages. The policy verdict remains null, with no native acceptance. Raw request, REPORT and actual served-resource hashes permit independent replay after each run.

Root must wait until the current native owner restores before launching either installed browser. After review, root preserves disabled POLICY/FILES, enables execution and reseals. Run Firefox, verify its terminal and cleanup, then Chrome:

```
python3 -I -S -B artifacts/css-registered-color-initial-independence-installed-v1/run.py --browser firefox --run
python3 -I -S -B artifacts/css-registered-color-initial-independence-installed-v1/run.py --browser chrome --run
```

Outputs are css-registered-color-initial-independence-{firefox,chrome}-runtime-1. Omitting --run only authenticates saved pins. check.py exercises the completion bridge, schema and exclusive receiver with synthetic data, checks unchanged lifecycle functions, and never starts a server or browser. No live process census, app reads, Git, index, control mutation or build occurs during preparation. No actual result is predicted.
