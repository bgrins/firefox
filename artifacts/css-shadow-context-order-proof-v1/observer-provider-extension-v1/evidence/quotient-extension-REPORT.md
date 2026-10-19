# Source identity quotient: new universal components

## Result

The allocation/normalized-priority quotient is proved for arbitrary immutable,
reverse-ordered property block projections in the stated two-phase evaluator
model. This is a new component result, not a proof of full native C7/C10/C11/C13.
The complete native provider, evaluator and observer instantiation remains open.
No original scope, source admission or preserved counterexample was changed.

The principal theorem is `source_projected_deletion_quotient` in
`TwoPhaseQuotient.lean`. Its left side uses semantic occurrence identities and
physically deletes all remaining declarations of an occurrence on `Rule`.
Its right side executes the same projected blocks using accumulated allocation/
priority keys. The theorem quantifies over arbitrary block contents, repeated
aliases, occurrence orders, state and effects. Mixed Rule/value actions in one
block are permitted. No per-declaration deterministic action by key is assumed.

The companion `two_phase_occurrence_quotient` proves the underlying statement
for arbitrary important and normal action lists. Important and normal lists may
have different order and multiplicity. Coverage is required only when a normal
occurrence's shared important projection contains Rule. Empty important halves
and blocks with no important Rule do not need a fabricated important occurrence.

## Proof construction

1. `BlockProjection` constructs reverse/filter projections by original-to-physical
   property mapping and importance. It derives event membership and corresponding
   important Rule coverage from an immutable block lookup.
2. `GroupedQuotient` first collapses each complete mixed-action half-block to its
   head using the existing state-preserving local theorem. Only then does it use
   the atomic alias theorem. It proves single-phase computed-state equality with
   fresh exclusions; it does not mistake raw declarations for atomic events.
3. `PhasePruning` proves that initially blocked events can be removed under
   monotonically shrinking eligibility, initial exclusions only matter on
   identities actually present, and every new exclusion comes from a Rule event.
4. `TwoPhaseQuotient` uses those facts to remove normal halves whose important
   block contains Rule. Every such semantic occurrence is already excluded or
   ineligible after important processing. Remaining normal events cannot be in
   either initial exclusion set, so their normal phase can start with fresh
   exclusions. Single-phase quotient equality then composes across both phases.
5. `Nonvacuity` supplies an admitted witness with two distinct occurrences sharing
   an important Rule and mixed normal values 5/13. Both executions reach the
   separate fallback 37. This verifies that the premises admit the motivating
   mixed-importance alias case.

This is equality of the computed state supplied to the model. It intentionally
is not equality of semantic-ID and allocation-ID exclusion lists.

## Exact remaining premises

| Premise | Mathematical result | Native admission still needed |
| --- | --- | --- |
| Immutable full source blocks | Projection uses a single lookup per key; earlier `SourceCoherence` constructs coherent allocation-backed rule lists | Complete constructor/provider/FFI and lock lifetime closure, including synthetic/direct declaration callers; relate `RawStyleRule` declarations to this projected declaration type |
| Exact identity key | Arbitrary quotient function is supported | Bind physical longhand plus allocation address plus exact `CascadePriority::unimportant()` equality; retain flags, origin, context and layer, not merely ordering equivalence |
| Phase construction | Arbitrary order/multiplicity; only relevant Rule coverage required | Derive occurrence pairing from actual rule-tree construction, elision, sort, importance iterator and buffering; no prearranged stream added to `rawAdmitted` |
| Transition prefix | Initial computed state is arbitrary | The actual transition normal node precedes important nodes in reverse iteration; factor that prefix with an admitted no-Rule/terminal provider contract, or extend the stream theorem. The current theorem is not a proof that every native stream is simply important then normal |
| Uniform eligibility | Eligibility depends on current state and quotient key | Bind seen state, included flags, pseudo restrictions and cumulative cutoff predicates for every property pass; prove candidate importance does not change these tests for a normalized key |
| Self-disabling non-Rule effects | Required explicitly; used only after an admitted effect | Terminal seen insertion and retained origin/layer cuts have local support; include invalid substitution, ignore-colors fallback, registered custom properties, prioritary-property callbacks and every early exit |
| No eligibility reenabling | Required explicitly | Repaired A+B+D cumulative cutoff component supports the cutoff part; compose all other evaluator state updates rather than assuming the whole evaluator is monotone |
| Stable ordered actions | Arbitrary mixed action lists, fixed per block/key/phase | Substitution, custom values, dependencies, visited filtering and evaluation must yield the same relevant action for corresponding declarations. This is weaker than false raw action determinism, but is still an unproved native premise |
| Observers | Computed-state equality only unless observers are included with valid effect laws | See the explicit observation obstruction below; scope restoration, cache/dependency observers and final publication remain separate obligations |

A theorem parameter is not evidence that native construction satisfies it. In
particular, no restriction was silently added to the approved arbitrary raw
collector/input domain to obtain this result.

## Exact native review binding

Retained `cascade.rs` SHA256:
`c24e1a917fadc22ede8737434ff940bc670459c24c77f7d0608b415a4a656684`.
Retained `applicable_declarations.rs` SHA256:
`e346cc700aee5a322fad664ccde52ae12043adbd7aa30b06403ac2ab78f371e5`.
These are the corrected A+B+D then C semantics, not the original A candidate.
`ROOT-STACK-VALIDATION-v1.json` remains the finite stack evidence: no-C assigned
80 pass; C's no-C baseline has 20 failures across D64+C72; full C has 136 pass.
Those finite results are retained as context and were not expanded or rerun.

Source inspection confirms:

- `DeclarationIterator::next` reverses the block iterator and filters importance
  and pseudo restrictions. It carries the block reference to buffering.
- `CascadePriority` exact equality/hash includes flags. `unimportant()` preserves
  flags and layer while normalizing the level. Ordering equality alone is an
  insufficient native identity contract.
- `apply_one_longhand` checks seen/flags/cutoffs/source exclusions before variable
  substitution. Rule adds the physical-property/exact-priority/source key;
  non-Rule rollback accumulates `RevertState` instead of replacing prior cuts.
- `RevertState::allows` conjoins origin, ordinary layer and important-inline
  layer predicates. The retained-cutoff model applies to this corrected source;
  it cannot justify the original A or saturation-only source.
- The custom-property consumer has its own unique-name, registration and
  substitution machinery. This longhand block-quotient theorem is not its full
  evaluator proof. Original-property uniqueness must be admitted where that
  consumer relies on it; the logical alias counterexample cannot be discarded.

## Observer/evaluator obstruction

`apply_non_prioritary_properties` records a writing-mode dependency for a logical
property before `apply_one_longhand` checks whether its source has been excluded.
Thus a physical Rule followed by an excluded logical declaration can leave a
writing-mode dependency even though that logical declaration contributes no value.
A reference that deletes events before this observation phase will not have the
same dependency observation.

`ObserverBoundary.observation_before_guard_not_deletion_invariant` proves the
small abstract counterexample: native raw traversal observes a logical event,
whereas deleting the excluded event first does not. Both selected-value models
still agree, as separately proved. This refutes that particular observer
composition, not CSS computed-style correctness or the repaired native patch.

To finish the observer obligation, preserve a separate pre-filter observation
pass over the appropriate raw stream, or prove a specified abstraction permits
conservative dependency additions. Exact trace/count equality cannot follow
from the computed-state quotient theorem. Variable substitution also mutates
cache conditions, builder flags, shorthand cache and attribute tracking; Rule is
state-neutral in the current control model, so those effects need an explicit
extension/admission rather than being hidden inside its Rule branch.

## Approved obligations and next work

- C7: the mixed-block, two-phase quotient component is now proved. Complete
  allocation/flag source binding, elision and provider admission remain open.
- C10: corrected occurrence deletion plus cumulative cutoff composition has
  stronger component support. Full native evaluation and complete raw-stream
  correspondence remain open; original saturation-only and A refutations stand.
- C11: the inherited scoped-reference no-path counterexample remains unresolved.
  No relative integer/quotient proof repairs root ownership or provider identity.
- C13: selected model state equality is stronger; full observer/evaluator and
  publication composition remains open. The pre-filter observer mismatch is an
  explicit obstruction to a naive deletion-before-observation reference.
- C1–C6, C8–C9 and C12: no closure claim or admission change. Existing exact raw
  provider, numeric, iterator and scope-restoration requirements still apply.

The next useful composition is to derive phase occurrence coverage and immutable
projection from the actual complete rule-path/iterator construction, including
transition and direct declaration providers, while extending the evaluator model
with pre-guard observations and substitution effects. This package supplies the
previously missing abstract quotient target for that work. It does not replace
that work with a finite matrix or declare the full formal goal complete.

## Replay

`replay.py` first authenticates `INPUTS.json`. With only `--lean` and a new
`--output` directory, it copies the retained `.lean` closure into a new temporary
directory, compiles every module from source, and checks every new theorem's
axiom report. It imports no historical project `.olean` cache. The official pinned
Lean distribution supplies `Std` and foundational modules. The accepted axiom
set is limited to `propext`, `Classical.choice`, and `Quot.sound`.

Run integrity only:

```
python3 replay.py
```

Run a fresh proof replay:

```
python3 replay.py --lean /path/to/lean-4.35.0-rc4/bin/lean --output /new/output/path
```

`replay-final-v1/RESULT.json` records the fresh result. `replay-v1` contains retained
development attempts, including failed intermediate proofs; they are not the
accepted replay and are not inputs. Root acceptance and independent review of
these producer-authored new proofs remain separate gates.
