# Source correspondence and admissions

## Retained source identities

The complete tokenizer is the corrected identifier-guard source with SHA-256 `8a5925e228e5838ef6afcaf165b27037cf48d0daa31f0bef3d42338c30ff51ab`. Its numeric arithmetic is unchanged. The complete custom-properties source is `d7765d0a1de32f85ad7713409398282556078331e7a1b8ecc047d82b1fc789ab`. These are historical, authenticated snapshots, not a claim about later live source. The separately proposed/repaired numeric arithmetic must receive its own exact-delta integration.

`source_bindings.py` uses the retained Rust lexical reader to extract full definitions. It checks identical provider bodies against the accepted name/guard integration and verifies the exact complete numeric extraction against the static capsule. `SOURCE-BINDINGS.json` retains source bytes and byte ranges, not only selected lines. The frozen manifest authenticates that ledger before replay. The actual Rust replay compiles the full cssparser source with this tokenizer overlaid onto the authenticated dependency source. The existing `ReferenceFlags::from_unit` body, bitflags declaration and 12 length constants are extracted unchanged into the harness.

| Native source/control | Model and checked obligation | Remaining admission |
|---|---|---|
| `next_token_unchecked` digit, sign and dot branches | `NumericEntry` entry equivalence and nonempty first read/loop | Rust ASCII digit primitive, byte representation and dispatch feature correspondence |
| `byte_to_decimal_digit`, three loops in `consume_numeric` | `NumericDigits` independent literal-digit classification, maximal prefix, exact remainder and all recorded read indices in bounds | Native usize additions and valid allocation; source-to-model translation is inspected and bounded by actual execution, not a verified Rust frontend |
| Fraction/exponent short-circuit predicates | `NumericParts`, `NumericReads`: separate grammar reference, nonempty body, complete guard/read offsets and shifted bounds | `has_at_least` must complete without arithmetic overflow; native indexing/compiler contracts |
| Numeric sign/type/prefix | `NumericLexical`: all consumed bytes ASCII, native/reference result equality, cover, positive consumption | Reference shares the elementary sign stripping/outer sign observation; sign predicate is explicit literal +/- comparison, not a separate Rust standard-library proof |
| Percentage branch before identifier branch | `NumericToken`: percent excludes corrected identifier approval, hence equivalence to identifier-first reference, exact suffix, count bound | Corrected identifier source identity inherited; no assertion about arbitrary invocation of `consume_numeric` |
| `consume_name` and escape providers | Accepted name/repair modules plus `NumericBoundary`: independent decoded output/count/remainder, return marker, composed numeric prefix | Valid UTF-8 source/codec shape, char decode/encode, allocation, usize and normal-return metadata arithmetic; ownership flag is native projection only |
| `ReferenceFlags::from_unit` | `NumericUnits`: recursive ASCII-caseless comparison equals independent lowercase-list table; LH=5 and RLH=10, other relative units 1/2, others 0 | Actual Rust `eq_ignore_ascii_case` and core ASCII lowering; exact classifier body/constants are compiled and compared, but standard-library implementation is not proved |
| Both Dimension-only callers | Complete scanner and declaration bodies pinned; `tokenFlags` and selected Dimension/non-Dimension theorem | Full `parse_declaration_value_block` is source-bound, not compiled/proved as a whole here; unrelated parser/function/block behavior remains open |
| Numeric floating expressions and int option | `NumericPayload` preserves ordered expression tree and conditional clamp branch; lexical reference yields same expression | No IEEE implementation, powf, f32 cast, exact-real numeric value or universal i32 saturation-correctness theorem. Comparator/cast meaning remains external |
| `resolved_token_dependencies` suffix restart | `NumericScanner`: actual numeric entry yields positive bounded count, return boundary, exact remaining bytes and decoded-unit summary | One numeric token step only. Native string slicing contract, all other token classes, general restart equivalence, syntax validity and graph consumers remain open |

## Native arithmetic and metadata

`Parser::advance`, `has_at_least`, length/index casts and offsets use machine integers. Mathematical list proofs do not justify wraparound or allocation. Inputs and all reached native operations must be representable and complete normally. The accepted name provider reaches `ParserState::advance_line_number`, which adds `count << 2` to a packed u32. Each newline update requires sufficient headroom; ignoring metadata outputs does not remove overflow/abnormal-completion risk. No all-input headroom theorem is claimed.

The name model permits temporary positions inside UTF-8 units; only admitted return boundaries are used for slicing. A boundary marker becomes an actual Rust str boundary under the inherited valid UTF-8/codec representation relation. The proof does not assume every internal position is a boundary.

## Feature and compiler boundary

The native harness builds cssparser with fast_match_byte and fast_match_color disabled, matching the prior direct-source harness. The signed dispatch component and corrected-guard transfer retain optimized dispatch-pattern equivalence separately. This component does not compile the procedural-macro optimized configuration or prove Rust compilation. It does not replace root browser/Gecko gates.

## Floating values

The source still loses mathematically finite values through intermediate overflow/underflow. The replay retains `5` followed by 308 zeroes and `e-309` producing infinity, and longer compensated exponent examples producing NaN. Exact raw native payload bits are retained; only simple controls and the infinity witness have asserted payload expectations. Lean correspondence compares token kind, total count, decoded unit, dependency flags, sign/type flags and suffix, not f32 values. The ordered expression model preserves multiplication/addition order and percent division before cast without reassociation. Branch-selection lemmas for saturation are conditional control facts, not evidence that original intermediate arithmetic computes an exact integer.
