# Range-to-sink map and bounded findings

## Producer chain

`VariableValue::parse` scans original component bytes, records nested function/fallback positions, then stores repaired/trimmed text. **New confirmed failure:** a leading whitespace prefix is removed without rebasing those positions on the raw-attribute entry path. This violates safety before URL-specific taint checking; the parent reproduced the exact Rust bounds panic.

`substitute_one_reference` returns a serialized CSS string plus first/last token metadata and an aggregate attr bit. Direct attr branches quote strings or serialize typed results and set the bit. Var lookup preserves wrapper metadata; recursive unresolved universal values OR wrapper taint after recursive resolution. Fallback recursion returns a fresh aggregate bit. Env currently returns false.

`do_substitute_chunk` adds clean literal pieces, substituted pieces, and suffixes. `VariableValue::push` inserts any required `/**/` before recording the start, appends substituted CSS, then records [start,end). Byte lengths are taken after serialization, so string escaping and UTF-8 expansion do not require multiplying character offsets. A whole-input optimization records [0,len) under the actual top-level callers. Fallback recursion can start above zero but receives no interval accumulator; it returns aggregate taint to its enclosing substitution. The apparent `taint.push(start,len)` issue is therefore not a separate reachable offset bug in these inspected calls.

`Substitution::into_value` turns aggregate taint into a full-value range before registered parsing and ORs it into the resulting wrapper. Universal values retain the wrapper bit. `ComputedValue::to_declared_value` copies wrapper taint into explicitly_attr_tainted for universal uncomputation when necessary; typed conversion retains its wrapper field. The accepted map/endpoint/base/arithmetic components address different later equality and delivery boundaries, not this new raw-input coordinate failure.

## Consumers

- Normal longhand/shorthand reparsing constructs Parser over the unchanged substituted css and supplies the matching AttrTaint to ParserContext. `skip_whitespace` advances the same parser, without reslicing its input, so positions keep their original origin.
- Registered parsing similarly forwards one Parser and AttrTaint through component alternatives and nested parsing.
- CssUrl::parse_with_cors_mode captures parser positions around expect_url; parse_from_string applies the range guard before constructing the URL.
- ImageSetItem::parse captures positions around URL/string parsing and uses the same guard. Resolution/type strings are distinct non-URL consumers; numeric taint near a clean URL is permitted by the security rule.
- The unchecked URL constructor's inspected production caller is @import raw syntax, not arbitrary element substitution.
- Container-query substitution forwards AttrTaint into parser/registered-value parsing. Numeric style-range resolution drops the range while reinterpreting only numeric component types; no URL/string sink was established on that branch.

## Other seams, not new confirmed bugs

1. Attr fallback can return a clean literal fallback unchanged. The current prose calls values produced by attr tainted, but does not spell out fallback provenance separately. A literal fallback observer only discloses attacker-supplied bytes. Keep normative clarification and possible compatibility review separate from the crash and from unknown-data exfiltration.
2. LinkParameters stores only OwnedStr, and env substitutions unconditionally return clean taint. Current Linked Parameters §3.1 requires preservation when the defining param was tainted. Native comments already identify bug 2028998 for carrying complete values/URLs. Reachability and feature defaults, downstream embedded-document URL behavior, and overlap with that known issue remain unadjudicated. This is a provider-frontier lead, not a newly established vulnerability.
3. A universal explicitly-tainted value reparsed under a changed typed registration would require preserving that bit. No actual same-epoch producer path violating the registration assumption was found in this bounded audit; do not infer a browser bug from constructing an arbitrary inconsistent internal value.

## Exclusions

No whole tokenizer or source-translation proof; no blanket URL-consumer enumeration beyond the retained direct constructors; no external-resource image loader audit; no arbitrary registration-epoch/history proof; no global network noninterference; no unknown-attribute-byte exfiltration claim. No runtime was launched by this agent for this task. The parent owns browser reproduction and native repair.
