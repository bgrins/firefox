# Typed attribute namespace cache: independent adjudication

## Verdict

The recorded browser gate confirms a real direct typed-attribute identity defect. Two different namespace URIs with the same local attribute name influence one another. Both literal lengths are valid independently; declaration order changes which result is wrong. This is within the known namespaced attr infrastructure problem described by bug 2021110; no novelty or separate-bug claim is made.

This review accepts the baseline reproduction and recommends the qualified-key repair below. It does not approve an as-yet-unreviewed candidate implementation or assert a universal substitution proof. No native edit, compilation, browser execution, or Git command was performed by this review.

## Actual evidence

`baseline/baseline-v1.jsonl` has exactly nine subtest results, seven PASS and two FAIL, one OK harness end and one suite end. The receipt records exit 1 and identical before/after hashes for all 13 inputs, including three relevant Rust files, browser/XUL, WPT, harness and ancestor metadata. All 11 archived nonbinary inputs match these hashes; browser bytes themselves are external recorded pins, not bundled here.

| Case | Observed result | Independent expected result |
| --- | --- | --- |
| typed-width-first | width 37px, fails first size assertion | width 13px, height 37px |
| typed-height-first | width assertion passes at 13px; height 13px fails | width 13px, height 37px |
| only-a / only-b | PASS | 13px/7px and 5px/37px |
| distinct-local-names | PASS | 13px/37px |
| same-qualified-name | PASS | 13px/13px |
| numeric-units | PASS | 13px/37px |
| null-and-named-distinct | PASS | 13px/37px |

The calibration also passes: typed/unit syntax accepted, two namespace rules retained, fixture width 100px. Every case checks DOM namespace reads and retained CSS declaration before size assertions. The first failed test does not print height; 37px/37px is a source-derived prediction, not a fully logged observed vector. Predictions in the fixture are never used as expected values.

The final WPT embeds the scout CSS/JS verbatim; the checker verifies this separately. The original scout status was UNEXECUTED and is preserved. Root's later log is the execution evidence. Absence of test-specific metadata is not evidence that a test ran.

## Normative oracle

Primary snapshot: `scout/css-values-5.html`, HTTP 200 from https://drafts.csswg.org/css-values-5/, fetched 2026-10-19T15:28:26.897754Z, hash and URL in `scout/FETCH.json`. Anchors `attr-notation`, `typedef-attr-name`, and `attr-substitution` are present and rechecked.

CSS Values 5 defines an attribute name with optional namespace prefix. The prefix is resolved to a namespace URI; an omitted prefix selects the null namespace. Substitution parses the name/type, retrieves that element attribute, substitutes functions in a typed value, then parses it against the requested syntax. Here URI A/local x selects 13px and URI B/local x selects 37px. Neither contains a substitution function; both parse as lengths. Neither fallback applies. Width and height have no competing declarations, percentage dependency, layout measurement tolerance or font premise. Swapping their declaration order cannot change these independently selected attributes.

The unit case follows the separate numeric-unit branch before arbitrary substitution and is a useful control for the typed-value cache boundary. A passing single-namespace case rules out unsupported namespace syntax and basic DOM attribute lookup as the explanation.

## Exact source cause and full key propagation

The three source files in `scout/source` match the browser receipt. Supplement files are separately marked current-source acquisitions; they are not retroactively browser pins.

1. `ParsedNamespace::parse` resolves the prefix and intentionally discards it. `Known(Namespace::default())` is the null namespace; `Unknown` is different. This is the right identity boundary.
2. `AttributeTracker::query` already receives local name plus namespace, stores both for style sharing, and calls `ElementContext::get_attr` with both. No DOM lookup representation repair is required by this witness.
3. `update_attributes_map` deduplicates typed references only by `next.name`. It queries the qualified attribute but stores the resulting parsed token stream in `ComputedSubstitutionFunctions.attributes: OwnMap`, whose key is Name alone. Distinct qualified attributes collide before substitution.
4. The final typed attr branch queries the correct qualified DOM attribute, then outside container queries replaces it with `get_attr(&reference.name)`. Numeric/raw branches bypass that replacement.
5. The graph is equally affected: `VarType::Attr(Name)`, `OrderIndexMap.attr`, `visit_value_references` map fill/node creation/primary classification, `traverse` root lookup and ordering, `handle_loop`, and both successful/failed `substitute_references_if_needed_and_apply` paths all discard namespace. Fixing only preload and final lookup leaves false node equality or cross-namespace invalidation.
6. Final roots come from `seen.attr`; root enumeration must retain namespace too. Generic custom-property storage (`OwnMap`) must remain unchanged.

### Smallest recommended representation

Use namespace buckets, preserving borrowed atom lookup and the existing single-atom precomputed hasher:

```rust
// Schematic API design, not compiled candidate code.
type ComputedAttributes = PrecomputedHashMap<Namespace, OwnMap>;
// seen.attr: PrecomputedHashMap<&Namespace, PrecomputedHashSet<&Name>>
// VarType::Attr(Name, Namespace)
// index_map.attr: PrecomputedHashMap<Namespace, PrecomputedHashMap<Name, usize>>
```

`get_attr`, `insert_attr`, and `remove_attr` take `&Name` and `&Namespace`. Reads use borrowed namespace/name lookup; clone atoms only when storing owned keys. Existing `selector_map.rs` already uses `PrecomputedHashMap<Namespace, ...>`. Do not apply `PrecomputedHasher` directly to an unreviewed tuple/composite key.

Change `ComputedSubstitutionFunctions::new`'s attribute parameter to `Option<ComputedAttributes>`. Change the apply routine's kind parameter to `Option<&Namespace>`: None means custom property; Some(empty namespace) means a real null-namespace attr. Derive the Var/Attr branch from that option or use a typed equivalent. All remove/insert paths use the same qualified key; do not infer it later from the local name. Keep custom registration, invalidation, CSS-wide keyword and taint semantics unchanged.

Expose the existing parsed namespace as `AttributeData::namespace() -> Option<&Namespace>`. Unknown means no attribute graph node/cache access. It must still traverse a used fallback; a bare early continue that drops fallback dependencies is incorrect. Retain existing can-chain gating independently. URI aliases intentionally share a bucket; different URI atoms and the null namespace cannot alias. Custom-property nodes remain tagged separately from attribute nodes.

Graph traversal mutates maps: carry or clone the URI into `VarType::Attr` as needed to satisfy borrows, then select its namespace bucket before `entry_ref(name)`. Preserve tombstone semantics for failed/cyclic values, and do not let an invalid primary reuse another namespace's valid entry. The outer namespace map may change unrelated-node visit order; semantics should be independent, but the SCC/fallback tests below are required because no Tarjan/order-independence proof is established here.

## Known issue boundary

`scout/BUG-2021110.md` retains the fetched issue: “Chained references should support namespaced attributes”; comment 1 explicitly identifies missing namespace lookup infrastructure in cycle detection and substitution. That overlaps the proposed key plumbing even though this witness uses only direct literal attributes. Treat this as a concrete reproducer/partial repair for that known area.

`get_attr_value_for_cycle_resolution` still parses an attribute's token contents with `VariableValue::parse(..., None, ...)`, and its TODO explicitly names bug 2021110. Namespace-qualified references written *inside attribute values* therefore remain a separate context-plumbing obligation. A map-key repair must not silently remove that TODO or claim all chains fixed. Proposed tests avoid prefixed nested attr text: outer stylesheet names may be qualified, inner attribute text uses var() or null-namespace attr(). Container-query bypass has its own existing bug 2028861 comment and is outside this repair.

## Tests and controls

`CONTROLS.md` specifies proposed additional cases with independent expected values, all UNEXECUTED by this reviewer. Keep both declaration orders for direct collisions, chains and cycle/invalid isolation. Use array equality for width/height so a failing assertion prints the complete observed pair; remove sourcePrediction fields from the eventual landable test.

Existing inspected tests are included under `supplement/testing`: attr-namespace-valid.xhtml covers a single typed qualified attribute; attr-null-namespace.xhtml tests null namespace selection/mutation with differently named properties; attr-namespace-non-existing.html tests unknown-prefix fallback; attr-namespace-case-sensitivity.xhtml exercises selectors and raw generated-content attr; attr-cycle.html covers chained and cyclic attrs/custom properties but not independent typed same-local attributes in different namespaces. This is a bounded coverage review, not an exhaustive WPT inventory. Their metadata presence/hashes are in ACQUISITION.json. None was executed by this reviewer.

## Remaining gates and limits

Root must compile the actual candidate, pair the expanded WPT with frozen baseline/candidate sources, and run relevant existing namespace/cycle/taint/invalidation tests. Confirm unknown-prefix fallback edges, same-URI aliases, null namespace, true and false cycles, dynamic namespace-specific mutation/removal, and preservation of unrelated custom-property cases. Static source correspondence plus finite browser cases cannot prove general Tarjan correctness, mutation scheduling, heap safety or full CSS substitution semantics. The separately assigned formal component can establish qualified-key noninterference and graph identity conditional on native API admission.

Inspected: direct parser namespace identity; preload/dedup; complete relevant apply routine; attr substitution branch; complete SCC traversal and fallback/root paths; tracker query; map type; builder constructor use; named existing WPTs; primary attr section; known issue snapshot; exact recorded raw browser statuses. Not inspected exhaustively: all invalidation callers, style sharing consumers, property registrations, container query behavior, parser serialization, allocation paths, full spec substitution/cascade semantics. No unsupported claim is used to accept the reproduced literal witness.
