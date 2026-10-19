# Source admission ledger

## Fresh parser and restart state

`Parser::new` initializes position/line/block state to zero, no delimiter mask, dummy cached start `usize::MAX`, no observed functions/source directives, depth zero. `next_including_whitespace_and_comments` first calls `skip_block_at_start`; fresh low block bits are zero, so this does not enter the recursive/nested skipper. Nonempty input then admits `next_unchecked`. The cached start cannot equal zero. Each suffix therefore uses exactly the native lexical dispatcher once, including its opener effects, then discards that parser.

`next_unchecked` requires no pending block. A reference flat lexer must clear only pending block bits between raw token calls. Repeated ordinary public `next()` is NOT that reference: it skips blocks. The proposed theorem must not compare these two different operations.

Lexical byte helpers read input and position. Column/line metadata is updated for diagnostics; arbitrary-function/source-map/source-URL tracking records observations. These fields do not select token kinds or decoded names in the complete tokenizer. Current block depth/limit is unused by direct lexical dispatch. Future theorem: for the same remaining valid UTF-8 bytes, two legal lexical states produce equal token payloads and consumed byte counts, ignoring these diagnostic effects, provided arithmetic is defined. This is source-reviewed, not kernel-proved here.

## Progress and valid UTF-8 endpoints

| Provider | Entry admission / positive progress | Endpoint reason to formalize |
| --- | --- | --- |
| Direct delimiter/match/opener arms | Nonempty input; ASCII advance by 1/2/3/4, with prefix guards for multi-byte operators/CDO/CDC | Known ASCII prefix; boundary preserved |
| `consume_whitespace` | Dispatcher guarantees whitespace; first call advances one ASCII whitespace or CRLF | Repeated ASCII whitespace; stops before a complete scalar |
| `consume_comment` | Dispatcher has `/*`; first advances 2 | Inner steps can temporarily be inside UTF-8; returns only at ASCII `*/` or valid source EOF |
| `consume_quoted_string` | Opening quote guaranteed; first advances 1, including later BadString/EOF paths | Returns at ASCII quote/newline/EOF; escape path constructs UTF-8 via scalar encoding and copies complete sequences |
| `consume_numeric` | Dispatcher lookahead guarantees at least one digit after optional sign/point | Sign/digit/exponent/percent bytes ASCII; optional name tail inherits name admission; floating result does not decide consumed unit bytes |
| `consume_ident_like` / `consume_name` | Dispatcher/is_ident_start guarantee a valid name start, or NUL/non-ASCII/escaped-EOF name case | Fast name loop can consume only part of a scalar; continuation paths finish it before any ASCII delimiter or EOF return. Backslash followed by newline is a stop, but cannot be the sole admitted name start |
| `consume_unquoted_url` | Already consumed name and `(`, so overall token is positive even when this helper returns Err without moving | Initial whitespace lookahead is ASCII; quoted URL returns Function at the original `(` endpoint. It must not consume looked-ahead whitespace. Nonquoted branches stop only at complete boundaries |
| URL internal/end/bad recovery | Overall ident-like prefix already positive | ASCII delimiter/EOF exits; escaped chars encoded as UTF-8; source sequence copying needs the same complete-scalar invariant as names/strings |
| `consume_escape` | Backslash already consumed; next byte not newline; EOF allowed | Hex scan <=6 ASCII bytes, optional whitespace/CRLF; scalar replacement/encoding; nonhex `consume_char` advances one scalar |

A proof about `Parser::advance` alone is insufficient: it intentionally permits UTF-8 leading bytes and may leave the cursor inside a scalar. The relevant invariant is at lexical **return** boundaries. Similarly a blanket helper-returns-positive premise is false: the URL quoted fallback and `consume_name` at a non-name input can return without consumption. Their actual callers provide the needed prefix/admission. No theorem here assumes those false blanket contracts.

## Arithmetic and source size

`ParserState` packs line number and block tag into one u32. `advance_line_number` uses ordinary addition of `count << 2`; Rust debug overflow checks and release wrapping differ. A single enormous whitespace/comment token can visit many newlines. The source-level bounded theorem should require enough headroom (for example fewer than 2^30 counted newlines), plus defined `usize` lookahead additions. Diagnostic wrapping does not by itself prove all Rust executions are equivalent.

`VariableValue::push` has a 2 MB growth guard, but it does not by itself establish a bound for every constructor, unchanged borrowed result, arbitrary attribute/environment value, or imported persistence source. This audit does not turn that local check into a global admission invariant. The existing 300,000-level test demonstrates finite stack behavior, not arbitrary-memory success or arithmetic safety.

## Feature configuration

Gecko's style dependency enables cssparser defaults. The retained root Cargo lock pins cssparser and cssparser-macros to the same upstream revision. `fast_match_byte` switches from direct Rust match to the real procedural macro; this is the feature gate addressed by the accompanying proof. `fast_match_color` selects color-name machinery and is not on the lexical `resolved_token_dependencies` path. Optional serde/malloc derives are not token-kind branches. Rust/syn/quote/code-generation and optimizer semantics remain external; no optimized Rust build was run here.

## Next useful proof

After dispatch equivalence, implement a byte-to-scalar boundary invariant for complete `consume_name`, including its fast ASCII/UTF-8-leading run, continuation-byte handling, escaped newline stop and owned-buffer branch. Prove the hex escape's exact <=6 prefix and scalar replacement separately, then compose name progress under actual `is_ident_start` admission. This directly covers decoded Dimension units and recognized substitution names. String/comment/URL and numeric providers still need their full corresponding invariants before closing the scanner's universal suffix-restart theorem.
