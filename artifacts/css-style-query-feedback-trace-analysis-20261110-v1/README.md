# Strict scheduling trace analysis

The parser accepts only a completed native transaction with successful build/WPT commands, absent owned process groups, and a complete source/application restoration receipt. It authenticates the raw log and both completion/restoration receipts. The copied `observations.py` is the original four-mode QF validator; `analyze.py` adds strict native validation and observation value types.

Native acceptance requires exact event schemas and key types; no cap or trace-error; contiguous per-PID sequences beginning at one; balanced, correctly nested style/refresh/stale/cache/method entry and exit; matching live object, document and target fields; and reconstructed StyleDocument call/depth identity. Changed rebinds must return with the requested candidate timeline. Animation index is ordering metadata only. Timeline addresses are not immutable allocation identities.

Primary restoration counts use the entire native record stream, independently of QF mode windows. Restoration means both start and hold were unresolved on entry and at least one was resolved on exit. Nested align/ready/tick records may describe the same restoration; method totals must not be added. Nullness observations do not prove identical full machine states or full-state recurrence.

QF validation covers four passing callbacks, one OK harness ending, bounded preparation, arming markers, four synchronous and twelve frame snapshots per mode. Mode summaries associate native records by captured-log order. Stdout/stderr cross-stream ordering is not proved, so these windows are secondary contextual attribution; cross_stream_phase_order_proved is false. Grouped JavaScript observations are not atomic.

The controls use synthetic native records with retained valid QF records. A positive control moves one restoration inside a style call and checks detection. Seventeen negative controls cover gaps, caps/errors, incomplete scopes, wrong scope/method/active-animation identity, incorrect depth, malformed or duplicate/extra fields, nonfinite rates, bad QF modes/phases/types, callback failure and process-fragment interleaving. These finite controls do not formally verify the parser or native implementation.

NATIVE1-REJECTION.json authenticates the original run and retains four multi-prefix records. The parser rejects it before producing a complete-trace scheduling verdict. V2 uses single bounded writes. Complete successful transport remains an assumption: an entirely unreported process or failed stream delivering neither events nor its error marker cannot be detected from this log.

Run controls.py, then analyze.py with a completed run directory. Set PYTHONDONTWRITEBYTECODE=1 to avoid cache files. Neither script mutates the browser, native sources, build, or Git. The independent logger review does not constitute a parser review.
