# Proposed interfaces and data flow

These are design types, not Rust additions or a compile-tested patch. Reuse the existing atom, namespace, value, declaration and index types where possible. A `ResolutionSession` owns transaction-local state; it is not installed in shared computed style or retained beyond this cascade/keyframe computation.

## Owned state

| Proposed item | Contents and lifetime |
| --- | --- |
| `RawAttrKey` | Element implicit in the session plus resolved namespace and local name. Identifies a DOM attribute independently of consuming property, parser type and recursion context. |
| `RawAttrInput` | `Missing`, `Unparseable`, or owned raw string plus parsed `Arc<VariableValue>` variants keyed by URL/parse environment. Obtained through `AttributeTracker::query`; never replaced by a resolved token string. Keep missing results tracked too. |
| `UseContext` | Owned equivalent of the existing optional `PropertyIdRef` (custom name or noncustom ID, including shorthand identity), existing `suppress_animation_taint_sink`, URL/parse inputs, and evaluation mode. Do not replace the actual property ID with a non-animatable boolean. |
| `AttrRequest` | `RawAttrKey`, owned/cloned `AttributeData` or interned equivalent, `UseContext`, source occurrence, and persistent substitution-guard path ID (property and attribute frames, with sticky cyclic flags). An occurrence records the actual attr call, including type and fallback; fallback text is owned through its source Arc. |
| `RequestId` / `RequestEntry` | Index into a per-session arena. Stores the complete request key, `Unseen / Evaluating / Ready / Invalid` state, owned result and dependency/guard information. First implementation reuses only the same suspended request ID; it does not memoize completed results across distinct consumer/guard paths. |
| `OwnedSubstitution` | Owned text (or Arc-backed span), token-boundary serialization, animation provenance, attr-security marking/ranges. No `Cow` borrowed from a map entry or stack-local parsed string survives a yield. |
| `ResolutionFrame` | Source Arc, reference/chunk cursor, output accumulator, continuation phase, current SCC node/index, and guard path. Store indices/ranges into owned input, not references into an arena that may move. |
| `ResolutionSession` | Existing Tarjan information and unfinished stack, raw input table, request arena, frames, and immutable environment references. The outer driver retains mutable cascade/computed-context/declaration-cache/tracker access and lends them only for a single step. |

The conservative request identity deliberately avoids claiming that `(attribute, property)` is a sufficient memoization key. A result can depend on attr type, source URL/parser arguments and active guard ancestry. Sharing results is a later optimization requiring a proof of context/guard independence or checked dependency summaries. Raw input may be shared within the stable element transaction; resolved results may not silently cross contexts.

## Step interface

An owned expression cursor makes progress until it needs a dependency or completes:

```
step_expression(frame, short_lived_ready_view)
    -> Complete(OwnedSubstitution)
     | Invalid(reason)
     | Need(DependencyRequest, owned_continuation)

DependencyRequest = CustomValue(name, existing_lookup_context)
                  | Attribute(AttrRequest)
                  | Prioritary(PrioritaryPropertyId)
```

`Need` is an internal suspension, never an invalid CSS value. The caller drops all map/context/cache borrows before dispatching it. The driver records the selected edge, visits the dependency using the current SCC session, then resumes with a ready value, a resolved invalid primary, or explicit in-progress SCC information. Do not convert “not ready yet” into guaranteed-invalid merely to obtain a fallback.

The expression operation is extracted from `do_substitute_chunk` / `substitute_one_reference`; it must retain token serialization, size limits, CSS-wide/defaulting decisions and attr-taint ranges. This is one implementation of primary acceptance and fallback selection used by both substitution and dependency discovery, not two approximately matching predicates.

### A Var reference

1. Request the referenced value through the existing registration/defaulting path. A ready value is cloned/owned before mutation is possible.
2. If the value is unresolved, preserve the existing deferred custom-resolution semantics: recurse with taint sink suppression, maintain custom cycle bookkeeping, and apply the completed value's outer Var guard in the original caller context. Preserve the existing parser `property_id` arguments separately from the suppression bit; the held provider intentionally passes them through. Do not silently substitute a custom name for the caller parser ID.
3. If the accepted primary is missing/invalid/rejected by the actual outer Var rule, enter that occurrence's fallback cursor under the caller context. Only references actually selected there generate new edges.
4. Ready and deferred paths must agree on CSS-wide/defaulted registered values and metadata. If a deferred expansion cannot safely reuse a canonical custom result because parser context differs, retain a contextual expansion request linked to the same canonical custom SCC node; do not overwrite the canonical map with a consumer-specific expansion. Proving when that expansion can be coalesced is an open implementation obligation.

### A typed Attr reference

1. Resolve the namespace and call-site attribute identity. Check the current attribute recursion guard **before** any completed-result lookup. The same physical attribute remains guarded even if consumer/type/request ID differs.
2. Query/load owned raw input through the tracker. Missing or malformed input proceeds through the existing attr fallback rules; guard failure is represented distinctly from ordinary cache miss.
3. Push the physical attribute onto the persistent guard path, then evaluate the raw expression under the caller `UseContext`. A nested Var can therefore select an inner fallback before attr type parsing. A custom alias's internal evaluation retains custom-reference suppression; a direct ordinary consumer does not.
4. Parse the resulting tokens using the actual attr type, URL data and parser property ID. A typed parse failure selects this Attr occurrence's outer fallback. The attribute-value substitution invocation ends before the outer fallback substitution; the latter uses the caller context. Retain sticky cyclic markings on every involved guard frame, including property frames, and check them when each surrounding substitution finishes. Popping an attr frame must not erase a cycle marking or let a successful fallback rescue a cyclic surrounding substitution. This follows the current primary guard/substitution text recorded in PRIMARY.json; native SCC equivalence still needs implementation verification.
5. Mark attr-security provenance on the result of the Attr operation, including its fallback result, while preserving the separate animation metadata according to the chosen propagation policy. The unresolved normative alias-provenance policy is not settled by this API. A whole-Attr rejection based only on its combined animation bit would discard the inner-fallback distinction and is not this design.

`RawAttrInput` is not the existing computed attribute map with a second flag. Existing `get_attr(...).css` consumers must be routed through the contextual request or explicitly limited to a context-independent/raw operation. A second table is ineffective if one ordinary path still substitutes the context-free final token string.

## Scheduling and SCC integration

Keep canonical custom node identity. Replace the context-free `VarType::Attr(name, namespace)` result node with an attr request node. Keep a separate physical-attribute active-guard index plus the ordered full property/attribute guard stack and sticky cycle flags. On guarded reentry, mark the involved guard interval cyclic and record the dependency on the active request before classifying the reference failure; do not create an endlessly expanding series of new context-key nodes. SCC invalidation affects the participating contextual requests, not every result for that attribute in every consumer. Custom/noncustom members still use their existing invalidation/defaulting semantics.

This does **not** make guard rejection and SCC failure interchangeable. The implementation must specify which selected edges participate in the SCC and which guards invalidate only a substitution occurrence. Before production code, test nested attr reentry with an outer fallback and a custom-property participant against the chosen spec interpretation and the existing held cycle behavior. No table entry may globally poison an otherwise valid consumer merely because another context selected a cycle.

The DFS may discover a fallback after a primary becomes invalid, including after an SCC is finalized. Such a continuation must not append a new dependency to an already-finalized node without reopening a well-defined evaluation request. Preserve the frozen walk's ordering where it is adequate; introduce a request-level continuation when a newly selected edge outlives that traversal step. Mark only final ready/invalid outcomes reusable. The current `traverse -> Option<index>` cannot express all three states (ready, suspended, unresolved SCC), so extending its return type is a required change, not an optional optimization.

Do not reset Tarjan state for a nested request. Existing `run_one` reset is a top-level-root operation; it must occur only after that root and its suspended continuations have closed. No arbitrary retry/pass budget is proposed.

## Priority properties and mutation boundary

`ensure_prioritary_property` currently inserts its ensured bit before applying dependencies. `apply_one_prioritary_property` then selects a declaration through a revert-aware loop, and `apply_one_longhand` performs substitution before committing `seen.longhands`, style data and bookkeeping. This is the concrete split:

- `prepare_longhand`: retain current eligibility/cascade/revert selection, produce an owned declaration-substitution cursor, yield dependency requests. Track `Unseen / Evaluating / Applied` separately; `Evaluating` is not “computed and available.”
- `finish_longhand`: accept the prepared owned declaration, retain CSS-wide/revert handling and existing commit suffix once, then perform `did_apply_prioritary_property` once for the accepted winner. A revert chooses the next declaration without leaving a stale result or marking the property applied.
- A priority request schedules generated `PrioritaryPropertyId::dependencies()` as graph edges before computation. Use priority IDs rather than only the current three unit-reference buckets where required, so writing-mode pulled in by line-height participates explicitly. Mapping font/line-height/color-scheme unit dependencies into those nodes must preserve existing distinctions and invalidation behavior; the source itself identifies generalizing `VarType::NonCustom` as a TODO.
- All ordinary declarations, including shorthand-derived ones, pass their existing `UnparsedValue::substitution_property_id` into the contextual evaluator. The historical wrapper caches shorthand substitutions by source Arc and longhand: a suspended result must not enter that cache, and a completed contextual result must not be reused against a different source/consumer/guard environment.

The current `substitute_variables_if_needed` already calls `set_uncacheable` and adds `DISPLAY_OR_CONTENT_DEPEND_ON_INHERITED_STYLE` before expression substitution. Preserve these conservative monotonic bookkeeping effects once per admitted declaration (or stage and apply them before completion); suspension must not clear them or misrepresent preparation as mutation-free. Keep shorthand-cache publication and accepted-declaration mutation separate from those effects.

This split must occur before mutation of `seen.longhands`, reverted-cascade state or computed style that would make replay non-idempotent. The existing loop's early eligibility checks can be retained, but suspension cannot restart an already-committed suffix. A callback from an immutable `ComputedSubstitutionFunctions` borrow into `ensure_prioritary_property` is explicitly disallowed; the driver owns the handoff instead.

## Call-site checklist

| Frozen hook | Required edit surface |
| --- | --- |
| `Cascade::maybe_note_non_custom_dependency` | Retain declaration identity and actual substitution property ID, not just a raw attr inventory; admit the consuming request. |
| keyframe builder `prepare_attributes` | Accept/retain the ordinary declaration's consumer identity; keep keyframe-specific preparation separate from property evaluation. Caller census is required before a signature change. |
| `update_attributes_map` | Populate immutable tracked raw input; stop treating an attr result computed under a name-derived custom context as universally reusable. |
| `substitute_all::{Context, visit_link, traverse}` | Own request frames and selected edges; return explicit ready/suspended/SCC states; keep nested work in the same session. |
| `substitute_references_if_needed_and_apply` | Keep custom/default selection path; separate attr raw storage from contextual results. Never destroy the only raw expression during completion. |
| `substitute_one_reference` / `do_substitute_chunk` / public `substitute` | Use the suspendable expression operation; preserve alias suppression and caller parser identity; release borrowed state at every yield. |
| `Cascade::substitute_variables_if_needed` and `apply_one_longhand` | Drive preparation through the session, then commit once. |
| `VariableDeclaration::substitute_variables` | Split substitution from parsing/cache publication or accept an already completed owned substitution; preserve shorthand source identity and IACVT conversion. Historical supporting capture only: current exact body must be joined before patching. |
| final attribute-reference publication | Finalize the same tracker that observed raw and newly selected fallback reads. Do not lose missing-attribute or namespace dependencies. |

## Implementation acceptance gates

First implement owned raw retention plus the step/request types without changing results, and verify that the legacy path reconstructs existing outputs. Then integrate contextual attr evaluation and selected-edge discovery together. Do not ship raw reevaluation without the session path or declare success from the four current callbacks alone.

Required checks include: primary-valid unused cyclic fallback; newly selected acyclic/cyclic fallback; same attr in direct and custom consumers in both evaluation orders; same attr under different type/URL/guard ancestry; registered/CSS-wide/defaulted aliases in ready and deferred forms; writing-mode/line-height priority cycles; missing/changed/namespaced attributes; keyframe and shorthand callers; attr URL-security preservation; repeated requests and cascade revert. The next implementation needs a real crate compile and targeted engine observations, not just an extracted mock. General cycle policy and typed-attr alias animation infection remain explicit spec obligations.
