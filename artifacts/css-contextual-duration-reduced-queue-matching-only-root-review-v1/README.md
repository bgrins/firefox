# Matching-only reduced WPT post-run verification

Root-only helper prepared before the matching-only run's terminal. No outcome has been read or assumed. `verify.py` reuses the executed broader root verification and instrumented-candidate failure-cleanup protocols, with exact predecessor diff and hash references. It authenticates activated matching-only owner `0e251cc9…` and accepts root-supplied actual session, terminal, exit and result digest.

After the actual owner terminates, root reviews and runs:

```
python3 -I -B -S artifacts/css-contextual-duration-reduced-queue-matching-only-root-review-v1/verify.py --session ACTUAL_SESSION --terminal ACTUAL_CHUNK --exit ACTUAL_EXIT --result-sha256 ACTUAL_RESULT_SHA
```

This command performs restoration verification, bounded backup deletion and raw-index reconciliation; it is not a read-only check. The separate `check.py` is synthetic-only and has already run without reading the live runtime.

The helper requires a successful matching-only build with exact source/owner/command/binary joins; independently replays the frozen two-PASS original and actual candidate raw stream under exact policy and app metadata; verifies captured fixture/resources/manifest, phase PRE/POST and built source snapshot. Complete two-PASS, one-FAIL and two-FAIL outcomes are preserved. An ordinary negative candidate must have an exact WPT comparison assertion failure, clean stream and OK ending, and owner/phase exit 1. Other failures, infrastructure errors, incomplete runs or failed restoration stop before cleanup. There is no requirement that matching-only must fail.

Independent current checks require original source bytes/identities, all accepted claims and original EC context, app/extras semantic restoration, exact flags and full restored state. The prestate comes from this owner's CANDIDATE-PRE, not a historical app/index snapshot. On a complete ordinary failure, only the owned `backups` subtree is removed, and only after its complete inventory equals BACKUPS and independent restoration succeeds. Success requires the owner already removed its backup. Original failed result/assessment remain byte-for-byte unchanged; root cleanup and raw summaries are additive.

The helper writes exclusive ROOT-REPLAY and ROOT-TERMINAL receipts, preserving exact rows/messages/outcome and recording native_acceptance false. It records symlinks without traversal and freezes regular runtime files. It then reuses the exact one-field CURRENT-EPOCH raw_index_observation.current update with ownership claim, unchanged OWNED/ROLE checks, full-state re-verification and rollback on error. It changes no semantic index, source, app, acceptance marker or count. Raw-index drift is observation, with no attribution of cause.

It is intentionally single-use. A partial root-helper interruption needs review rather than automatic retry, as in the predecessors. No build, browser, live guard, current source/app/canonical read, or mutation occurred while preparing this package. Synthetic coverage is limited to outcome admission (three positive paths and 19 rejected controls); it is not execution of restoration or deletion.
