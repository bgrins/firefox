# Source mapping and provider contract

All retained C++/Rust/generated sources are exact authenticated inputs from the accepted independent native review. `SOURCE-PINS.json` connects each byte copy to that review's manifest. The original and candidate Document snapshots differ in the already accepted startup hunk. Current unrelated worktree edits are not consumed.

## Normative reference

Retained primary CSS View Transitions 2 `dom-element-startviewtransition` clones options types as a set; Document delegates to its root. `viewtransition-active-types` and the `types` getter identify the same mutable setlike DOMString contents. `the-active-view-transition-type-pseudo` reads existence of at least one query argument in the active transition. Infra `ordered-set`/`set-append` and Web IDL `idl-setlike`/`es-set-delete`/`es-set-clear` supply uniqueness, insertion order, prior-membership return and emptying semantics. This repair uses ordinary active visible document-root transitions. Newer scoped-transition lifecycle algorithms and invalid/reserved identifier disagreements are not imported wholesale.

`OrderedTypes.firsts` selects the first occurrence while scanning input order. `TypeMutations.reference` models the independent public ordered-set operations: append absent values, filter every equal value on deletion, clear all entries. The source model uses first-match native erasure. The theorem equating these deletions needs uniqueness; its missing-premise witness fails for `[a,a]`.

## Startup and ownership

The complete `Document::StartViewTransition`, same-document constructor and `ViewTransition::Types` are bound. The executable extraction retains the exact startup option-projection block through completion of its loop, then returns its local vector to an adapter that invokes the exact constructor. Callback/null option branches are exercised for their type projection only. Hidden/previous-transition branches, event scheduling and root-state installation remain source/browsing premises, not executed in the extraction.

`initialStep` reflects `EnsureInserted` and vector append; `initialRun` models successive loop iterations. Its prefix theorem gives first-occurrence order, native uniqueness and seen/vector membership equality. The seen set is represented extensionally; no hash-table iteration supplies order. The source hash wrapper, weak-key specialization, pointer comparison and count-based insertion body are bound. Actual infallible allocation, hashtable soundness and pointer hash behavior are provider premises; the extracted count-based insertion executes over an adapter table with deliberate hash collisions.

The weak-key proofs establish an owning vector reference exists at iteration boundaries; during insertion the current local reference additionally owns the new atom. Actual `RefPtr`, moves, reallocations, atom caches, thread confinement and lifetime transitions are source-reviewed provider semantics, not a C++ memory-safety proof. The temporary seen set's scope ends before the vector transfers into the transition.

## Atom identity across time

DOMString is `List UInt16`, not a Unicode-scalar string. Exact length/code-unit equality, embedded NULs, lone surrogates, case distinctions and non-normalized combining sequences remain distinct. The complete native atom equality function executes in the extraction. Native atom-table lookup/insertion and both UTF-16 entry functions are retained for source review; caches and locks are not compiled here.

`AtomProvider.Provider` is a stable value-identity abstraction with `text(intern(s))=s`. Its transport theorem does not assert a raw address is immortal. `LiveAtoms` supplies the more faithful lifetime boundary: atoms are nominal allocation-generation identities with immutable text. Canonicality is required only against currently retained native atoms. Initialization has a per-prefix provider trace; successful mutations require an atom only on branches that actually atomize. A deleted value may be re-added using a different allocation generation. The regenerated witness exercises exactly that case. No global injectivity of text over dead and live allocations is assumed by these live-provider theorems.

The source bridge must map simultaneously live raw pointers to distinct generation identities, preserve immutable text while referenced and have atomization return the extant identity for an equal live string. Address reuse after lifetime end is allowed. This is an explicit provider obligation, not inferred from abstract equality alone.

## Public backing and mutations

`materialize` copies native contents through ordered-set insertion on first getter access, retaining an existing backing representation on later access. Its correctness requires successful helper initialization. Native `IgnoreErrors()` is retained as an excluded failure boundary; a counterexample with partial backing contents refutes unconditional agreement. Idempotent modeled materialization is not a proof of JS wrapper identity or live iterator behavior; the extraction separately checks repeated getter pointer identity.

The complete Add/Delete/Clear methods execute unchanged in the adapter. Generated `SetlikeHelpers` are bound as a whole: realm/wrapper acquisition and DOMString conversion can fail before JS Set calls. The successful path supplies Has/Add/Delete/Clear behavior; JS Set, realm/GC/OOM and conversion implementations are admitted. Error and allocation failure paths are not erased into successful operations. The Lean successful-history theorem covers arbitrarily many operations and exact reply sequences, preserving transition/document fields. Add returns the transition-associated self identity in the abstract interface; the actual adapter checks the returned TypeSet pointer.

The full source array IndexOf and RemoveElement bodies are retained. Source first-match removal maps to Lean `List.erase`; adapter `std::find`/vector erasure implements that provider contract. No whole nsTArray translation proof is claimed.

## Direct selector observation

The actual Gecko Stylo branch checks ACTIVE_VIEW_TRANSITION state and sends the element's owner document to the bound C++ bridge. The bridge reads that document's active transition and its native vector, returns false for absent/empty state, then tests any query argument with its validity filter. The complete bridge and IsValidViewTransitionType execute in the extraction. The Rust branch and macro-generated state flag are separately bound static source; they were supplemental snapshots in the original review, not original browser-run pins.

The world model keeps queried document, root flag, active-state flag, active transition identity and installed native vector separate. `successful_history_observation` needs the correct owner, active identity, installed resulting list, root/state and valid query premises. `root_state_refines` additionally exposes the relationship between native state flags and spec root/active predicates. Wrong owner, false state, nonroot stale state and invalid-name witnesses prevent inferring more. No restyle invalidation, rendering flush or cache observation follows from direct matching.

The native calibration directly constructs CustomIdent wrappers to exercise the bridge; it does not parse selector syntax. For empty/NUL/surrogate values, these queries are provider controls only and must not be called valid parsed CSS selectors. The public TypeSet can still contain arbitrary strings. Native's actual `none`/`-ua-` filter is retained; no general agreement with spec for those queries is claimed.
