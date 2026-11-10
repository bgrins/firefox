# Atomic-line diagnostic logger

This capsule supersedes only the diagnostic logger from `../css-style-query-feedback-instrumentation-20261110-v1/`. Native1 proved the original three-stdio-call logger allowed process fragments to interleave; its complete trace is rejected in `../css-style-query-feedback-trace-analysis-20261110-v1/NATIVE1-REJECTION.json`.

All normal records are formatted in a 512-byte stack buffer and emitted using one write of at most 511 bytes, within the POSIX minimum PIPE_BUF. Cap and error records also use one bounded write. EINTR retries only an unsuccessful system call. Prefix/body formatting overflow, partial write, and other write failures invalidate tracing, attempt an explicit trace-error record, and disable later logging. A permanently unwritable stderr may also prevent that marker; a complete successful transport remains an explicit capture assumption. No source getter, sampling, timing, or traversal behavior changes from the original diagnostic.

Enable MOZ_CSS_FEEDBACK_TRACE=1. Preserve all original interpretation limits: process-scoped sequence; exact balanced method/style/sampling scopes; no cap/error acceptance; pointer identity only during live intervals; animation index is ordering metadata, not allocation identity; timing nullness does not prove full-state recurrence. Main-thread assertions and the 20,000-record cap remain.

`prepare.py` regenerates four copied sources from the same frozen native basis and `logger.inc`. `check.py` verifies the four Git source hashes, exact scratch patch application, and reverse restoration. Native compilation/runtime are owned by the root agent. Independent V2 review is in `../css-style-query-feedback-instrumentation-review-20261110-v1/`.
