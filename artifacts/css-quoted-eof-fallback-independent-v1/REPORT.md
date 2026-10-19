# Independent quoted EOF adjudication

## Findings

Root's browser evidence establishes three distinct recovery defects. This review inspected the exact tests, result receipts, raw logs and complete relevant source; no browser was run by the reviewer. Raw/console digests match both copied receipts.

1. **Reference endpoint after deletion:** the three-case fallback probe crashes in do_substitute_chunk with byte index 25 outside `var(--absent, "example")`. The raw root receipt reports CRASH, not individual PASS statuses for the earlier tests. Source causality is direct: VariableValue::parse removes the terminal backslash after enclosing reference.end values were recorded. Every enclosing end after that deletion is one byte too large.
2. **Even terminal backslashes:** the separate 22-case semantic probe reports four failures for positive even trailing slash runs at EOF, both quote kinds. The tokenizer decodes each pair to a literal backslash, but parse's unconditional last-byte pop changes the token when the closing quote is appended.
3. **Escaped terminal quote:** the same probe reports four failures for odd slash runs before a final quote. The source's token_slice.ends_with(quote) condition mistakes that escaped quote for the string delimiter, omits the real closer, and subsequent `, serif` becomes string content.

The semantic gate has 8 FAIL / 14 PASS; odd slash EOF, genuine final quote and the two earlier fallback controls pass. These are computed-value differences with a decoded-string oracle. They do not depend on the disputed exact spelling of escaped U+FFFD in unregistered custom-property serialization.

## Oracle and caller admission

[CSS Syntax string consumption](https://drafts.csswg.org/css-syntax-3/#consume-string-token) treats a backslash at EOF as ignored, pairs of backslashes as escaped literal backslashes, and a backslash before a quote as literal quote content. EOF returns the string token. Nested function/block EOF recovery returns the accumulated component values. [CSS Variables substitution](https://drafts.csswg.org/css-variables-1/#replace-a-var-function) selects a fallback for the missing variable, and the substituted value is parsed in the receiving property's grammar. A fully quoted literal family list is therefore an independent reference for the resulting font-family computed value. No actual font installation or glyph metric is required.

The root semantic oracle computes literal content from pair count and quote parity, serializes that known content with explicit escaping, appends a generic family outside it, and compares computed font-family. Retaining the generic suffix makes swallowed delimiter/content observable. This tests decoded content and component structure, not a discretionary raw spelling. Both asserted reference acceptance and target custom-value acceptance prevent an empty-value false positive.

Complete native chain read: parse_non_custom_property_declaration_value_into detects arbitrary substitution, resets and calls VariableValue::parse; custom-property declarations call that same parser directly. parse_declaration_value and its complete recursive block parser record source intervals and missing closers. VariableDeclaration::substitute_variables calls substitute/substitute_internal; substitute_one_reference selects the missing-variable fallback using `[fallback.start, reference.end - 1)`. do_substitute_chunk slices these bounds and its final `[cur_pos, end)` suffix. The last subtraction assumes reference.end follows an actual closing parenthesis in the stored buffer.

The endpoint crash is REACHED. The two semantic preservation obligations are REACHED by the independent decoded reference and root runtime. Native reference bounds and repaired token semantics still need separate implementation validation; this is not a formal proof or proposed patch acceptance.

## Repair boundaries

Keep three independently reviewable repairs. An endpoint-only patch must correct bounds for the bytes its actual current deletion predicate removes; it must not silently claim parity or terminal-quote semantics fixed.

For any actual one-byte deletion at source position d, offsets at or before d remain unchanged, and later offsets shift by one. All enclosing reference.end values need adjustment, including references stored inside fallback.references. Earlier closed siblings do not. start/fallback.start are before the terminal deletion in this case. Merely decrementing every reference globally corrupts earlier siblings; correcting only the outermost end leaves nested fallbacks unsafe.

Preferred narrow design is parser-time recovery metadata: determine whether a byte will be deleted before computing the enclosing endpoints, and apply exactly that same decision during final buffer construction. A post-pass offset map can work but needs recursive coverage and adds another traversal. Repeatedly reparsing the whole value or changing generic token serializers is unnecessarily broad.

Parity and quote-closure patches should change the recovery predicates, not the tokenizer's already-correct string decoder. The parity predicate is odd count of consecutive trailing backslashes. A genuine terminal matching quote requires length > 1 and an even count of consecutive backslashes immediately preceding that quote. Hex escapes ending in digits, an empty opening quote alone, escaped newline and both quote kinds need deliberate admission; do not infer closure merely from decoded output ending in a quote.

Integration constraint: endpoint correction and the final pop must use the same predicate. If a separate parity patch stops deletion for even runs, cached/duplicated endpoint logic must also stop subtracting for those runs. A shared recovery descriptor is useful, but each standalone patch must retain a valid pre-endpoint baseline application and make composition explicit.

## Minimal endpoint regression matrix

Use odd terminal slash cases to avoid depending on either semantic repair: both quote kinds; one and two nested missing var fallbacks; an earlier closed sibling followed by the final unclosed fallback; a custom-property carrier; a present primary with unused quoted fallback; plus closed and no-backslash EOF controls. Compare computed font-family with fully closed literal references. The existing 22-case semantic probe already covers parity and escaped terminal quotes; retain those failures until their separate repairs, without weakening expectations.

Existing missing-closing-nested-fallback WPT and crashtest are included as regression controls. The claimed endpoint repair must preserve those outcomes and references around unclosed comments. No new live WPT was authored in this review.

## Prior art

[Bug 2013337](https://bugzilla.mozilla.org/show_bug.cgi?id=2013337), particularly comments 6 and 19, describes nested missing function parentheses misidentified because the source ended in an inner rgb() closing parenthesis. Its repair compares inner/end parser positions; that code is already present here. The same bug also links a follow-up for trailing unclosed comments. This is strong known overlap in the missing-closer/reference-interval invariant, but the current quote deletion, backslash parity and escaped-terminal-quote predicates are distinct source mechanisms. No novelty, regression-introduction or absence-of-other-bugs claim is made. Direct historical commit fetches failed; this comparison relies on the public bug explanation plus current complete source and tests, not an independently fetched historical diff.

## Coverage and proof obligations

Pinned source: complete custom_properties.rs, properties/mod.rs and tokenizer.rs. Read full relevant parser, string consumer, fallback selector and substitution chunk consumers. Pinned evidence: both root raw/console/receipt sets and exact fixtures, plus current primary-spec parsed captures. Those captures are web-tool text, not raw HTML or independently validated fragment IDs.

Needed proofs: trailing slash pair decomposition; genuine closing delimiter classification; decoded-content equality before/after recovery; endpoint correction for arbitrary nested fallback trees and untouched earlier references; UTF-8-boundary preservation for deletion of ASCII backslash; final closing-parenthesis correspondence. Source/codec/usize/allocation/compiler and whole style-engine/caller refinement remain explicit. This review ran no compiler, browser, Git or native mutation.
