# String and comment consumer audit

Status: no new tokenizer discrepancy established. This is source/spec review and finite extracted execution, not full formal admission or browser validation. No live native/WPT, Git, Mach, Firefox build or browser changes were made.

## Evidence

Searchfox discovery and complete local tokenizer/parser/serializer definitions are retained. The local tokenizer is pinned at 5319a01e403cd2a93bfc3dd4c53a7e5ec95129360da58c6f9f76f480ae5e6211; its indexed counterpart predates the local URL, identifier-escape and numeric repairs. Complete diffs are retained. Parser and serializer bytes match Searchfox. All reviewed string/comment functions are unchanged across that tokenizer difference.

`consumer-witness.rs` extracts 27 complete functions/methods, including quoted-string and comment loops, escape/hex helpers, byte advancement, newline/UTF-16 bookkeeping and packed line-number operations. Its small type harness substitutes std::borrow::Cow for CowRcStr, a plain Rust match for match_byte, and admits the wrapper field layout/constants. `EXTRACTIONS.json` binds every copied body. It does not execute the public Parser cache/block/skip wrappers.

An independent Python reference preprocesses code points, consumes strings by specification rules, and maps endpoints back to original byte offsets. Comments use first-terminator/EOF reference logic and preserve raw slices as an implementation observer. Both debug and release execute 298 string and 348 comment cases: 646 PASS, including decoded payload, BadString result, cursor, UTF-8 endpoint and UTF-16 line/column. Cases cover both quotes, opposite quotes, empty/ordinary/escaped EOF, CR/LF/CRLF/FF, NUL, BMP/supplementary UTF-8, one/six hex digits, surrogate/out-of-range escapes, first comment terminator and unterminated comments. This finite matrix is evidence for the proposed model, not universal proof.

A preliminary generated Rust fixture used JSON's unsupported Rust `\f` escape. Its source/compiler rejection is retained under `draft/`; the generator now emits Rust control-code escapes explicitly and uses a non-pictographic supplementary-plane letter in the final cases. This was fixture syntax, not a native defect or semantic mutation.

## Source/spec findings

| Consumer | Reviewed behavior | Verdict |
|---|---|---|
| String fast path | Borrowed slice until matching quote, EOF, escape/NUL transition, or unconsumed newline; opposite quote retained | Matches current Syntax branch behavior |
| String owned path | Decodes escapes, replaces NUL, joins escaped newlines, drops final backslash, preserves complete UTF-8 payload | No discrepancy found; UTF-8 loop invariant remains a proof obligation |
| BadString | Returns before the raw newline and leaves it for the following token | Required reconsume behavior, not independently a recovery bug |
| Comment | Consumes through first `*/`, or all remaining input on EOF; no nesting | Matches comment termination/ignoring requirements |
| Comment observers | Exposes original contents and updates source-map/sourceURL fields | Implementation extensions; not prescribed by CSS comment-token semantics |
| Public parser | Normal iteration skips comments; preserving-comment API is explicitly separate | Must be composed in full provider admission |

`SPEC-TRACE.md` gives the current primary-source paths and distinguishes scope. `PROOF-TARGET.md` lists the complete proposed obligations and external boundaries.

## Existing expected failures and prior art

`escaped-eof.html` tests a selector hash and CSSOM custom-property serialization for identifier, dimension, URL and string cases. Its local metadata expects FAIL only for identifier, dimension and URL rows. The string escaped-EOF row has no expected failure. The string consumer explicitly drops the final backslash. The raw custom-property preservation/serialization path is a separate composition target; this audit does not infer its root cause solely from metadata or propose changing string decoding.

`serialize-escape-identifiers.html` serializes a list of stylesheet rules, reparses it, then compares the serialized rules. Its expected failure concerns rule-specific identifier serialization/round-trip. It neither directly observes a string token nor localizes a failing rule. There is no evidence here that a string/comment repair would fix it.

Upstream rust-cssparser issue 393, opened 2024-10-28 and still open in the fresh retained response, reports BadString recovery and alleges a browser difference. The reported token sequence—BadString before newline, then a new string beginning at the following quote—is consistent with current Syntax tokenization. Declaration-level processing must be traced separately; see the two-row probe below. No novelty claim is made, and the issue's browser assertion is not treated as a fresh measurement.

## Root-owned optional probes

`string-comment-controls.html` contains 19 asserted admission controls, expected to pass: decoded font-family equivalence against a valid literal reference, bad-newline rejection, and comment token-boundary/EOF behavior. It compares equivalent parsed values rather than demanding one arbitrary quoting serialization. This is a candidate probe, not a proposed bugfix WPT or an observed failure.

`known-badstring-recovery.html` contains 2 distinct declaration-recovery cases for the existing issue context. With a quote after the bad newline, the new string contains the semicolon and following color text, so no separate color declaration is reached. Without that quote, the semicolon remains a token and the following color declaration is reached. These are current-spec inferences, unexecuted here; any contrary browser result requires a consumer/recovery investigation and should not be labeled a new string-tokenizer defect.

No root browser work is required merely to manufacture a discrepancy. The useful next task is universal string/comment provider admission with explicit source-state and observer boundaries.
