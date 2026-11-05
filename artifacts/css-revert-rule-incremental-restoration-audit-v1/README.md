# Incremental C independent restoration audit

Prepared only; run after the parent confirms a closed owner terminal, while tracked/index state is held. Invoke isolated Python with --runtime artifacts/css-revert-rule-incremental-native-runtime-v1 --config artifacts/css-revert-rule-incremental-native-v1/CONFIG.json --result RESULT.json and explicit --owner-launch/--owner-session/--owner-terminal/--owner-exit.

Restoration is independent of experiment success. A closed build failure or partial browser sequence can pass restoration checks while reporting incomplete/failed observations. The audit requires the owner's restoration record, independently checks original source bytes/inodes, preserved library/context pins, HEAD/index/staged/unrelated diffs, application and extras semantics, removed backup and transition lock, and fresh process absence before and after those checks. It accepts a nonzero owner exit without relabeling the experiment successful.

The exact allowed roster has nine process receipts: build/wake; correctness, controls, occurrence; long_timing/repeat-1/2 and single_timing/repeat-1/2. It rejects any extra PROCESS receipt, malformed PID/PGID, symlinked receipt or changed receipt during the audit. All recorded PID/PGIDs must be absent in fresh ps snapshots. Missing receipts are reported separately: absence of a receipt is not independent proof that a process never started. The owner’s pinned process registries/cleanup guard and actual terminal remain part of the closure evidence. Partial runs are not assumed to launch later lanes.

Available build/failure/lane/timing observations and raw benchmark report hashes are retained. Missing or malformed optional observations do not turn successful restoration into a false test pass; aggregate mismatches are reported as observation_errors. No complete-roster, all-pass, timing threshold or native adoption assertion is made by this audit. The report labels aggregate completion/validation values as claims and always records native_fix_acceptance=false.

Prepared by static syntax checking only; no live audit, browser, build, source or index action was executed. Fresh ps may require sandbox elevation.
