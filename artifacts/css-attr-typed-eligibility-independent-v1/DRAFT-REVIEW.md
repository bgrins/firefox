# Typed attribute eligibility: draft independent review

Status: **provisional source review; producer seal and final exact-byte check pending**. No native build, WPT execution or final acceptance is claimed.

## Inputs

`draft-inputs/` is a separately hashed snapshot of the mutable producer package. `DRAFT-INPUTS.json` records its exact bytes and unsealed status. The signed design is retained by that package with its earlier freeze record. Additional parser/image/URL sources are read-only current-source supplements in `current-providers/`, labeled separately in `PROVIDERS.json`; they are not asserted to be independently tied to the tested binary.

`DRAFT-CHECKS.json` independently identifies the baseline's three remaining browser failures from actual statuses: custom typed fallback to a literal attribute, to a preloaded unresolved `var()` attribute, and to an unresolved attribute without an independent preload. The baseline receipt has stable inputs. It does not contain a candidate run.

## Source review

### Shared primary parser

`AttributeData::parse_typed_value` moves the existing `SpecifiedRegisteredValue::parse` call behind a Type-kind guard. Its inputs remain occurrence syntax, URL data, namespaces None, computational dependence allowed, default input taint, and the passed property ID. Final substitution still constructs its parser from the resolved attribute CSS and calls `to_variable_value` after a successful parse, then marks the resulting substitution attr-tainted. Unit, raw-string, omitted type and invalid type branches are unchanged.

The helper accepts an already-created parser rather than CSS text. Both reviewed callers construct a fresh parser over the same `resolved.to_variable_value().css` projection; neither carries a partially consumed stream into the helper. This is consistent with the design's shared primary-only validation boundary.

### Graph eligibility

`visit_value_references` still visits the primary link first. It retains non-custom flags from a universal resolved value, checks `!has_references()`, and only then calls the helper when `next.is_attr_with_type()` is true. That predicate includes both Attr-kind and Type-kind checks. Permissive `type(*)` therefore cannot make a pending primary ready.

The parse result is a local `primary_valid` value for the occurrence. It is not stored by attribute key, does not replace or tombstone the cached primary, and does not affect a later occurrence's requested syntax. Failure queues the fallback's references; success leaves that fallback unvisited. The helper itself cannot query the attribute tracker, resolve dependencies or enter fallback evaluation because it has none of those inputs.

The enclosing namespace guard, namespace-sensitive lookup, `contains_attr` tombstone check, lazy insertion and primary-link traversal are unchanged. Recursive preload remains a separate preparation phase. The existing graph/SCC logic is not proved correct by this patch.

### Property context

Collection now stores `(v.id, Arc<UnparsedValue>)`. It preserves the originating longhand instead of inferring one from FontUnits/LhUnits nodes. The latter can contain line-height as well as font-size values.

`UnparsedValue::substitution_property_id` gives the original shorthand precedence over the supplied longhand ID. Final `VariableDeclaration::substitute_variables` and non-custom graph traversal both use this exact helper. Custom/attribute roots pass the same `Some(PropertyIdRef::from(name))` convention as `substitute_references_if_needed_and_apply`; this review does not reinterpret attribute names as property names.

The source-aware shorthand-cache key and Arc source-identity comparison remain unchanged. Storing an extra enum per collected reference increases that vector's footprint; it is necessary source identity, not a new validity cache.

### Parser effects and taint

The registered-value parser builds a fresh local ParserContext with no error reporter or use counters and applies property context only around parsing. The inspected Gecko URL path creates lazy URL data; it does not fetch a resource during the extra primary parse. Image parsing dispatches into URL/image-set/gradient/value parsing and produces specified values, which the graph discards after checking success. This is a source audit, not a universal absence-of-side-effects proof for every supported syntax or future parser.

The helper's default AttrTaint matches the previous primary-parser call. Final substitution's explicit attr-taint publication remains intact. The graph parse does not publish untainted parsed values into style or cache and does not call to_computed_value. Existing URL rejection at consuming substitution boundaries remains required. No security restriction is relaxed in the reviewed delta.

Extra parsing can allocate and repeat work per traversed typed occurrence. Reusing one Boolean per attribute would be incorrect because syntax and property context can differ. No performance measurement was performed.

## Test oracle review

All twelve draft cases have expected results consistent with occurrence-specific primary parsing and used-fallback substitution:

- Three core cases reproduce the missing used-fallback dependency with literal, independently preloaded unresolved and lazily reached unresolved attributes.
- Both orders of length and universal syntax on one attribute test occurrence independence.
- Successful length/universal primaries ignore an otherwise cyclic self fallback.
- A failed length primary uses its self fallback and invalidates the custom property; the consuming width uses 37px.
- Preloaded literal and absent-primary cases are controls.
- Line-height and font shorthand cases exercise the new context path. They do not establish that erasing property identity changes parser success for these particular inputs, so they must not be described as discriminating context-erasure tests.

Explicit width/font defaults prevent accidental matching through unrelated inheritance. Custom-property output is normalized only for whitespace, appropriate to these simple literal token fixtures. The first three cases map to the actual remaining failure family. The current tests do not independently cover all namespace/tombstone/taint behaviors; root should retain the earlier regression suites for those.

CSS Values 5 first resolves the typed attribute's substitutions, then parses it using the requested syntax; parse failure reaches fallback substitution. Fallback is not evaluated after successful primary parsing. This supports the test's local edge-selection oracle; it does not prove the entire native graph matches the recursive specification. [Attribute substitution](https://drafts.csswg.org/css-values-5/#attr-substitution).

## Remaining gates

1. Receive and authenticate the final producer seal; compare this draft snapshot and inspect any changes.
2. Recheck complete original/candidate source identities, patch reconstruction, WPT bytes and signed-design correspondence.
3. Root-owned compile, exact original/candidate browser pair, prior namespace/tombstone/preload/cache/taint regressions and standalone packaging remain required for native acceptance.
4. Full SCC scheduling, provider freshness, observer/cache behavior, all parser semantics and broader C1–C13 obligations remain open.

Searchfox discovery was used. `webspec-index` is unavailable; direct current primary specification retrieval was used instead. No bootstrap or build was run under this artifact-only assignment.
