# Attribute reference origin after leading-whitespace trimming

Status: source-derived crash hypothesis; parent owns isolated browser reproduction. No native change.

## Independent expected result

CSS Values 5 [attribute substitution](https://drafts.csswg.org/css-values-5/#attr-substitution), step 6, substitutes arbitrary substitution functions in the attribute before parsing against its type. A leading whitespace token does not prevent `37px` from matching `<length>`. Every `probe.html` case must compute width `37px`; no fatal error is permitted. The script-free `crash-minimal.html` is the smallest proposed reproduction.

## Actual path

1. `AttributeTracker::query` forwards `ElementContext::get_attr`. Gecko wrapper calls `Gecko_LookupAttrValue` and converts the returned string without trimming.
2. `Cascade::update_attributes_map` calls `get_attr_value_for_cycle_resolution` for typed attr references. The latter creates `Parser::new(&attr)` and immediately calls `VariableValue::parse`.
3. `Parser::new` initializes position zero. Neither `parse_entirely` nor `parse_until_before` skips leading whitespace before invoking the callback.
4. `VariableValue::parse` saves `input.position()` before scanning. `parse_declaration_value_block` includes whitespace and records reference start/end relative to that saved position. It then stores `slice_from(start_position).trim_ascii_start()` and trims the end, without adjusting reference positions.
5. `data-x=" var(--v)"` therefore stores css `var(--v)` (8 bytes) but reference range `[1,9)`.
6. The resolver retains the universal value, follows the custom-property dependency, then calls `substitute_references_if_needed_and_apply` with the retained value. It forwards unchanged references to `substitute_internal`, which calls `do_substitute_chunk` with start 0 and end 8.
7. The reference is not an exact whole-input match. Its prefix slice `css[0..1]` is valid but wrong (`v`); after substitution `cur_pos=9`, so suffix slice `css[9..8]` is invalid. Rust bounds checking should panic. The analysis does not claim memory corruption.

No offset rebasing was found in the inspected constructor→map→resolver→substitution chain. Parent should run each query case in a separate process because a failure can abort content.

## Controls

- `plain`: no leading whitespace, same substitution.
- `literal`: leading whitespace without any reference; exercises trim but no offsets.
- `comment`: leading comment retained rather than trimmed.
- `trailing`: trailing whitespace trimmed after the reference; reference end still valid.
- `tab`, `newline`: other trimmed leading ASCII whitespace.
- `nested`: leading space followed by `calc(var(--v))`, tests nested reference origin.

## Repair boundary to assess after reproduction

Prefer establishing one consistent origin before recording references in `VariableValue::parse`, rather than compensating each consumer. A caller-only skip can address this path but leaves the constructor contract dependent on every caller. A blanket `skip_whitespace` also skips comments and can change retained serialization, so it is not automatically the minimal semantics-preserving repair. Rebase all nested ranges or advance only the exact discarded ASCII prefix before capturing the origin; inspect tokenizer normalization and closure repair interactions. No patch proposed yet.
