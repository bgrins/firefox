# Snapshot build-failure restoration review

Disabled recovery for actual owner33133/e369a3/exit1. The failed result stays unchanged: successfalse, AssertionError(), candidate_phase null, build exit2. The exact saved build log reports GeckoBindings.h's uint8 forward declaration conflicting with the proposal's uint16 enum. There is no aggregate candidate-build/RESULT.json, browser phase, OUTCOMES or PHASES receipt. No browser result or successful compilation is fabricated.

This adapts the sealed success-only snapshot verifier. verify.py.diff shows the complete delta. All seven restored source bytes and preimage inode identities, accepted claims, source context pins, full application/extras, flags, process groups, controls and full restored state are checked before cleanup. The source/application/full-state block and raw-index-only owned replacement/rollback tail are byte-identical. The three headers absent historical canonical pins still pass the complete seven-role restoration loop.

The retained backup must have exact owned path, no symlink root, exact saved inventory including identities and hashes, and matching1,008,605,176-byte accounting. Only after complete restoration verification does root remove that owned directory. This is the executed matching-only failure-cleanup protocol. The original BACKUP-CLEANUP and failed CANDIDATE-RESULT remain untouched; a separate ROOT-BACKUP-CLEANUP records root deletion. No user data or other directory is targeted.

The actual terminal tuple and result digest are fixed in POLICY; all completed runtime input receipts and build log are pinned. Build process failure must be the ordinary recorded exit2 with no interruption, process error, cleanup error or surviving owned group. The saved traceback must identify the build helper's failed command assertion. Other failure modes are not admitted.

Root output ROOT-REPLAY/ROOT-TERMINAL explicitly reports build_success:false, browser_executed:false, observation_complete:false, comparison_gate_passed:null and owner_failure_preserved:true. The runtime is frozen after cleanup; only raw_index_observation.current may then change through the inherited owned epoch protocol. The root verifier completing successfully means restoration verification and recovery succeeded, never that the native experiment passed.

Saved check6a2866/0 joined the actual failure, seven saved source/inode preimages and raw-only PRE/POST difference and rejected20 mutated outcomes. It did not run the verifier main, inspect current native/app state, scan/delete backup contents, run Git, or mutate canonical state. The documented wake-group permission-error fallback remains in its original receipt; its recorded empty census is checked, and root independently requires fresh group absence.

Execution remainsfalse until root reviews and enables POLICY. Root command after activation:

```
python3 -I -S -B artifacts/css-contextual-duration-masked-snapshot-build-failure-root-review-v1/verify.py --session 33133 --terminal e369a3 --exit 1 --result-sha256 fe42a1c7ded1ed6f15ff17442523fd2225c37e66053c26fdf18861bbcafb6690
```

The success-only snapshot verifier remains sealed and inapplicable. No new source patch, native build, browser execution or accepted fix is created by this package.
