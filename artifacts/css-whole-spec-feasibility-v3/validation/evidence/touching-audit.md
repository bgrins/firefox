# Touching attr-taint URL ranges: source audit

## Status and proposed diagnostic

Concrete source-admitted false-positive candidate; browser execution is pending and owned by root. Five cases in touching-url-taint.html have syntax-only Node validation. No native patch is proposed here. Do not change overlap endpoints without checking the complete producer and consumer contracts.

The isolated candidate is direct `image-set("DATA_URL"attr(data-density type(<resolution>)))` with density `1x`. The comparator is the same declaration with one space before attr(). The test separately checks adjacent literal string/resolution grammar and typed attr resolution via a registered property whose initial value is 2x. Unsupported syntax cannot pass those prerequisites. Other controls require direct attr URL and whole custom-property substitution to stay blocked.

## Actual source trace

1. `VariableValue::push` inserts a serialization separator only when token classes require one, then records taint from the byte count before appending the substituted text to the byte count afterward. `TokenSerializationType::Other` (quoted string) does not need a separator before Dimension. Empty text adds no range.
2. Typed resolution computation serializes 1x as 1dppx. The whole attr substitution is tainted; the literal prefix URL is not part of that substitution.
3. `ImageSetItem::parse` captures start before `expect_url_or_string`; the quoted token consumes through its closing quote. It captures end immediately after this call, before parsing resolution. The parser accepts resolution without a whitespace requirement.
4. `CssUrl::parse_from_string` asks `ParserContext::disallow_urls_in_range`, which calls `AttrTaint::should_disallow_urls_in_range`. The range documentation says end-exclusive, but the predicate uses <= and >=. In the touching case the taint start equals the URL end. The current predicate reports overlap; the separated case does not.
5. SPAN-TRACE.json gives the exact ASCII byte/code-point offsets derived from these bodies. It is deliberately labeled source-derived, not an executed tokenizer trace. All included strings are ASCII, so byte and scalar indices coincide. Whitespace consumed before a URL can widen its start; that is not needed for this example, where the URL is first in the option.

## Normative route and limits

[CSS Values 5 attr security](https://drafts.csswg.org/css-values-5/#attr-security), editor draft dated 4 September 2026, read 19 October: taint propagates through substitution and registered values; URL use is forbidden when the URL value itself is tainted. Its explicit direct image/fallback-color example permits a literal URL beside a tainted non-URL argument. Whole custom-property substitution broadens taint, and is intentionally a blocked control here. This audit infers the corresponding direct image-set resolution distinction; the normative URL restriction does not ban an unrelated resolution merely because it shares a containing image function.

The source grammar is consistent with CSS Images image-set option ordering (image followed by resolution/type). The test calibrates the actual no-whitespace spelling. This is not a claim about unsupported image(), src(), if() or arbitrary fallback grammars.

## Prior work

[Bug 1997583](https://bugzilla.mozilla.org/show_bug.cgi?id=1997583) is resolved fixed in Firefox152 and introduced partial-taint URL checks. Its description/comments distinguish a tainted gradient from a nearby literal URL; it lists duplicates 2026241 and 2030861. The retained implementation already includes that work. This bounded lookup does not establish novelty or rule out a follow-up report. The new map equality repair is separate: this diagnostic does not depend on equal-payload map replacement, and changing map deduplication does not change range intersection.

## Remaining gate

Run the five cases on root's pinned browser. If touching alone fails after all calibrations pass, obtain an extracted native span trace and review zero-length ranges, separators, skipped whitespace, URL-function spans and full-substitution boundaries before selecting an endpoint repair. Preserve the broader source/spec uncertainty instead of treating a mathematical half-open predicate alone as full parser correctness.
