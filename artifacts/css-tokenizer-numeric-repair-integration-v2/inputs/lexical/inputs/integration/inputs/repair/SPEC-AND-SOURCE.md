# Normative and native trace

Sources consulted on 2026-10-19: current CSS Syntax Editor's Draft, whose page identifies its draft date as 2026-10-16. These are ED citations, not claims that all text is identical to a dated TR.

1. [Input preprocessing](https://drafts.csswg.org/css-syntax-3/#input-preprocessing) normalizes CR, FF and CRLF to LF. NUL is replaced with U+FFFD.
2. [Valid escape](https://drafts.csswg.org/css-syntax-3/#check-if-two-code-points-are-a-valid-escape) rejects a backslash followed by a newline.
3. [Identifier start](https://drafts.csswg.org/css-syntax-3/#would-start-an-identifier) considers the second and third code points for the escape after an initial hyphen. Thus hyphen/backslash/newline is false; two initial hyphens are already sufficient and remain true.
4. [Consume a token](https://drafts.csswg.org/css-syntax-3/#consume-a-token) uses that predicate after an at-sign. A failed predicate returns a delimiter at-sign. A successful predicate consumes an at-keyword.
5. [Stylesheet contents](https://drafts.csswg.org/css-syntax-3/#consume-a-stylesheets-contents) dispatches an at-keyword to the at-rule algorithm; ordinary delimiter input is reconsumed by the qualified-rule algorithm.
6. [Consume an at-rule](https://drafts.csswg.org/css-syntax-3/#consume-an-at-rule) stops at a semicolon. [Consume a qualified rule](https://drafts.csswg.org/css-syntax-3/#consume-a-qualified-rule) has no semicolon stop in this top-level invocation. Consequently the correctly tokenized invalid prefix consumes the following target rule's block as part of an invalid qualified rule, which is discarded. The incorrectly tokenized unknown at-rule instead stops at the separator, exposing the following valid style rule.

Verdict: REACHED for invalid identifier start and the resulting recovery distinction. This is not a statement that an escaped newline is invalid in every CSS context: strings have different rules, and a hexadecimal escape producing a newline code point is valid here. The WPT includes the latter as a disconfirming control.

Actual retained source path:

- `next_token_unchecked`, at-sign arm: advance one ASCII byte, call `is_ident_start`, then `AtKeyword(consume_name(...))` or `Delim('@')`.
- Complete `is_ident_start`: outer nonempty guard; first-byte dispatch; inner `has_at_least(1)` guard; second-byte dispatch. The inner backslash is at index 1; its following byte is index 2. The helper `has_newline_at` checks bounds before reading and recognizes exactly LF/CR/FF.
- `consume_name`, owned-name backslash arm: rejects a newline at offset 1 relative to the backslash. On the original invalid prefix it returns the already consumed hyphen and leaves the backslash unconsumed. Correcting the predicate avoids entering this branch as an at-keyword.
- `StyleSheetParser::next` in `rules_and_declarations.rs`: leading at-sign is tokenized; only `Token::AtKeyword` chooses `parse_at_rule`; otherwise it resets and invokes `parse_qualified_rule` with nested=false.
- `parse_at_rule` stops at semicolon or curly block. `parse_qualified_rule` with nested=false stops only at curly block. The subsequent invalid selector is discarded by the style-rule parser. That final selector-validation behavior is a native/browser boundary here, not proved in Lean.

Other actual predicate callers are the hash arm, hyphen token arm and `consume_numeric` dimension suffix. The exact-change theorem applies to their predicate results too, but the WPT does not claim to exhaust those callers. A bare backslash, a backslash at EOF, double hyphen, ordinary names, and hexadecimal escapes retain their prior predicate decisions. For the hash arm, fallback `Hash` classification can differ from `IDHash`; this is expected grammar correction rather than blanket preservation of full token types.

Source correspondence ledger:

| Rust component | Lean observation | Admission |
| --- | --- | --- |
| `is_eof`, `has_at_least` | empty list / guarded second element | valid position, defined additions |
| `next_byte_unchecked`, `byte_at` | list head / indexed byte | native bounds guards, unchanged source |
| `has_newline_at` | `newlineAt` | exact 10/12/13 byte membership, EOF false |
| ASCII match arms | `nativeAscii` | independently related to `specStart` |
| `is_ascii` fallback | byte < 128 | byte domain, valid UTF-8 boundary for code-point interpretation |
| nested escape check | original offset 1 / corrected offset 2 | exact one-hunk source equality |
| `match_byte!` | ordered arm selection | signed dispatch-v2, candidate pattern regeneration |

The complete source snapshots, macro source and all helper bodies are retained. Reviewed translation and Rust compiler behavior remain explicit trusted boundaries. No claim is made about unadmitted interior UTF-8 parser positions.

Upstream check: https://raw.githubusercontent.com/servo/rust-cssparser/master/src/tokenizer.rs retrieved on 2026-10-19 still has the same nested `has_newline_at(1)`. Web cache reported retrieval age five days. GitHub issue/PR search returned internal errors; generic search did not locate a matching issue. This bounded search does not establish novelty. Searchfox discovery had DNS failures during initial investigation; retained local/source-capsule bytes, not an unverified Searchfox revision, establish this patch's identity.
