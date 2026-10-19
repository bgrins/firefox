# Recursive fallback preparation: finite worklist component

Status: universal model component with manual source binding. The independent native review is separately sealed in native-review-v1. No full provider, observer, CSS parser, substitution, Tarjan or occurrence-specific type-eligibility correctness claim is made.

## Proven execution model

The finite input is a list of references. Each reference has metadata and either no fallback or an explicitly present fallback list, including an empty list. The pending SmallVec is represented with its top at the head of a list. scan processes a complete reference list in source order and pushes each present fallback before the filtering/preparation action.

- scan_actual_push_order proves that scan's queue is reverse(children(current-list)) appended to the previous stack. This captures the native sibling/LIFO schedule, rather than substituting an unrelated recursive traversal.
- A ghost stack cost counts pending fallback frames and all their descendants, including empty frames. Each outer pop decreases it by exactly one. Each inner scan structurally terminates on its finite reference list. finite_worklist_terminates proves completion with sufficient fuel.
- run_complete preserves arbitrary natural-valued weights on reference occurrences. No occurrence is lost or added, including duplicates and descendants under var/env/untyped/unknown outer references.
- inner_loop_factorization relates the native interleaving of enqueue and preparation to the queue and map effects. actual_worklist_trace_composition proves the entire outer execution equals preparation over exactly the emitted run trace and its remaining stack.
- actual_worklist_seen_complete combines both: after complete execution a qualified key is Seen exactly when initially Seen or present as an eligible typed/known-namespace reference anywhere in the finite pending fallback trees.
- Provider attempts are unique by qualified key under the initial attempts invariant. Previously Seen values are preserved through arbitrary preparation. Keys absent from all eligible occurrences are preserved. Qualified same-name/different-namespace keys remain distinct. Failed fresh attempts mark Seen without writing a value. A fresh key may overwrite an existing map value if Seen does not contain it; no stronger initial-state claim is assumed.

There are 38 new audited theorems and 16 retained qualified-key/history theorems, in four substantive modules plus Audit. All retained proof source is copied into the package; no prebuilt olean is needed.

## Native binding and admissions

The final producer manifest SHA is 80ec502c400e5810708f53ca5cc8021697457c7590e4cf38844bc4095a0f8ade. Complete original/candidate custom_properties.rs and cascade.rs are retained. Only update_attributes_map changes; custom_properties.rs is identical. native-review-v1 separately binds root's isolated native/WPT patch and paired runtime receipts.

| Native mechanism | Model / admission |
| --- | --- |
| SmallVec push/pop; for next in refs.refs | enqueue, scan, scanAndPrepare, execute; top is list head |
| Fallback push before continue | Metadata-independent enqueue and explicit skipped/duplicate-parent theorems |
| is_attr_with_type | Info.kind typedAttr; all other attr kinds grouped as untypedAttr for filtering |
| Known namespace including null; Unknown skip | infoKey/resolveKey; injective Nat tokens for actual Name/Namespace admitted |
| Namespace -> name Seen sets | Qualified State.seen flattened to membership-equivalent list; native Hash/Eq/set semantics external |
| Seen insertion before provider, duplicate skip | prepareOne branch and attempt invariant; attempts is a reverse chronological ghost list |
| Provider success inserts Some, failure writes nothing | Arbitrary pure Provider result and preload |
| Initial ATTR flag guard | Model starts after worklist admission; parser sets kind flags and ORs fallback flags. Successful parser flag soundness is manually reviewed, not kernel-proved |
| value.url_data | Fixed owning VariableValue context for syntactic fallback lists; VariableFallback has no separate URL |

The provider receives name, AttributeData, URL data and AttributeTracker, not Seen/cache. The model supplies its old abstract cache to a pure result oracle, whereas native Seen is already updated before provider invocation. Matching results requires provider independence from that Seen-only update or a supplied result trace. The source signature supports this separation; native tracker/DOM/parser observations are not modeled or proved equivalent.

The finite owned fallback AST is the admitted input. Fuel and mathematical Nat cost are proof devices, not production limits/counters. Native allocation success, bounds and lifetime admission remain external. Source reasoning for borrowing, flags, filtering and URL data is in the separately sealed independent review.

## Preparation versus used edges

preparation_does_not_select_used_edges is explicitly a modeled product projection: its wrapper returns the supplied used-edge list unchanged. It is not a native observer or graph noninterference theorem. The actual function does not call visit_link, but new provider reads, first preparation of a key, independent Seen attribute roots, and later root scheduling/invalidation can have downstream effects. Worklist discovery must not be interpreted as unconditional semantic fallback-edge creation.

Occurrence-specific typed eligibility remains separate. The retained pair makes final16 pass and preserves 70 existing passes, while leaving one diagnostic19 failure and two readiness failures. These boundaries are retained. The separately sealed typed-eligibility component establishes the ready-only counterexample and parser-context design; this worklist does not repair them.

## Replay

Replay authenticates sources/receipts, applies and reverses the exact native patch in an isolated directory, compiles all Lean source afresh, checks 54 theorem audits, and rejects four semantic mutations: FIFO queue, skipped var-parent children, namespace aliasing and dropped Seen deduplication. No native build/browser was run by this agent. Root owns source/binary pairing, native acceptance and signing.

Workspace interruption was checked before final replay: restored producer/source/native-review pins and both paired receipts authenticated; the report and checker were absent and completed afterward. No missing runtime evidence was reconstructed. After restoration, root requested a hypothesis-name-only rename from admit to key_eq to keep its strict lexical gate simple. SEAL-REVISION.json records the superseded initial seal and the reversible rename; no theorem statement or algorithm changed. Fresh v2 replay checks the renamed sources.

This component does not close the broader C1–C13 scope or erase prior source/provider/evaluator refutations.
