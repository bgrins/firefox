# Source review of the proposed constructor repair

Reviewed exact candidate `e3c5f24c1478ea9b1232748814b971939bf8b4895344b0717fdb3622ee7f3a20` and adjacent native.patch. Source-level approval for the narrow crash repair; candidate runtime is the parent's separate gate.

- WhiteSpace consumes the complete tokenizer whitespace run before capturing origin. Non-whitespace (including comments) resets position and pending-block state; the normal scanner then receives that token from the retained cache.
- Parser reset does not roll back observer flags or source URL metadata. Here no enable/query/disable transition occurs between the speculative read and real read. A Function observed on first lexing remains observed; the cached replay does not need to observe it again. A comment metadata observation is the same first comment the original scanner would read, before any subsequent comment. This is a local source argument, not a general cache-history theorem.
- EOF/non-whitespace errors reset and the actual parse keeps its prior behavior. Empty and whitespace-only values remain empty; comments stay in css. VT and NBSP are not consumed as CSS whitespace.
- Native constructor callers must enter without an unconsumed pending block: raw Parser creation does; ordinary declaration entry is after colon; LinkParameters and typed syntax are inside the corresponding parse_nested_block callback. A fully arbitrary Parser with pending block state is outside the source admission. The lookahead, like original next(), skips a pending block; do not claim arbitrary-parser observational equivalence.
- Block delimiters and nested callbacks keep the parent source coordinate system. Capturing the origin after whitespace means nested reference and fallback positions automatically use the same retained origin; no recursive mutation is needed.
- The patch removes only start trimming; end trimming and missing-closure repair remain unchanged. Their independent contracts and existing regression gates remain necessary.

No source concern requires broadening this patch. A separate end-trim/token-metadata hypothesis is retained below and must not be silently included in its claim.
