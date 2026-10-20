# Backslash/newline proof extension proposal

This is a proposal, not an implementation or accepted theorem claim. It uses the completed source-review findings in css-variable-backslash-newline-review-v1 and the retained source pins in READ-PINS.json. Root owns native/WPT packaging; no production or browser work belongs in this extension.

## Recommended representation

Keep TerminalSpan.Kind as the native serialization-class projection. Add an orthogonal lexical role to each raw outer token: WhiteSpace, DelimBackslash, or Ordinary. Backslash delimiters currently project to serialization class Other; the class alone cannot distinguish them from an ordinary `&` delimiter. A new lexical role preserves that distinction without inventing a new native serialization class.

Require role/class consistency, nonempty raw spans, and DelimBackslash's exact raw byte `[0x5c]`. WhiteSpace raw spans must be actual CSS whitespace, preserving CRLF as two raw bytes. Ordinary spans remain unrestricted at their end: escaped SP/HT inside an identifier must not be silently excluded. Comments are Ordinary with DelimSlash metadata. Nested blocks are one outer opener summary whose raw span includes the whole block; internal whitespace is not outer terminal whitespace.

Name the native source admissions separately:

- Finite, source-order, nonoverlapping raw token partition and exact serialization/lexical-role projection.
- Adjacent WhiteSpace tokens are coalesced because consume_whitespace consumes the maximal raw run.
- Every DelimBackslash has an immediately following WhiteSpace token whose raw span starts with LF, FF or CR. Native EOF backslash takes the identifier path; it is not a terminal DelimBackslash.
- InitialReady/EOFReady, recursive outer-span ownership, reference bounds and machine-size/UTF-8 conditions remain explicit, as in the accepted predecessor.

## Independent suffix reference

Reuse the predecessor's right-to-left split into a nonwhite-ended prefix and the complete terminal whitespace suffix. Decide preservation from that independently computed partition: keep the whole suffix exactly when it is nonempty and the prefix ends with DelimBackslash. Otherwise remove the suffix. The reference must not read either implementation flag or the scanner's trailing-length field.

Prove reconstruction and classification for arbitrary finite lists first. Under coalescing, show the whitespace suffix is empty or a single token and derive its exact byte width. Only then connect the source-shaped scanner to the reference.

## Source-shaped integration

Extend the scanner state with the previous-token Backslash bit. On WhiteSpace, set trailing length to zero if that previous bit was true, otherwise to the exact raw width; on every other token set trailing length to zero. Then replace the bit with whether the current token is DelimBackslash. Preserve the existing first/last/last-nonwhite class updates.

The key theorem is about the final trimming decision and extent. It must not equate the final previous-token bit to the standalone persistent flag: the integrated bit is false after the terminal whitespace token, while the persistent flag can remain true.

Target conclusions:

1. Integrated trailing extent equals the reference removed suffix width.
2. Stored bytes equal the reference retained bytes, preserving the entire required newline/mixed-whitespace run.
3. First/last outer metadata describe that retained list. A protected suffix leaves last metadata WhiteSpace; an ordinary removed suffix selects the last nonwhite metadata.
4. Every reference slice already bounded by the retained prefix remains byte-identical. Deriving all native bounds stays outside this theorem.
5. EOF completion is a separate partition: under EOFReady, completion has a terminal nonwhite outer token and no whitespace trim. Do not infer arbitrary tokenization equivalence from this fact.

## Standalone preservation guard

Define the standalone accumulator independently: replace its bit on nonwhite tokens and leave it unchanged on whitespace. Prove its guard agrees with the reference protection decision on admitted tokenizer streams. A weaker conditional theorem for streams ending in whitespace needs coalescing but does not need to assert anything about an EOF backslash.

Compare preservation decisions, not full stored output. The standalone source still uses its base's trim_ascii_end and retains repair85's escaped-SP/HT defect. The native reviewer found and removed exactly those unrelated WPT controls. Full constructor equality would therefore be false and must not be asserted.

## Recursion and fallback

Represent a fresh scan accumulator per parse_declaration_value_block invocation. An outer function/block token resets the Backslash bit according to its outer role. Inner return flags are discarded by the outer loop; fallback tuple destructuring also discards the new summary. Prove this frame property on the represented callback interfaces, with complete source bindings to both scanner signatures, return tuples and fallback destructuring. Do not flatten nested token lists and accidentally let an inner Backslash protect outer whitespace.

## Required challenges

- `[Backslash, WhiteSpace(LF), WhiteSpace(SP)]` distinguishes immediate and persistent accumulators without coalescing. This is an inadmissible native stream and a necessary premise witness.
- A terminal abstract DelimBackslash distinguishes the flags when no-following-token validity is dropped. Native EOF behavior must remain the separate identifier/repair case.
- Backslash versus ordinary `&`, which share Other serialization metadata, demonstrates why lexical refinement is required.
- Missing preservation reproduces the original LF/CR/FF/CRLF suffix loss; one-byte preservation fails mixed runs and raw CRLF extent.
- Escaped SP/HT inside an identifier remains Ordinary and exposes the standalone repair85 difference without reclassifying content as whitespace.
- Comment/block reset, nested local-state reset, fallback summary disposal and EOF-closer cases prevent state leakage.

## Validation and closure

Reuse the native review's four variants and 73-case extraction receipts as source calibration; avoid new browser runs. Add selected exact model/native raw-byte and metadata comparisons only where they test these new obligations. Audit theorem premises and standard axioms, compile meaningful mutations, and require an independent review.

All new Python entrypoints must put the explicit isolated/no-site/no-optimization guard immediately after builtin import sys, before other imports. Any reusable capsule should use the corrected strict lstat manifest roster and authenticate before dispatch.

The resulting closure is a source-bound terminal-newline preservation component. It does not establish full CSS serialization, general retokenization, provider evaluation or whole Stylo parser correctness.
