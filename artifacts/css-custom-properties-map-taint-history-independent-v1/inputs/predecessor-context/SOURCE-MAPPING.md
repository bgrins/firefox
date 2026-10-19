# Source and specification mapping

## Source chain

The originals are complete retained snapshots from the routing audit. Candidate map and cascade snapshots are separately pinned. check.py verifies each changed file is exactly its retained original plus the reviewed replacement. No live-tree dependency is needed to replay.

- Value<Component>::PartialEq and VariableValue::PartialEq explain the payload comparator projection. The former omits wrapper metadata; the latter compares CSS strings.
- CustomPropertiesMap::do_insert first takes the unique mutable-inner route, otherwise tests deduplication before modifying shared storage. mapUpdate preserves this ordering at the selected-value projection. Candidate can_deduplicate_values compares both optional payload and wrapper taint, preserving None/Some distinction.
- Cascade::value_may_affect_style can return before substitution or map insertion. In the universal Unparsed comparison, candidate compares existing wrapper attr_tainted with value.is_attr_tainted, as well as CSS payload. This earlier return is modeled by pipeline. Earlier CSS-wide/inheritance and non-universal branches are not collapsed into a claimed native universal theorem.
- VariableValue::is_attr_tainted combines the ATTR reference flag and explicitly_attr_tainted. These are separate Incoming fields. substitute_references_if_needed_and_apply has a universal is_var/no-references direct path through ComputedRegisteredValue::universal, which sets wrapper taint using is_attr_tainted. This motivates the reference-free provider contract. It does not prove the earlier gate always lies in that domain.
- substitute_one_reference carries computed wrapper taint into the selected variable substitution. do_substitute_chunk accumulates selected taint ranges. Substitution::into_value preserves aggregate taint in stored results. These source slices identify the observer path but are not a proved substitution execution relation.
- AttrTaint::should_disallow_urls_in_range compares range endpoints; ParserContext::disallow_urls_in_range routes this check; CssUrl::parse_from_string rejects tainted ranges. ImageSetItem::parse is retained as one relevant consumer. Observation.lean models the comparator and contained-query projection over natural-number positions, without proving byte-range construction.

## Normative trace

Primary retained source: https://drafts.csswg.org/css-values-5/#attr-security (FETCH.json records retrieval and hash).

CSS Values 5 marks attr-produced values and containing functions tainted. A substitution is tainted as a whole when tainted values contributed to its creation, including equivalent token sequences from registered custom properties. Use of such a value in a URL invalidates the declaration at computed-value time. Therefore equal payload text alone cannot determine URL eligibility when its origin taint differs. The rule does not say all URLs near attr usage are invalid: the selected range and substitution context matter. A replacement literal with no attr contribution does not inherit taint merely because an older equal-text value had it.

This supports the paired selected-value witnesses. Full normative substitution and URL parsing remain outside this component. No novelty, complete security analysis or global PartialEq repair is claimed.
