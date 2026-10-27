# Disabled hidden SVG browser diagnostic

`ready_for_execution` is false. No browser, build, source, WPT or index operation has been run by this draft.

The fixture and validator are byte-identical to the reviewed eight-row SVG audit (`5b2b762f…`). This adapts the installed-client browser driver and imports the existing OOF capture function, process cleanup, snapshot and batched index validators without changing their implementations. `DRIVER-DELTA.patch` shows the driver changes.

The initial gate authenticates the actual successful OOF trace/restoration seal `0bbbfcb6…`, its root receipt, BEFORE=FINAL, 49 guarded source files, all 337 source/resource/binary pins, and the restored Firefox `a783e8…` / XUL `bce392…` hashes. It reuses the trace's installed-epoch adapter to recover the exact two installed112 WPT hashes/inodes and native inventory, then joins the added display-list guard and actual restored binaries. The installed working fixes/prototypes are the source role; this is neither a HEAD-only build nor a newly installed candidate. The prior installation binary hashes are never used as current binary pins.

Before launch and after capture, verification preserves HEAD90, the exact 925 staged paths/payloads/index entries, native diff and 26 modified-native identities, all role pins and absence guards, and both installed112 WPT inodes. The operational test list is those two existing files; `install` is empty. No source or WPT restoration is needed because the driver does not write either tree.

The existing capture helper uses an exclusive new profile, one bounded JSON POST, a 45-second browser wait, owned process-group cleanup, profile identity checks and HTTP cleanup. It retains failures and before/after pin receipts. Safe-mode/update startup settings are inherited from the reviewed helper; both earlier native trace environment variables are removed. Cleanup limits remain those of the existing helper, not a promise of recovery after arbitrary OS/process failure.

`SUMMARY.json` retains every observation, null result, calibration check and first/repeat/recovery match. Completion requires all eight calibrated and stable, all four visible first-read controls correct, all eight explicit-layout/reveal controls correct, and local-shape BBox checks. The getBBox-only recovery matrix is diagnostic data. Hidden first/repeated outcomes have no mandated PASS/FAIL pattern; unexpected outcomes are retained rather than relabeled as predicted failures. Diagnostic completion does not accept a bug.

`check.py` compiles Python syntax, authenticates the archived epoch and joins, and verifies exact copied inputs without launching a browser or probing live source/index/binary state. Its receipt is `STATIC-CHECK.json`.

Root activation: copy this capsule to a fresh runtime directory directly under `artifacts`, change only CONFIG readiness to true, reseal DRAFT-FILES, then run:

```
python3 -I -S artifacts/<runtime>/run.py <activated-DRAFT-FILES-sha256>
```

The current source and binary epoch must still match. Local HTTP binding/browser launch may require the previously used sandbox escalation. No build command is present.
