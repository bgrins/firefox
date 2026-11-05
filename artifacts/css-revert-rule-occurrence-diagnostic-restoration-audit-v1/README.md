# Independent occurrence diagnostic restoration audit

Prepared only. This derives from the incremental restoration checker and does not execute the experiment. Run after the owner has an **actual closed tool terminal**, with tracked/index state held. Root must first save the actual receipt at `artifacts/css-revert-rule-occurrence-diagnostic-native-runtime-v1/EXECUTION.json`. Its exact fields must match the supplied launch/session/terminal/exit arguments and include `closed:true`; this audit does not fabricate or independently obtain a tool terminal.

```sh
python3 -I -S -B artifacts/css-revert-rule-occurrence-diagnostic-restoration-audit-v1/audit.py \
  --runtime artifacts/css-revert-rule-occurrence-diagnostic-native-runtime-v1 \
  --config artifacts/css-revert-rule-occurrence-diagnostic-native-v1/CONFIG.json \
  --result RESULT.json \
  --owner-launch ACTUAL_LAUNCH_CHUNK --owner-session ACTUAL_SESSION_NUMBER \
  --owner-terminal ACTUAL_TERMINAL_CHUNK --owner-exit ACTUAL_EXIT_CODE
```

A nonzero owner exit is allowed; it does not become a passing experiment. The audit requires the owner's restoration record and independently rechecks original source bytes/inodes, library/context pins, HEAD/index/staged/unrelated diffs, baseline application and extras semantics, missing transition lock and removed backups. It checks all recorded PID/PGIDs against fresh process snapshots before and after verification. No benchmark timings are read or interpreted.

Exactly three process-receipt paths are allowed: build, wake helper and occurrence WPT. Extra, malformed, symlinked or changing process receipts fail the audit. Missing receipts are reported, not treated as proof that those processes never started. The owner’s pinned cleanup registries and actual terminal remain necessary closure evidence. Available build/failure/occurrence/trace observations are retained separately from restoration status; observations cannot make restoration success imply CSS correctness or sharing.

The audit pins and rechecks the external owner execution receipt during its checks. It preserves the original checker’s application/source/process verification logic. Preparation performs syntax checking only; no live process scan or restoration audit was run. Fresh `ps` access may require sandbox elevation.
