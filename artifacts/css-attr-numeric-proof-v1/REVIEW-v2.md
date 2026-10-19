# Design review, version 2

This is the model author's review; independent review remains a separate gate.
This version corrects the concrete storage-type mismatch caught by the native
build and the missing seconds unit caught by independent review. It retains the
version 1 artifacts as historical evidence; successful version 1 preparation
did not establish that its candidate compiled in Gecko.

## Specification and source map

| Rule | Native implementation | Verification boundary |
| --- | --- | --- |
| Values 5 `attr-notation`: parse the number keyword as a number token; unit forms first perform that same parse | `substitute_one_reference`, `AttributeType::Unit` | Lean exact token grammar; cssparser bridge |
| Syntax 3 `parse-grammar`: normalize, parse component values, match the whole grammar | `expect_number` followed by `expect_exhausted` | No significant suffix may survive |
| Values 5: turn that number into a dimension or percentage with the given unit | Exact number lexeme followed immediately by `SortKey::as_ref()` | Abstract construction theorem; finite tokenization/value checks |
| Values 5 `attr-substitution`: failure selects fallback | Existing `None` primary and outer `do_substitute_chunk` | Branch-selection theorem; recursive evaluation excluded |
| Attribute-derived primary is tainted | Existing `Substitution::from_value(value, true)` | Primary-taint theorem; consuming-property behavior excluded |

Primary references:

- https://drafts.csswg.org/css-values-5/#attr-notation
- https://drafts.csswg.org/css-values-5/#attr-substitution
- https://drafts.csswg.org/css-syntax-3/#parse-grammar
- https://drafts.csswg.org/css-syntax-3/#consume-token
- https://drafts.csswg.org/css-syntax-3/#consume-comment
- https://drafts.csswg.org/css-syntax-3/#consume-numeric-token

Values 5 explicitly links its number parsing to the CSS grammar algorithm. That
algorithm normalizes a string into a token stream. Syntax token consumption
consumes comments and returns no comment tokens. Consequently comments around
one number are harmless, but a comment between two numbers does not join those
numbers: `10/**/20` is rejected. EOF inside a comment is a recoverable tokenizer
parse error; `10/*` still leaves one number. The model's comment constructor
represents ignored input trivia, not a claim that normative token streams emit
comments. The bridge includes these cases; the initial WPT deliberately avoids
depending on the comment extension of the oracle.

`skip_whitespace` in `tokenizer.rs` handles space, tab, LF, FF, CR and comments.
`Parser::expect_number` uses `next`, which consumes the number token.
`slice_from` ends at the current byte position. `expect_exhausted` calls `next`
and restores its original state, so taking the slice before it makes exclusion
of trailing trivia explicit. A non-number token rejects immediately; a number
with any remaining significant token rejects at exhaustion. No raw attribute
text is appended after the exact slice has been selected.

The source gate retains the complete enclosing substitution function so changing
the primary taint bit, unit serialization category, or fallback call is rejected.
The model theorem does not derive that source identity from Rust operational
semantics. The bridge compiles the candidate numeric body against the pinned rlib,
which is stronger finite evidence than merely matching source strings.

Do not replace lexeme copying with generic float formatting: negative zero,
explicit signs, exponent notation, overflow, and percentage rounding introduce
extra obligations. The existing serializer also has special exponent-like unit
handling. Every currently accepted unit spelling is exercised in the bridge.

The old prefix-only model has a proved counterexample. The Rust PrefixOnly
mutation rejects the proposed exhaustion gate and must fail a malformed-input
assertion; KeepRawInput and KeepLeadingTrivia must fail an explicit output oracle;
OmitUnit must fail numeric-token construction. These failures distinguish the
two accepted bug mechanisms without relying on the consuming property's late
invalidation to stand in for attr fallback.
