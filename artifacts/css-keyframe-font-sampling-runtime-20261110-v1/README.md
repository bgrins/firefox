# Font sampling baseline runtime

Prepared for root review/freeze; no browser/build/live-source/Git execution. HEAD remains null. The exact frozen three-case proposal has fifteen KFONT-V1 records across sync-seek, ready, reseek, unrelated style invalidation and two frames. All font/style/timing/frame values are observations, with no inferred result oracle. Before/after reads are sequential and can flush; the proposal report defines their order and interpretation limits.

Acceptance requires lint and WPT exit 0, exactly three PASS callbacks and one OK harness ending, complete lifecycle, no crash/error/out-of-range assertion events, and all fifteen unique records in each ID's declared phase order. The parser rejects malformed/duplicate JSON, wrong IDs/phases/fields/types, missing style/timing/frame metadata, nonfinite numbers, marker corruption, merged/truncated records and incomplete inventories. Nullable timing fields remain nullable; arbitrary style strings, progress values and empty frame arrays are accepted, proving no hidden font oracle. Fifty-two negative controls and two positive controls pass.

run.py, analyze.py, bundle.py, process.py and freeze.py are byte-identical to custom-property probe v2's frozen inputs. Analyzer/transaction/freeze helper bytes are additionally authenticated to signed owned-generation origin 3f8f7324. No candidate/build branch is reachable and SOURCE-ROLES is empty. One absent temporary WPT and absent metadata are installed/removed; common test-profile dump preference is pinned. The retained combined #172 receipt and artifact-only source bridge authenticate the browser. No newly prepared research artifact is falsely claimed signed.

The reviewed helpers preserve full-app/extras backup and restoration, owned process-group cleanup, binary/source/test/config/HEAD/index validation and fixture absence. Root must maintain the exclusive live transaction until independent terminal restoration review. Failed or incomplete restoration retains evidence/backups; no promise of recovery from arbitrary external concurrent writes or power loss is made. Raw logs, parsed values, exact callbacks/messages, binary samples and command/process/restoration receipts are retained.

Root invocations after review:

```sh
python3 -I artifacts/css-keyframe-font-sampling-runtime-20261110-v1/freeze.py FULL_HEAD artifacts/css-keyframe-order-combined-current-build-20261110-v1/build-result.json
python3 -I artifacts/css-keyframe-font-sampling-runtime-20261110-v1/run.py baseline baseline1
```

Freeze verifies current clean HEAD/index and live binary/config/test pins before writing ready/manifest receipts. The runtime cannot run before readiness. This is independent diagnosis of v1's own-target font setup failure; it neither attributes that failure to nearby font bugs nor modifies the main getter conformance oracle.
