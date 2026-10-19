# Recursive attribute preload draft

Status: artifact-only proposal. The Rust patch is **UNCOMPILED**, the six new WPT cases are **UNEXECUTED**, and no browser result or native acceptance is claimed. The sealed 19-case parent probe is unchanged. This draft addresses missing preload traversal; it does not repair fallback eligibility in the dependency graph.

## Source and normative oracle

The complete original files are the authenticated namespace candidate v2 from `../css-attr-fallback-preload-probe-v1`. `PINS.json` records original/candidate hashes and that parent manifest. This is the combined local cascade context, not an independently built HEAD patch. Only `Cascade::update_attributes_map` changes; `custom_properties.rs` is byte-identical context. No native repository file was edited.

The copied primary CSS Values 5 document and retrieval metadata are identical to that sealed parent. Its `attr-substitution` algorithm substitutes arbitrary functions in a typed attribute's value before parsing the requested syntax. A missing attribute or failed type parse selects the fallback. A successful primary returns without evaluating the fallback. These rules determine the expected widths independently of cache state. The new fixtures use null-namespace attributes, so they do not require the missing prefixed chained-attribute support in bug 2021110. Prior-art/search records remain in the authenticated parent; no new novelty claim is made.

## Minimal preparation change

The parser stores references in each fallback's own `References`; it propagates flags but does not flatten those references into the parent's `refs` list. Existing `update_attributes_map` only walks the top-level list. The draft uses the existing `SmallVec<[&References; 5]>` worklist pattern from `visit_value_references` to visit each syntactic fallback list as well.

The fallback is queued before testing the outer reference's kind, namespace, or duplicate key. This preserves nested typed attrs under var/env, unknown namespaces, and repeated outer names. Existing `(namespace, name)` deduplication and unknown-namespace behavior are retained. The worklist parses typed attribute values into the existing map and registers independent attr roots; it does not recursively resolve those values and does not add dependency-graph edges.

This avoids native call-stack recursion. Existing imports supply `References` and `SmallVec`; references borrow the original `&'a VariableValue`. No new dependency or owned clone is needed. Rust lifetime/type checking and formatter/build gates remain pending root integration. Worklist order visits top-level refs first and fallback lists in stack order; it must not be treated as a semantic evaluation order.

## Readiness before custom roots

`Cascade::maybe_note_non_custom_dependency` calls `update_attributes_map` while collecting non-custom declarations. `Cascade::cascade_custom_property` defers values containing references. `apply_custom_and_prioritary_properties` invokes `substitute_all` after collection. At the end of `substitute_all`, the complete loop over `seen.var` precedes the loop over `seen.attr`.

Consequently preload means parsed, not computed. For `chain="var(--v)"`, a separate declaration `height: attr(chain type(<length>), 7px)` registers the attr root but does not ensure that root runs before `--result`. In `visit_value_references`, `primary_valid = !v.has_references()` does not validate a resolved attr against the syntax of this occurrence. `bad="not-a-length"` is therefore treated as a valid primary for graph selection even though final `substitute_reference` rejects it as `<length>`.

The new discriminating fixture is:

```css
--v: 13px;
--result: attr(bad type(<length>), attr(chain type(<length>), 5px));
width: var(--result);
height: attr(chain type(<length>), 7px);
```

With `bad="not-a-length"` and `chain="var(--v)"`, both width and height must be 13px. Static source tracing predicts width5px/height13px even with this draft: the custom root selects its substitution fallback before the independent chain root has resolved. Replacing chain with literal13px can pass and conceal this problem. Replacing bad with a missing primary allows the graph to follow and resolve the fallback dependency. The case file retains all three controls, the direct ordinary-property case, an unwarmed custom-root case, and an unused cyclic-fallback control. Exact predictions are separate from normative WPT assertions.

## Used and unused cycles

Preparation must remain distinct from edge creation. Do not flatten fallback references into the primary reference list or add edges for every preloaded attribute. A successful primary must not acquire an edge to its unused fallback. The existing graph traversal condition remains unchanged by this draft.

An independently preloaded attr root can still resolve or become invalid from its own dependency graph. A one-way dependency from that root to a valid custom property does not by itself create a reverse edge or a cycle. The existing parent cases cover used versus unused custom-property cycles, an unused cyclic attr, and registered font-size dependency cycles. The new sixth case adds an unused fallback whose independent attr/custom pair is cyclic, while width has a valid primary. Expected width remains13px.

This reasoning is not a universal Tarjan/noninterference proof. Reading and parsing unused fallback attributes can add tracker dependencies, allocate map entries, and increase work. Shared map invalidation and finished-index behavior still require runtime/review evidence; a separate agent is investigating reload after SCC invalidation. This draft does not assume that issue away. Running the unchanged 19-case suite plus these six cases is a useful next gate, but cannot establish universal absence of graph-order effects.

## Suggested repair boundary

Use this one-function patch as the smallest candidate for the missing recursive preload issue, subject to root's browser gate. It should repair direct nested typed fallbacks, including prioritary properties that did not otherwise enter the graph. It should not be represented as fixing all typed fallback handling: occurrence-specific requested syntax must participate in used-fallback graph admission, and that separate repair must resolve actual fallback dependencies before computing the referring root. Reordering all attr roots before custom roots is not a substitute: their dependencies can be mutual.

## Replay and limits

Authenticate `MANIFEST.json` using the separately communicated digest, then run `python3 check.py --manifest-sha DIGEST` from any location. The checker authenticates every input before parsing it, reconstructs the exact patch result, checks unchanged context and the six fixture definitions, and verifies retained source-order observations and primary-spec anchors. It uses only the Python standard library. It does not compile Rust, execute JavaScript, run a browser, or prove semantic equivalence. `REPLAY.json` records relocated integrity and deliberate-tamper checks. No absence of test metadata is used as execution evidence.
