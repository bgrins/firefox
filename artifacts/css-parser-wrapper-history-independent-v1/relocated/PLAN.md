# Public next/whitespace wrapper bridge

Derive the actual raw whitespace/comment prefix after observer-active pending-block cleanup, preserving the existing cache. Compose primary fetch and arbitrary skip/next/save/reset histories with an independent cursor/token and annotation reference. Derive safe tracking entry from a successfully returned non-Function token, including Colon; do not assume production callers always satisfy that entry.

The raw scanner is byte-directed: space/tab advance, CR/LF/FF newline consumption (including CRLF), direct comment consumption and early return at any other byte. Stop-before does not gate this scanner. It gates the following primary fetch. Cache and tracking mode survive direct whitespace/comment scanning; annotations do not necessarily survive comments unchanged. Pending-block cleanup can observe Functions and annotations.

Reuse authenticated public-history v1 for cache coherence, name/URL classification and pending cleanup. Keep exact observer effects separate from token/cursor projection. Preserve late-enable, re-enable and annotation counterexamples. No whole-parser, metadata/native-codec/usize/compiler/heap claim. Full Rust source correspondence and focused mutations supplement universal Lean results rather than replace them.

Initial production declaration enable-entry is a separate follow-on admission, contingent on the static caller trace. Source-only artifact work; no production, WPT, Git or browser operations.
