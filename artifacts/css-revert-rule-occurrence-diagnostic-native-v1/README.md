# Reversible occurrence diagnostic owner

Prepared and disabled. No source, application, browser, build or index operation has run. This owner derives from `css-revert-rule-incremental-native-v1` and retains its backup, bounded build, process-registry guard and restore-before-validation behavior. It overlays diagnostic cascade `35d377bd71dd93732577aa4d70920e7fccc1d5cf525b342d2a04c7ba724dfcdc` and the existing cold-C stylist `fd5ded7d96e15b16caacd03bc758da255333bdbed9b99bb4bc65bc6a1900b9b3` on the accepted A+B+D/Arc baseline. The diagnostic itself is based on incremental `d32913`; full source-role hashes are explicit.

Only the six occurrence callbacks run, once. There are no timing lanes, repetitions or timing thresholds. The browser adapter reuses the sealed `css-revert-rule-occurrence-local-wpt-v1` resources/manifests/helpers. No staged fixture or dependency trees were copied into this package; runtime preparation creates only that lane's private inputs/profile using the existing helper.

`CONFIG.json` pins the accepted baseline build receipt, source/context/library hashes, binary hashes through that receipt, the prior incremental build binding and closed owner execution, its restoration receipt, and the three direct correctness/control/occurrence results. It does not recursively include historical `baseline_evidence`, timing payloads or old staged trees. Prior validation must retain 190 PASS, unchanged 5 PASS/2 FAIL controls, and six occurrence PASS. These are prerequisites, not results of the new run.

Root must first commit the research, then set `expected_head` to that exact new HEAD and `execution_enabled` to true. Review the resulting complete configuration and hash it. The owner rejects a stale HEAD, changed helpers/payloads, non-artifact commits since the baseline build, changed native source, or a different baseline application. Activate only after the previous owner has closed and restoration is independently accepted.

Actual owner command after activation, with the reviewed 64-character CONFIG hash substituted:

```sh
python3 -I -S -B artifacts/css-revert-rule-occurrence-diagnostic-native-v1/run.py \
  --run REVIEWED_CONFIG_SHA256
```

The fixed output is `artifacts/css-revert-rule-occurrence-diagnostic-native-runtime-v1`; it must not already exist. Root owns the tool launch/session and must wait for its actual terminal, then retain `EXECUTION.json` with `launch_chunk`, `session`, `terminal_chunk`, `exit`, and `closed:true`. The owner never self-certifies its outer tool terminal. Run the separate restoration audit only afterward, including when the owner exits nonzero.

## Environment and observations

The owner passes `browser_environment:{CSS_OCCURRENCE_TRACE:"1"}` in its pins. The derived occurrence wrapper explicitly places it in the `phase_env` supplied to the actual `Popen` of `mach wpt`, and records that narrow setting in `BROWSER-ENVIRONMENT.json`. `ENVIRONMENT-PATH.json` pins the inspected native harness path: Firefox `get_environ` calls `mozrunner.test_environment`, which copies `os.environ`; that result is supplied to `FirefoxRunner`. The custom non-None key survives that path. Existing `dom.window.dump.enabled=true` preserves fixture phase markers.

Runtime evidence remains required. The adapter parses retained `process_output` records with the sealed diagnostic analyzer and saves `TRACE-ASSESSMENT.json`, including raw SHA256, content PID/call rosters, caps and weak phase contexts. Validation requires all six callbacks PASS, complete/safe WPT cleanup, actual native trace records and retained trace integrity. A missing trace fails validation; a setting or successful resource load alone does not establish propagation or block sharing. A positive repeated-block witness is reported separately and is not a requirement for calling the WPT lifecycle complete. Call caps limit observation; phase context is transport-only, not a certified content-PID/element join.

## Restoration

Before mutation, the owner records source bytes/inodes, HEAD/index/staged/unrelated diffs and the baseline application/extras semantics, then backs up the application and extras. A bounded `mach build binaries -j2` produces the diagnostic binary. Cancellation and error paths retain the existing process cleanup registry. Source/application restoration happens only after build and browser registries report no owned process. If cleanup cannot establish that, source/app and recovery backups remain in place instead of being overwritten under a live process.

The finalizer restores source bytes in place, the baseline application and extras, rechecks preserved library/context/HEAD/index state, removes the transition lock and removes its verified backups. A test/trace failure is raised only after that finalizer. Restoration does not mean the diagnostic passed. The independent audit separately checks the three possible process receipts: `build/build-PROCESS.json`, `build/WAKE-PROCESS.json`, `browser/occurrence/PROCESS.json`.

`PREPARATION-CHECK.json` records inert syntax/import/path/hash checks and preservation of the original cleanup body. No owner, WPT, build, process-list audit or native experiment was executed during preparation.
