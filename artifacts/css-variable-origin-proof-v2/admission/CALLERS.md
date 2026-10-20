# Constructor admission and proposed repair

The source snapshots are pinned in SOURCE-PINS.json. Discovery used Searchfox for the concrete and two discovered alias names (`VariableValue`, `ComputedPropertyValue`, `CustomVariableValue`); this is an inspected call-site inventory, not a compiler-derived proof that no generated alias can call the method.

| Entry | Initial parser position | Consequence |
|---|---|---|
| `PropertyDeclaration::parse_into`, custom branch | Calls `input.skip_whitespace()` before saved state and attempted CSS-wide parse | Ordinary declaration prefix already normalized; failed try_parse restores normalized state |
| noncustom deferred helper | Receives the same saved state from parse_into; resets before VariableValue::parse | Same normalized origin |
| `get_attr_value_for_cycle_resolution` | Fresh Parser over exact attribute string, no skip | Confirmed failing constructor path |
| `SpecifiedValue::parse` universal branch in properties_and_values/value.rs | Forwards supplied parser directly | No local leading-whitespace guarantee; typed-attribute/universal callers must not be trusted to normalize it |
| `CssEnvironment::get` custom link parameter | Fresh Parser over stored OwnedStr | String is normally already trimmed by LinkParameters parse; this is an indirect producer assumption, not enforced here |
| `LinkParameters::parse` | Immediately after comma, no skip | References can be misaligned temporarily, but this caller discards them and keeps only parsed.css; later parsing starts over |
| style-range `parse_for_style_range` | Explicit skip, saves function start, reconstructs Parser over slice beginning at Function | No leading prefix in reconstructed input |

## Preferred minimal robust change

Normalize the constructor's origin before recording any reference. Consume a leading whitespace token using `next_including_whitespace_and_comments`, restoring parser state if the token is not WhiteSpace, then capture start_position. Keep comments in the stored css. The tokenizer consumes a contiguous CSS-whitespace run, including CRLF as its original byte extent. A central fix establishes the contract for all callers and all nested fallback references at once.

A simpler `input.skip_whitespace()` also establishes safe origins, but additionally discards leading comments. That is a wider serialization difference than this crash requires. A caller-only skip in get_attr_value_for_cycle_resolution leaves other constructor paths dependent on undocumented normalization. Recursively rebasing every reference/fallback after trimming can preserve the output but is more invasive and easier to incompletely implement.

Rust's `trim_ascii_start` excludes vertical tab (U+000B), matching the relevant whitespace set; do not replace it with Unicode `trim_start`, Python's general whitespace set, or locale whitespace. VT/NBSP should remain non-whitespace tokens and invalid in the length fixture. Source: https://doc.rust-lang.org/std/primitive.u8.html#method.is_ascii_whitespace (verified during this audit).

No production patch is authored here. The parent owns final design and application.

## Predicate for a meaningful offset proof

For every successful stored VariableValue, including recursively nested fallback references:

- all ranges are ordered byte offsets within the *stored repaired CSS string*, at UTF-8 boundaries;
- each reference start/end identifies the same substitution-function component scanned by the parser;
- fallback start and inferred end identify the original fallback after whitespace handling and inserted closure repair;
- the saved source origin equals the start of the stored CSS before end repair/trimming, so no dropped prefix changes the coordinate system;
- trimming trailing whitespace cannot delete any reference closing extent;
- appending closing delimiters/removing quoted EOF backslash preserves every previously completed reference and correctly adjusts incomplete containing references.

The constructor theorem should compose with do_substitute_chunk's monotone cur_pos, valid source slices and output-byte taint append law. An arbitrary list of prevalidated ranges does not prove the native constructor establishes these predicates. Existing quoted-EOF endpoint/parity repairs are relevant predecessor obligations, not a reason to assume them.
