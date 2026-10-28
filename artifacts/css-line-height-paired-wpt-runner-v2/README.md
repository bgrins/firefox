# Line-height WPT runner v2

This successor preserves the exact six pages,34 assertion identities, captures, manifest and assessor from v1. The only publication repair removes run.py's conflicting oracle_caveat override. The assessor is the single source of that field; augment_assessment adds only provenance fields and rejects any collision with assessed keys. No raw status/message/expectation/intermittent comparison is weakened. Frozen v1 and its real failure remain unchanged.

The preparation control runs the actual augmentation function used by main, JSON-serializes its result and replays the full assessment. It exercises both synthetic paired-original validation and all34 real historical original raw events. Reinstating v1's override produces exactly the known oracle_caveat mismatch. These offline controls do not adopt the historical run as the new original; both new browser phases are still required.

New signing state: HEAD19ec304f1e043ff66e2fdf7c19e73c5ce3cc4ed4, canonical epoch snapshot349bcd04cd155ef603886a1e08c30fa639bf5a73d69901664bab5059b889ee6a. SIGNING-BASELINE-EPOCH.json is an exact read-only snapshot and v34 FINAL-CHECK is pinned. The ordinary clean-index epoch guard replaces v1's historical staged165 adapter. Phase epochs must retain the signed baseline pins/identities/nested/recovery/staging state except font and four built binaries, with exact original/candidate font scope. Each original/candidate still binds its actual successful local build receipt and exact saved build epoch, never canonical CURRENT during execution.

Fixed owner: artifacts/css-line-height-reversible-pair-runtime-2. Marker/schema and invocation are unchanged:

```
python3 -I -S -B artifacts/css-line-height-paired-wpt-runner-v2/run.py CAPSULE_SHA original-1 ABS_OWNER/original-build/EPOCH.json EPOCH_SHA ABS_OWNER/original-wpt
python3 -I -S -B artifacts/css-line-height-paired-wpt-runner-v2/run.py CAPSULE_SHA candidate-1 ABS_OWNER/candidate-build/EPOCH.json EPOCH_SHA ABS_OWNER/candidate-wpt
```

Outputs must be absent. Root's reversible owner builds, runs and restores; this runner does not mutate source, index, binaries or runtime controls. It copies frozen inputs into a private WPT root and retains the existing process-group timeout, cleanup, resource/application metadata and pre/post preservation checks. The candidate repeats exact original inventory and raw replay checks. All12 targets must pass;22 regression signatures and all6 harness ends must remain exact. Existing flaky metadata is preserved and does not permit silently changed results. Original complete FAILs are observations; no automatic native acceptance follows.

Preparation was artifact-only: Python syntax, exact payload/capture equality and synthetic plus historical saved-data controls. No browser, build, main runner or live preservation guard ran. Actual phase bindings remain the reversible owner's responsibility. Backup cleanup and forced-process recovery belong to that owner, not this runner.
