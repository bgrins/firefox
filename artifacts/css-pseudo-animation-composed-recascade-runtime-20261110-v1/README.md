# Composer-to-recascade runtime proposal

Prepared only; no build, browser run, source installation or application mutation by the author. Root must review and freeze an execution HEAD plus retained baseline receipt after the active transaction restores. The copied native driver and fixture are the independently reviewed `css-pseudo-animation-composed-recascade-20261110-v1`; the cumulative source basis is the corrected transient recascade runtime v4. No production origin-eligibility candidate is included.

The candidate installs the same 14 existing-file roles and adds the composed test as a fifth temporary fixture. There are two WPT fixtures installed for both modes and three privileged fixtures installed only for candidate. The native/XPIDL/manifest driver patch applies over the exact predecessor candidate; the query geometry correction stays intact. A real candidate build, all three installed ESLint checks, WPT lint and manifest lint are mandatory gates.

| Suite | Required result |
| --- | --- |
| Ordinary WPT | Exact unchanged 130-record vector: 99 PASS, 19 known FAIL, 12 OK harness endings |
| Query helper | All 208 named assertions and unconditional normal completion, command exit 0 |
| Transient recascade | All 100 named assertions and unconditional normal completion, command exit 0 |
| Composed investigation | All 122 assertions present in order, all five task enter/leave pairs, all 119 non-probe assertions PASS (including 33 setup checks); retain all three probe outcomes |

`investigation_valid` is distinct from `all_assertions_passed`. The three exact names classified `probe` in COMPOSED-ASSERTIONS.json are the only failures permitted for a valid investigation. A probe-only failure must coincide with a normal aggregate `test_end` FAIL message `Finished in Nms` and command exit exactly 1. If every assertion passes, the aggregate ending must be PASS and command exit exactly 0. An unexplained aggregate FAIL, timeout, missing/duplicate/unknown callback, task mismatch, expected-todo/intermittent override, ERROR/CRITICAL, crash, abnormal browser exit, or memory diagnostic invalidates the investigation. All raw logs and messages are retained. `native_fix_acceptance` remains false even for all-pass output.

This distinction follows the pinned Mochitest TestRunner.js: normal completion emits the aggregate result with `Finished in Nms`; timeout uses a different message, and cleanup/profile failures can emit additional unknown callbacks, which are rejected. Passing this parser is not a waiver for a harness failure. The command exit is checked against the complete assertion result, never allowed merely because it is 1.

The three interpretation probes concern a registered effect with null progress selecting Animation origin over a real transition contribution. The present normative interpretation is unresolved; neither a probe failure nor a probe pass establishes a new Firefox bug. The other 119 assertions must pass before any probe is interpreted, including native transition level, target identity, in-effect membership, freshness, unchanged state and stable-provider setup. The fixture is restricted to physical fixed-pixel margin-left endpoints and held timing. General provider coherence, animated custom properties/fonts/logical units, visited/cache/admission semantics and the public missing-pseudo debug transform-hint gate remain open.

## Preparation and execution

Source-only replay:

```
python3 -I -B artifacts/css-pseudo-animation-composed-recascade-runtime-20261110-v1/check.py
```

After root chooses the clean execution HEAD and authenticates the retained baseline receipt:

```
python3 -I artifacts/css-pseudo-animation-composed-recascade-runtime-20261110-v1/freeze.py <head> artifacts/css-keyframe-order-combined-current-build-20261110-v1/build-result.json
python3 -I artifacts/css-pseudo-animation-composed-recascade-runtime-20261110-v1/run.py baseline baseline1
python3 -I artifacts/css-pseudo-animation-composed-recascade-runtime-20261110-v1/run.py candidate candidate1 baseline1
```

Do not run the privileged fixtures against the retained baseline: it lacks the temporary interfaces. Baseline measures only the ordinary WPT vector. Root owns exclusive source/app/Git hold, invocation, terminal inspection and independent restoration verification. The source/app/installed-Mochitest-tree/metadata backups and restore function are byte-identical to transient runtime v4. Concurrent source or fixture edits prevent overwrite; incomplete process cleanup retains backups. No cleanup or signing is performed by this preparation.

COMPOSED-ORIGIN.json pins the predecessor runtime inputs and source/review manifests. COMPOSED-RUN-DELTA.patch and COMPOSED-ANALYZER-DELTA.patch show the new integration changes. Inherited RUN-DIFF/CHECK-DELTA and earlier amendment files retain their historical meanings and bytes. Preparation authenticates the 14 Git source roles, all inherited inputs, exact forward/reverse patch transport, unchanged helper origins, manifest order and the exact assertion inventory. Parser controls comprise the preserved 30 WPT, 23 query, 23 recascade refusals plus 41 composed refusals and four accepted probe-count cases. No compiled output is produced or retained.
