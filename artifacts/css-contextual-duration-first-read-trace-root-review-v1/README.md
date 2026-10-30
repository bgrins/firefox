# Disabled trace terminal and restoration verifier

This is an unexecuted successor to the reviewed progress-candidate root verifier. It binds the activated five-source trace owner a77940f4977809eef414615ebbbed9f23021e00fcf9fea67c89e826d9a534931 and its dedicated runtime. Preparation reads only immutable owner/proposal/predecessor artifacts. The live trace run and current native/application/index/canonical state were not inspected. execution_enabled remains false.

Root must provide the actual owner session, terminal chunk, exit and CANDIDATE-RESULT digest. No provisional browser result or inferred process completion is accepted as a terminal. The supported path requires a successful linked build, complete nine-callback/three-ending WPT publication, and the existing private-record/trace receipts. Build failures, infrastructure exceptions or missing publication need a separately reviewed cleanup path; this verifier stops rather than inventing missing receipts.

Both original and candidate raw assessments are replayed with their saved policy and actual application metadata. The compiled native-source map must equal all five role postimages; command, binary map, phase snapshot, source captures, metadata and process cleanup remain joined as in the executed predecessor. The unchanged fixture resources are authenticated. The old uninstrumented candidate comparison is recomputed and must equal its saved report.

Callback comparison success is separate from owner completion. A normal callback failure retains its exact owner error/exit and assessment. An all-PASS callback phase may still have an owner failure caused by the exact full-signature assertion or structural trace-capture assertion. The verifier reproduces those explicit failure branches without changing CANDIDATE-RESULT, callback verdicts or calibrated record data. Unexpected errors stop review. Numeric freshness is never a completion requirement here.

TRACE-BINDING authenticates one authoritative raw stream, sealed parser/report hashes, and the before/after generated-header observations against the configured property mapping. The parser is replayed exactly; diagnostic_capture_complete means nonempty, syntax-valid, closed, uncapped structural capture with matching header observations. It does not mean all 258 authored queries were captured. ROOT-TRACE-REPLAY and ROOT-TERMINAL explicitly state strict_join_not_run and full_authored_rosters_matched=false. The separate sealed strict joiner can run after freeze, writing outside the frozen runtime; only its successful whole-roster/value join establishes that limited alignment. It still proves neither native causality nor first freshness.

All five restored source hashes and original identities, the shared provider/context pins, accepted payloads, app/extras semantic inventories, root/nested flags and full adjusted canonical snapshot are checked. A successful owner must already have removed its backup. A failed owner may retain its exact owned backup; only after independent restoration and full inventory equality does the inherited verifier remove that directory and save ROOT-BACKUP-CLEANUP. Process groups must be absent. The original failure receipt is preserved.

Freeze retains original raw/records/trace receipts and bounded replay/analysis reports. The inherited filesystem walk records regular files and symlink targets without traversal; it does not copy binaries or inventories. The canonical update, if needed, changes only raw_index_observation.current with the existing byte-owned write and inverse rollback. OWNED and ROLE stay byte-identical. Native acceptance remains false. Root alone performs these writes/deletion after review and actual terminal.

Saved-only preparation check:

```sh
python3 -I -B -S artifacts/css-contextual-duration-first-read-trace-root-review-v1/check.py
```

After the actual terminal, root can enable only POLICY.execution_enabled, reseal FILES.json, and invoke:

```sh
python3 -I -B -S artifacts/css-contextual-duration-first-read-trace-root-review-v1/verify.py --manifest ACTIVATED_VERIFIER_SHA --session ACTUAL_SESSION --terminal ACTUAL_CHUNK --exit ACTUAL_EXIT --result-sha256 ACTUAL_RESULT_SHA
```

Do not invoke it against a live owner. It is not retry-safe after partial publication; a stopped verification requires review of what was already written. Preparation checks exercise four outcome classes, seven invalid outcome variants, a synthetic parser/header replay and three tamper controls; isolated scratch is removed. No live guard, browser, native build, Git/index operation, cleanup or canonical mutation occurred during preparation.
