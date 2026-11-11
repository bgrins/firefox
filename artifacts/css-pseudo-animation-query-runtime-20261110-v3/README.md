# Query runtime v3 compile correction

Runtime v2 reached real native compilation and failed because the new driver used an ambiguous Animation name with dom and layers namespaces in scope. This copied revision adds explicit mozilla::dom::Animation qualification at exactly four driver references and [[maybe_unused]] on the pending snapshot used only by MOZ_ASSERT in optimized builds. COMPILE-AMENDMENT.json pins exact substitutions and changed-range clang-format checks. No other native bytes, preference setup, task body or 208-assertion inventory changed. The new patch applies after the four original patches. V2 remains immutable; execution HEAD and retained receipt are reset. Compilation remains unproven until root runs the new candidate.

# Query-helper build and direct execution experiment

Prepared for root execution only. No native build, installed-file lint or browser test has run for this capsule. Execution HEAD and retained-build receipt are deliberately unset until the other native transaction has restored and root freezes this plan. The initial compilation is an acceptance gate, not an assumed success.

## Exact candidate

The candidate combines the frozen query-input cumulative patch with direct driver v2. V2 fixes the owning/nonowning target conversion found by independent source review; driver v1 is not used. `ORIGINS.json` and `SOURCE-ROLES.json` authenticate all bytes. There are ten native/IDL files plus one existing test manifest, with three temporarily installed test files. Two WPT fixtures are installed for both modes; the direct mochitest exists only in candidate mode.

Runtime v1 stopped before compilation: genuine manifest lint rejected per-test `prefs` for this non-xpcshell manifest. Its failed run and verified restoration remain frozen. This revision retains `manifest-order.patch` and adds only `pref-setup.patch`: remove the new section's prefs and await `SpecialPowers.pushPrefEnv` from `add_setup`. Setup reparses the unchanged inline stylesheet after enabling the prefs, because its `animation-timeline` declaration was initially parsed before setup. No global DEFAULT preferences change. The thirteen tasks and all 208 assertion bodies remain byte-identical. The pref amendment itself leaves all ten native/IDL files byte-identical. The checker reconstructs and reverses all five patches and checks the precise fixture addition. Execution HEAD and retained receipt are unset.

`bundle.py`, `process.py`, the ordinary WPT analyzer and its 30 negative controls are byte-identical to the signed owned-generation transaction. `RUN-DIFF.patch` shows the orchestration delta. Signed historical evidence authenticates the ordinary baseline vector. The source-revision bridge must contain artifact changes only; a newly landed native change requires explicit candidate/baseline reconciliation before freeze.

## Two separate gates

1. **Retained baseline:** install only the two retained WPT fixtures, run genuine WPT lint and the 12-page ordinary suite with the retained restored application. Require exactly 130 records: 118 callbacks (99 PASS, 19 FAIL) plus 12 OK harness ends, matching the authenticated historical vector and its messages/expected classifications. Restore before ending the baseline transaction. The retained browser has no new XPIDL method: the direct test is neither installed nor run, and `DRIVER-NOT-RUN.json` states this explicitly.
2. **Candidate:** install the cumulative native/IDL changes, ordered test manifest and all three fixtures. Run WPT lint, unmodified installed-file ESLint (including import-globals), and manifest lint. Run a real `mach build binaries -j6`; on failure retain the complete build log, record failure and restore immediately. No driver test may run after a failed build. On build success, run the same 130-record suite and require zero status, inventory, message or classification changes against the fresh baseline. Then run the new plain Mochitest in the newly built application.

The direct gate requires all 208 named assertions in their exact source-derived order, one PASS harness end, balanced suite/test lifecycle and command exit zero. No expected failures or intermittent allowances are accepted. It has 13 tasks: 150 diagnostics, 20 setup assertions, 36 result assertions and two pending-state preservation assertions. The driver analyzer keys real plain-Mochitest records by unique assertion message, not by its normally null subtest field; it cannot overwrite the first callback with the harness row. Failed `is` diagnostics preserve their full suffix while matching the frozen assertion name.

A failed or missing setup assertion invalidates the corresponding task's semantic interpretation. Unknown exception callbacks and incomplete tasks reject the run without asserting a native defect. Preserve `DRIVER-RESULTS.json`, the complete raw stream and command log. A numerical failure is not automatically a new bug; inspect setup and diagnostic outcomes first. The ordinary WPT gate and direct gate are reported separately; passing one cannot compensate for the other.

The awaited setup explicitly enables scroll-driven animations and typed OM before the first task. The 208-assertion inventory and task bodies remain those of the independently reviewed driver v2. Source-only checks have not calibrated the advanced pending, unresolved, transition-retarget or named-range setups in a browser. Their explicit preconditions are intended to detect failed setup rather than silently claim coverage.

## Restoration and concurrency

Root must hold exclusive native/app/source/index/config access from freeze through terminal restoration review. This wrapper uses the authenticated process-group helper and will not restore beneath a live owned process group. It checks the clean tracked tree, exact HEAD/index, mozconfig, all candidate source bases, retained sampled binaries, fixture absence and pinned test/helper metadata before installation. The runtime directory itself should remain untracked through freeze/execution so updating RUN-PLAN and receipts cannot make the tracked-tree preflight fail.

Before any mutation it backs up the full Nightly.app tree (files, symlinks and modes), existing XUL/application.ini/WPT-runner extras, the full installed `_tests/testing/mochitest` tree, and existing all-tests.pkl/test-defaults.pkl/test-installs.pkl files. Originally absent metadata files are recorded and removed if the build creates them. The fixture sources are removed and all eleven existing source/manifest files restored byte-for-byte. The indexed file state and mozconfig are rechecked. Installed Mochitest files/symlinks and metadata are restored as well as the application. On verified restoration backups are deleted; on a restoration error they remain for recovery.

The wrapper does not snapshot the entire object directory: normal compiler intermediates and build caches can remain. A subsequent native build must rebuild against restored source. This is not a claim that all build products are restored. It preserves the application used for testing, specified standalone binary extras, source/tests/index/config and installed Mochitest tree, and authenticates the relevant WPT source/metadata pins. Full process/build/test logs are retained without shell filtering.

## Preparation checks

`PREPARATION-CHECK.json` records a source-only pass: exact signed helper/evidence origins, all source bases and copied candidates, forward/reverse five-patch reconstruction, exact manifest ordering and awaited fixture preference setup, retained 130-record comparison, 30 ordinary parser rejection controls, 23 direct-parser rejection controls and a temporary-tree restoration exercise including changed files, added files and replaced symlinks. `DRIVER-CONTROLS.json` includes first-callback status/deletion/label/duplicate failures, setup failure/deletion, lifecycle/order, malformed JSON, unexpected callbacks, crash/ERROR, todo/intermittent and wrong harness-end cases. Six additional amendment controls reject lost awaiting, wrong preference value, missing stylesheet reparse, changed assertion body, global DEFAULT preferences and forbidden per-test preferences. The checker now passes -B to driver-controls.py so source-only validation does not create bytecode caches. It does not prove native behavior.

One initial preparation check rejected a naive lowercased manifest-order check; the accepted check now runs the signed real sort functions. This was a checker correction, not a native change. Full installed-file lint, binding generation, compilation and real driver execution remain root-owned gates.

## Root invocation after review and restoration

After committing the candidate/source-review work, while this execution capsule remains untracked, freeze against the restored matching build receipt:

```sh
python3 -I artifacts/css-pseudo-animation-query-runtime-20261110-v3/freeze.py <exact-HEAD> <artifacts/path/to/retained-build.json>
python3 -I artifacts/css-pseudo-animation-query-runtime-20261110-v3/run.py baseline baseline1
python3 -I artifacts/css-pseudo-animation-query-runtime-20261110-v3/run.py candidate candidate1 baseline1
```

Do not execute until FREEZE-READY.json exists and root has reviewed its exact input manifest. Failed compilation or setup is a necessary review point; do not alter the frozen inputs during a run. Final missing-pseudo CSSOM acceptance remains out of scope: this helper is invoked only by the temporary privileged driver. Provider closure, the public caller/cache/visited handling and transient recascade still need implementation and review. The final debug transform-hint traversal gate remains required.
