# Owner-map dedup independent restoration audit

Prepared only. This derives from the reviewed occurrence diagnostic audit, expands the allowlisted process/result roster to the five-lane owner, retains the actual external terminal receipt binding, and keeps explicit build/wake result mapping.

Run only after the native owner's actual terminal has been observed and recorded in its EXECUTION.json. Use the actual exit even when nonzero:

```sh
python3 -I -S -B artifacts/css-revert-rule-owner-map-dedup-restoration-audit-v1/audit.py --runtime artifacts/css-revert-rule-owner-map-dedup-native-runtime-v1 --config artifacts/css-revert-rule-owner-map-dedup-native-v1/CONFIG.json --result RESULT.json --owner-launch ACTUAL_LAUNCH --owner-session ACTUAL_SESSION --owner-terminal ACTUAL_TERMINAL --owner-exit ACTUAL_EXIT
```

The audit accepts a partially completed experiment after restoration: absent future lanes are not invented, available child and aggregate observations are retained, and missing process receipts are enumerated. It verifies exact CONFIG/owner receipt, source bytes/inodes, HEAD/index/unrelated work, application/extras semantics, absent transition lock/backups, and recorded PID/PGID absence with calibrated process censuses before and after. Malformed/contradictory observation data is reported separately; restoration_verified does not certify validation_passed or imply observation_errors is empty. Missing process receipts cannot prove no process was started. A failure before restoration completion cannot pass this audit. No audit process or census was run during preparation.
