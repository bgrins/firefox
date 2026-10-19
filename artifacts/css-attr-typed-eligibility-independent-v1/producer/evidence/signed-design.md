# Occurrence-specific typed fallback eligibility

## Finding and boundary

A resolved attribute cache entry does not establish that an individual `attr()` primary succeeds. Final substitution parses that value against this occurrence's requested syntax; graph traversal currently tests only `!v.has_references()`. A resolved identifier can succeed under `type(*)` and fail under `type(<length>)`. Caching one primary-validity Boolean by attribute key therefore cannot represent both occurrences.

Root's after-tombstone baseline-v2 receipt has stable pins and confirms the readiness suite's three predicted failures and three passing controls. The warmed custom-property case returns width 5px / height 13px even though the independently specified CSS result is 13px / 13px. This separates the eligibility problem from a missing preload entry: the fallback attribute is present but has not been resolved when the custom root computes. Complete custom_properties.rs and cascade snapshots here exactly match that receipt's source pins. No new native implementation is supplied or accepted here.

## Proposed shared validation boundary

Extract the current `AttributeType::Type` primary parse into one crate-local `AttributeData` helper taking:

- the resolved attribute CSS text;
- the occurrence's URL data;
- the exact `Option<PropertyIdRef>` supplied to substitution.

Return the parsed `SpecifiedRegisteredValue` or failure. The body should preserve `Parser::new`, `SpecifiedRegisteredValue::parse`, the occurrence's stored syntax descriptor, namespaces `None`, `AllowComputationallyDependent::Yes`, `AttrTaint::default()`, and the passed property ID. Final substitution uses the returned parsed value and its existing to_variable_value/attr-taint path. Graph traversal tests the same parse result for success, after the resolved-value check.

Do not invoke `substitute_one_reference` as a Boolean test: that function fetches the DOM attribute and can evaluate the fallback. The shared helper must parse the primary only; it must not query AttributeTracker, compute dependencies or recursively evaluate fallback. Reuse the same to_variable_value CSS projection in both callers unless its equivalence to directly reading the universal value is separately established.

The graph still visits the primary dependency before classifying success: attr substitution resolves the primary before syntax validation. Keep its non-custom dependency observations. A failed requested-type parse then queues the fallback reference list; a successful parse adds no fallback edge, regardless of cyclic or invalid values in that unused fallback. A pending primary remains unresolved/invalid for the current traversal's existing branch; never let permissive type(*) parse make it ready.

This proposal targets the `AttributeType::Type` path. Unit/raw-string/omitted-type and container-query behavior need their existing separate treatment. The generic model does not prove their native branch correspondence.

## Exact property context must survive collection

The current custom/attribute root path calls `substitute_references_if_needed_and_apply` with `Some(PropertyIdRef::from(name))`. The eligibility call for those roots can reuse that exact argument, including the existing attribute-root naming convention; this design does not reinterpret it.

For non-custom roots, deriving the property ID from `SingleNonCustomReference` is insufficient. `maybe_note_non_custom_dependency` records line-height declarations under both LH_UNITS and FONT_UNITS. A FontUnits node therefore contains values from both font-size and line-height. Its entries retain `Arc<UnparsedValue>` but omit the originating `LonghandId`.

The actual local `VariableDeclaration::substitute_variables` takes longhand_id from self.id and chooses the shorthand property ID when unparsed.from_shorthand is present, otherwise that originating longhand ID. The registered-value parser passes this ID through ParserContext::with_property_declaration. Thus a proposed call with None or the node's own prioritary ID has not established equality of parser inputs.

Recommended exact-context repair: store `(LonghandId, Arc<UnparsedValue>)` (or a small named struct) in each references_from_non_custom_properties vector when collecting it. At traversal, derive the same shorthand-or-originating-longhand PropertyIdRef for each entry and thread it into visit_value_references. Alternatively a proof that type-parse success is independent of the erased property context would suffice for eligibility, but none is supplied. The context-erasure theorem here proves lost source identity, not an observable grammar difference between those property IDs.

Complete indexed and actual local value.rs and properties/mod.rs are retained with PARSER-CORRESPONDENCE.json and full diffs. value.rs is byte-identical. Local properties/mod.rs contains the earlier source-aware shorthand cache repair and uses VariableDeclaration rather than the indexed UnparsedValue method; its actual property ID selection confirms the same shorthand-or-originating-longhand requirement. This package preserves those local differences and does not alter that cache repair. These additional source files were copied read-only with root authorization; the readiness receipt itself pins custom/cascade, not these additional files, so this is source-level correspondence rather than a newly verified binary provenance gate.

## Preparation and semantic edges

The recursive preload proposal is separate: it walks all syntactic fallback lists to prepare attribute map entries, without making referring-root dependency edges. It can fix direct ordinary-property availability while leaving custom-root ordering wrong. Reordering every attr root before custom roots is insufficient because dependencies can be mutual.

The eligibility repair makes fallback traversal conditional on this occurrence's primary parse result. It can resolve a used fallback lazily for custom roots even when preparation did not discover it. It must not be presented as replacing recursive preload for paths that never enter graph traversal.

The model proves only that a preparation change preserving the current slot leaves this local decision unchanged. Actual preparation can read attributes, populate entries, and affect graph/root order. No unconditional observer, cache or graph noninterference theorem is claimed.

## Formal component

AttributeEligibility.lean contains 15 audited results. The universal component treats the actual parser as a parameter with explicit context, syntax and input, and proves:

- absent/invalid/pending primaries use fallback;
- successful ready parses add no fallback edges, for arbitrary fallback lists;
- failed ready parses select fallback;
- equal parser results transfer the edge-selection result;
- readiness alone misses rejection;
- a value-only Boolean cannot classify two occurrences with different parse outcomes;
- preparation preserving the looked-up slot preserves the local decision;
- a shared FontUnits node cannot reconstruct both originating property IDs.

Two concrete finite examples exhibit the identifier/length distinction. They illustrate the universal distinction theorem; they do not execute the native CSS parser. Mutation gates replace parsing with readiness and force unconditional fallback edges; both must fail kernel checking.

Full native parser admission, provider stability, successful-value terminality, SCC scheduling, fallback observer/cache behavior, and native collection context remain open. This extends the source design and local mathematical obligation; it does not close C1–C13 or full substitution correctness.
