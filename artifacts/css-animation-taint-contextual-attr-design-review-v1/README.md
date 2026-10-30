# Critical review: a smaller contextual-attr resolver seam

The frozen source does not establish that a general owned suspension machine or resumable longhand cascade is necessary. The existing synchronous DFS already resolves a primary, classifies it, visits a selected fallback, and substitutes after SCC handling. It clones the source value before releasing map borrows. These are useful foundations for a smaller complete strategy. An inventory-only change, however, is insufficient. A credible smaller design also has to close priority-property and deferred-alias call paths before claiming coverage.

The recommendation is to implement and falsify a synchronous contextual-dependency preparation seam first, retaining the current final longhand application. Do not restrict it to ready variables, literal fallbacks or the current four tests. If its closure invariant cannot be met at a concrete caller, add a local continuation there; the evidence does not yet justify a general expression cursor and prepare/finish protocol across all longhands.

## What the code actually permits

`visit_value_references` already calls `visit_link` before deciding whether a fallback is used. `traverse` holds a strong source clone, resolves dependencies using mutable context, handles its SCC, and then calls substitution. Dynamic selection of a fallback is therefore not by itself a reason to suspend the enclosing declaration. A synchronous call stack can retain the owned source while each short map borrow ends before recursive mutation.

`apply_one_longhand` performs eligibility checks, then substitution, then revert/seen/style commit. The final declaration application need not become resumable if a new dependency-preparation call completes before immutable substitution begins. The wrapper's earlier uncacheable and display/content dependency flags are conservative bookkeeping; preserve them once rather than rerunning or clearing them. Shorthand-cache publication and revert-aware winner selection remain in their existing order.

This is a possible control-flow construction, not a borrow-checked implementation. Merely passing `&mut Context` through the existing immutable substitution helper is not valid: its map/value borrows and the surrounding cascade borrow must end before any recursive preparation.

## Why only context-qualified inventory is not complete

| Frozen boundary | Concrete failure of the three-change proposal alone |
| --- | --- |
| `maybe_note_non_custom_dependency` | A writing-mode attr declaration populates raw attribute inventory but returns from the noncustom-node match: only font-size, line-height and color-scheme contribute those declaration edges. Naming an attr node with writing-mode does not schedule it before that property is applied. |
| `ensure_prioritary_property` | It marks an ensured bit before recursively applying generated priority dependencies. During a custom root, line-height can cause writing-mode application before the final loop over remaining attr roots. Inventory order cannot establish that its contextual result is ready. The bit also cannot mean completed computation. |
| Deferred `substitute_one_reference` Var path | An unresolved universal value is expanded recursively with the caller parser property ID and taint-sink suppression enabled. An attr reached here is not necessarily the canonical custom-name parse context or the unsuppressed ordinary context. A cache keyed only by attr name and ordinary property misses this distinction. |
| Attr lookup/cache | Replacing the raw expression with final CSS tokens loses the alternative nested fallback. Adding context to a result key without retaining raw input cannot reconstruct that expression. |
| Same physical attr through nested references | Distinct request keys must not evade the physical attribute recursion guard. Conversely, one cyclic request must not globally invalidate all consumers of that raw attribute. |

A source-shaped stress case is a registered custom length needing line-height while writing-mode contains a typed attr whose nested tainted var selects a new fallback. The precise CSS cycle oracle needs its own validation, but the call path already disproves “all attrs finish before priority application.” No new browser result is claimed for this example.

## Smallest complete candidate to implement

1. Retain tracked immutable raw attribute input separately from resolved tokens. Seed uses with the actual declaration/substitution property ID, URL/parse environment and suppression mode; discover further selected uses synchronously while walking raw input. Inventory seeds the work but is not the graph. Missing/namespaced attributes and selected fallback reads still pass through `AttributeTracker`.
2. Add contextual attr-use nodes to the existing resolver session. Start with per-use results rather than cross-request memoization. Keep physical attribute guards separate and sticky across nested substitution; custom node identity/defaulting remains canonical. The attr's typed parse and outer fallback belong to its reference occurrence. Raw substitution results need not include the outer type in their key if each occurrence performs its own typed parse; that separation requires an explicit implementation invariant, not a presumed equivalent cache key.
3. Factor one primary classifier shared by dependency discovery and substitution. Visit/resolve the primary first, then apply the current Var sink restriction and typed Attr parsing, then traverse only the selected fallback. Preserve all token/size/security/provenance behavior. Distinguish a final invalid primary from a still-active SCC node; do not call unfinished work invalid merely to force progress. The existing treatment of an unresolved primary is source behavior to audit, not a ready proof for the new contexts.
4. Complete priority scheduling inside that same session before calling the existing final apply path. A node keyed by `PrioritaryPropertyId` can represent generated dependencies, including writing-mode, rather than only the three unit-reference buckets. Keep evaluating versus applied state distinct. Prepare the actual eligible declaration and any subsequently selected revert winner before committing it; never eagerly apply a skipped/reverted declaration. This can be a synchronous driver loop around the existing winner loop, without returning a suspended longhand object to unrelated callers.
5. Add synchronous preparation at each consuming boundary: ordinary `WithVariables`, priority application and keyframe ordinary-declaration preparation. Prepare deferred custom expansions under their existing caller parser ID plus suppression, linked to the canonical custom SCC node without overwriting its canonical value. Then call the existing immutable substitution/parse/cache path with a completed contextual-result view. After custom resolution, ordinary declarations still need their own consumer preparation; the design must not substitute a global settled-map assumption for this step.

A conceptual sequence is:

```
resolve_use(source_arc, use_context, active_session):
    visit selected dependencies recursively with short borrows
    classify primaries and visit their selected fallbacks
    settle participating SCC/physical guards
    return owned ready result or final invalid result

apply selected declaration:
    synchronously prepare its contextual uses in the same session
    substitute and parse from the completed result view
    execute existing revert/seen/style/cache handling once
```

This does not promise that every recursive call can return a ready value: a back edge must return in-progress SCC information to its caller and defer publication until that component is settled. The ordinary call stack, existing Tarjan stack and a per-use result table may be sufficient. A heap-owned syntax continuation is necessary only if a specific edge has to be discovered after that stack frame or SCC root is irretrievably closed. No such necessity is demonstrated merely by the observed nested-fallback failure.

## Closure obligation and decisive falsifiers

The smaller route is complete only if final immutable substitution cannot discover a contextual attr use or value-changing dependency absent from preparation. Add a diagnostic assertion for an unprepared contextual lookup or a mismatched consumer/guard identity before enabling the new path. Preparation and immutable evaluation must preserve the same request context and sticky cycle-invalid outcomes; rebuilding fresh guard IDs or dropping preparation cycle markings cannot make a cached result safe. That assertion is a development falsifier, not a runtime fallback or permission to ship missed cases. One shared classifier helps, but does not alone prove that traversal and substitution produce the same typed/defaulted input.

Test ready and deferred aliases in both consumer orders; direct and custom uses of the same raw attribute; valid primary with unused cyclic fallback versus rejected primary with selected cycle; a selected missing/changed attr fallback; priority writing-mode/line-height reentry; registered CSS-wide/defaulted values; differing shorthand/type/URL contexts; namespaced attributes; keyframe ordinary consumers; and attr-security URL behavior. Preserve the existing unrelated ordinary-winner behavior rather than settle its disputed taint policy by accident.

If SCC invalidation changes a primary to a registered default with previously unprepared references, or parser-context-dependent deferred expansion exposes another use after a component closed, the synchronous approach needs a defined reopening/local continuation rule. It must not silently reset Tarjan, restart longhand commits, add arbitrary retries, or select all syntactic fallbacks. This is the concrete place to prove the simpler route insufficient, instead of assuming suspension is inevitable at the outset.

The current frozen `properties/mod.rs` wrapper is historical supporting evidence only; authenticate the current body before patching. The existing container-query branch also bypasses the cascade-populated attr cache. A complete caller census must decide how that read-only path performs contextual evaluation, rather than route it through nonexistent cascade state. No native patch, compilation, browser execution, settled general cycle policy or correctness proof is provided here.

## Decision

Do not adopt the full owned-cursor API as a prerequisite yet. Keep its useful ownership and guard invariants, but first build the synchronous contextual-DFS seam with complete priority and deferred-alias coverage. Reject the bare inventory/key/classifier-only patch and the ready-var shortcut as incomplete. If the closure assertion or a specific SCC lifecycle case fails, that evidence should determine the narrow extra continuation machinery. General complete correctness remains an implementation obligation; the current evidence supports a smaller candidate architecture, not a proved landable repair.
