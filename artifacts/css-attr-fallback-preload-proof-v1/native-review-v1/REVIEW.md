# Independent native/source review: recursive fallback preparation

## Verdict

The recursive worklist is a coherent, bounded native repair for missing preparation of typed attribute references inside syntactic fallbacks. I did not author the native draft. The inspected delta is one function, update_attributes_map; the exact final native/WPT patch is SHA 08027345b7f8a23aba216b6244d5c48ec7cc9ba459a4536fc9bf291f4a5159e2. No source defect was found in its queue order, filtering, borrowed-reference lifetime, qualified Seen behavior or use of the owning VariableValue's URL data.

This is approval of that source change and its stated preparation scope for root's final acceptance. It is not a full substitution/Tarjan/provider proof or an assertion of universal observer or dependency-graph noninterference. The separate typed-fallback eligibility defects remain open and are demonstrated by retained diagnostic failures.

## Authentication and delta

The final producer manifest SHA is 80ec502c400e5810708f53ca5cc8021697457c7590e4cf38844bc4095a0f8ade. All its files were authenticated before review. The retained originals and candidates bind cascade 268d593c... to 8d2e2193..., while custom_properties.rs remains ff3bdc18... . Root's isolated patch has only cascade.rs and attr-fallback-preparation.html paths; it excludes unrelated local native changes. Clean HEAD application/signing remains root's responsibility.

## Source reasoning

1. Each popped reference list is scanned in source order. A present fallback list is pushed before any early continue. Therefore var, env, untyped attr, unknown namespace and duplicate outer-reference filtering cannot suppress its children. An explicitly present empty fallback is pushed and later popped harmlessly.
2. SmallVec push/pop is LIFO: all current-list references are prepared before children; sibling fallback lists run in reverse sibling order. Nested lists follow the same rule. This is preparation order, not semantic substitution order. No call-stack recursion is introduced by this worklist. Finite AST and successful finite allocation are the admitted domain; allocation failure is not proved away.
3. The early ATTR flag guard remains appropriate for parsed References: parse_declaration_value sets each reference kind's flag and ORs fallback.references.flags into its parent. A nested attr under var/env therefore marks its ancestors. The patch does not add a flag test on each popped list or prune children on their outer kind. This is a source inspection of successful parser output, not a universal verified parser translation.
4. Only is_attr_with_type references with Known namespace attempt cache preparation. Known null namespace is valid; Unknown is skipped. Namespace and name both participate in Seen. Exact duplicates are skipped, different namespaces remain distinct. The push precedes deduplication, so duplicate outer keys may each expose different child fallbacks.
5. Seen insertion precedes provider parsing; a failed fetch/parse remains Seen and is not retried by this preload loop. This matches the existing behavior. Successful provider results alone write the map. Non-target keys are unchanged. A fresh key may overwrite a pre-existing map entry if Seen does not contain it; no unconditional nonclobber claim is made for that inconsistent starting pair.
6. All syntactic fallback References belong to the same VariableValue. VariableFallback stores offsets/token types/References, not separate URL data. Reusing value.url_data is consistent with the parser's ownership representation. Dynamically parsed DOM attribute values are outside this syntactic traversal. Cross-declaration first-load URL provenance and all downstream taint effects are not universally proved here.
7. The queue holds immutable references into that VariableValue while Seen and the computed substitution map are mutated. Those writes do not replace the referenced parsed declaration/fallback storage. Existing types/imports support the SmallVec borrowing; root's native build is the compilation gate.

## Used edges and observers

The native function does not call visit_link, add a referring-root edge, or evaluate fallbacks. It prepares entries and registers independent Seen attribute roots. It can nevertheless add provider/AttributeTracker observations, change which attribute key is first prepared, allocate entries, and influence later root scheduling and invalidation. Source absence of an edge insertion is not a proof that all later graph behavior is unchanged.

A valid primary must not gain an edge to an unused fallback. That semantic decision remains in visit_value_references. Its current ready-only classification still omits requested-type validation. The worklist component separately models preparation and carries any used-edge field unchanged; such a product-projection theorem proves only the model's separation, not native observer/graph noninterference.

The provider model returns an abstract pure result. Native Seen insertion happens before provider invocation. The native get_attr_value_for_cycle_resolution API receives name, AttributeData, URL data and AttributeTracker, not Seen or the cache; the model may supply the previous cache to its abstract oracle. Matching the oracle result therefore requires provider independence from the Seen update (or an explicit supplied-result trace). Tracker/DOM/parser effects remain an external admission. No provider side-effect equivalence is claimed.

## Runtime evidence inspected

Both retained receipts report unchanged input pins and one suite end. Their source pins match the full snapshots. The final 16-case WPT changes from 10 FAIL / 6 PASS to 16 PASS. Existing tests remain 70 PASS (37 attr-cycle + 21 namespace + 10 tombstone + 2 namespace reftests). Diagnostic19 changes 9 FAIL / 10 PASS to 1 FAIL / 18 PASS; readiness6 changes 3 FAIL / 3 PASS to 2 FAIL / 4 PASS. The remaining failures preserve the separate typed-eligibility scope. The combined candidate command exits 1 because those diagnostic failures remain; this is not represented as an all-green combined suite.

Root reports native build and lint exit 0 (one ignored lint warning). This review's sealed evidence contains source and WPT receipts, not a new independently executed build. Root owns exact source/binary pairing, compilation, lint and final acceptance. No native/browser/build/Git action was run by this reviewer.
