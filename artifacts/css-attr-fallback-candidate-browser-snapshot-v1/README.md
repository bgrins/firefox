# Candidate browser retained for final regression validation

Root's read-only capture waited for the successful candidate build receipt, verified the exact standalone custom_properties.rs candidate and all recorded rebuilt binary hashes, then copied the application with symlinks dereferenced. It required identical file hashes, sizes and modes before/copy/after, unchanged source and receipt, and unchanged rebuilt binaries. No active source, application or index was written.

The resulting8327-file archive is819801860 bytes. Its exact owned path and inventory are in SNAPSHOT.json. It belongs to the candidate role built from native e86 plus the standalone selected-fallback taint patch, not a signed new native commit. Capture completed at03f33f/session57578/1b44d8/exit0.

Retain this copy only while final28-case WPT validation needs it, then remove the exact owned parent after checking no process uses it. Do not commit browser binaries. This copy alone supplies no test result or fix acceptance.
