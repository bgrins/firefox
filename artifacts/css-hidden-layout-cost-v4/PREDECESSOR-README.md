# Hidden-layout cost v3: startup and batch diagnostics

**Unrun additive diagnostic.** Root alone installs/runs it. V2 remains immutable. No browser, build, native source or Git mutation was performed to prepare this fixture.

The six execution inputs remain `probe.html`, `benchmark.js`, `CONFIG.json`, `run.py`, `validate.py`, `cleanup.py`. Four are byte-identical to v2; only runner and script change. CONFIG still has measurement version2 because workload/counts/validator remain unchanged. SOURCE-PINS gives exact copies and delta files show the changes.

## Controlled child startup

Only the child environment is changed: `MOZ_DISABLE_SAFE_MODE_KEY=1`, and `MOZ_SAFE_MODE_RESTART` is removed. STARTUP-ENV and SPAWN/RESULT record these choices and only whether the restart variable was inherited, never its prior value. No user profile is read or modified. Every compared source variant must use these same child settings. These disable two explicit safe-mode entry mechanisms; they do not prove that every startup obstacle is removed.

This follows a concrete source clue: the timed-out both-v2 log names `refresh-profile-instead`, used in safeMode.xhtml. BrowserGlue._beforeUIStartup opens that dialog modally when inSafeMode before command-line handling. SafeMode.h permits the macOS Option key and inherited restart flag to request safe mode independently of fresh-profile creation. V2 did not record those conditions or HTTP requests; actual prior safe-mode entry remains unconfirmed. Full retained discovery and runtime interpretation are in css-hidden-layout-cost-timeout-v1.

## Progress without interquery yields

The server writes REQUESTS.jsonl for GET/POST arrivals. Script progress POSTs are persisted before acknowledgement, with strict sequential IDs, a small stage vocabulary,4KB payload cap and300-event cap. Normal completion produces220 acknowledged progress events: script-start, config-ready, fixture-start,108 batch begin/end pairs including warmups, and result-ready. Result POSTs remain separate from progress; progress cannot satisfy final measurement completion.

Batch markers include round, slot, ordinal, kind, visibility state and count. Begin is before construction/timers, end after target removal and timers. No new await/yield is inserted inside construction, establishment, mutation loops or first/repeat/distinct/second-pass/no-mutation query sequences. All84 measured rows and13,440 reads remain as v2, including full rectangle calibrations and retained target mismatches.

Acknowledgements add scheduling/network work between batches and to whole-fixture elapsed time. Thus timings are not byte-identical to v2. Compare only equally instrumented v3 runs with the same child environment, and retain quantization/fixed-order limitations. There is no performance acceptance claim.

## Reading a timeout

- No GET `/`: no evidence that the command-line page was requested; investigate startup/navigation first.
- GET page but no script-start: script fetch/execution/receipt path remains unresolved.
- script-start but no config-ready: configuration fetch/decode or progress delivery is the next boundary.
- fixture-start then a batch-begin without batch-end: identifies a batch interval, not a specific native query. An acknowledged begin bounds the interval before any fixture construction in that batch.
- result-ready but no result: inspect result serialization/POST handling.

The45-second fixture deadline is still checked only between batches. It cannot interrupt synchronous JavaScript/native work; the75-second runner bound terminates the owned process group using unchanged reviewed cleanup. A single missing marker does not establish a native hang. If one batch repeatedly stalls, use a separately labeled reduced diagnostic with finer operation checkpoints; do not insert yields into the repeat-query benchmark and call its timings equivalent.

## Parent integration

Same CLI as v2: `python3 -I -S run.py --binary ABS --output ABSENT_EXTERNAL --label PHASE --pin NATIVE...`. Pin/copy all six execution inputs. Keep the parent terminal/noLiveGroup/errors/profile and exact source/binary/fixture gates. Stable timeout/calibration failure may continue only after verified cleanup. An uncertain cleanup or integrity drift stops remaining phases and restores. REQUESTS/STARTUP-ENV/SPAWN/RESULT and raw browser log must be retained.

Two synthetic startup-environment cases also pass: parent environment unchanged, exact child controls, and restart-value presence-only receipt. Eleven AST-extracted HTTP-handler tests passed without opening a server or browser; malformed IDs/JSON, duplicate/out-of-order identity, oversized progress and event overflow reject, while valid progress and final-result separation pass. Python AST and Node syntax checks pass. No actual startup or timing result is claimed.
