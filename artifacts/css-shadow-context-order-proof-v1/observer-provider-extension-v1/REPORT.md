# Observer and constructor extension

## Result and scope

This extension proves an observer-preserving relation for the repaired A+B+D then
C control model, including raw logical writing-mode dependency observation,
important/normal phases and an animation-produced transition prefix. It also
replaces the per-rule important-coverage hypothesis with a theorem about the
actual modeled bucket constructor and its sorting/reverse iteration.

These are universal components with retained native source correspondence.
They do not complete C1–C13 or establish every native provider/evaluator premise.
The frozen source quotient extension and its deletion-before-observation
counterexample are unchanged; `ObserverBoundary` is included in this replay.
The original saturation-only, original A and scoped-root ownership refutations
remain in force. No native, WPT, Git, build or browser action was performed.

## Observer relation

`PreGuardObservers.preObservedExecution` records each declaration's annotation
before checking accumulated rule exclusions or eligibility. Its observer state
and evaluator state are separate. The independent deletion reference physically
removes declarations for value selection but retains raw traversal for these
pre-guard observations. This models the actual order in
`apply_non_prioritary_properties` and `apply_one_longhand`; it does not move the
native observation after rollback checks.

`pre_guard_observation_factorization` proves that the interleaved execution equals
an ordered raw observer fold paired with exclusion-based evaluation. It works for
arbitrary observation state/functions; observations need not be commutative or
idempotent. They must not feed back into eligibility/effects: that separation is
expressed in the model's function types, and native admission must justify it.

`two_phase_full_pre_guard_refinement` composes the previous mixed-block quotient
with this factorization. Its conclusion is equality of **both observer state and
evaluator state**, not selected value alone. Annotations are retained throughout
identity mapping, including annotations on excluded declarations. No raw
per-declaration deterministic-action premise was introduced.

For writing mode, the observer is the actual `Option<WritingMode>` assignment
shape: a selected logical declaration stores `Some(current writing mode)`;
otherwise the previous option remains. `writing_mode_observer_exact` proves the
result for arbitrary raw lists. `writing_mode_debug_invariant_preserved` retains
the native assertion condition, assuming the initial option is empty or already
equal to the current writing mode. `writing_mode_repeated_block_idempotent`
proves repeating an identical block leaves that observer unchanged.

The mathematical mode value is a `Nat` token; the proof uses equality/assignment,
not any interpretation of writing-mode bit fields. Binding the token to the
actual receiver and proving it is stable throughout the relevant property pass
remain required. The fixed-mode and initial debug-invariant premises are not
new restrictions on the approved raw domain.

## Important occurrence construction

`ConstructedCoverage` uses the existing `treePartition` implementation model and
`empty_tree_partition_important_buckets`, not an arbitrary prearranged important
stream. It follows author/user/UA bucket collection, per-bucket sorting, bucket
concatenation and reverse ancestor iteration.

The new coverage proof establishes:

1. An event in a reverse/filter important property projection implies an actual
   important bit in the source declaration list.
2. A source with that bit and an author/user/UA origin is inserted into the
   corresponding important bucket.
3. Both the sort-skipped and sorted branches preserve membership, irrespective
   of whether a skip is justified for ordering. Coverage therefore needs no new
   monotonicity assumption on sort keys.
4. Normal-only sources have empty important projections. Consequently every
   relevant normal occurrence with an important Rule has its corresponding
   important occurrence when the provider is author/user/UA or normal-only.

`constructed_important_covers_resolved_event` also permits an arbitrary declaration
resolver and any resulting action. It does not assume that only literal
`revert-rule` declarations can generate Rule after substitution. This establishes
bit/bucket coverage for such an event; it does not prove stable evaluation across
aliases or manufacture a resolver correspondence for native substitutions.

`ProviderBits` additionally bridges actual parallel declaration/importance data:
an important event visible through the zip iterator implies a true bit in the
provider vector, hence native `any_important`. This direction requires no
assumption that the two arrays have equal lengths. It covers arbitrary resolved
actions while preserving the actual importance bit. Full block length and
mutation invariants remain required for complete provider correspondence.

Source binding is to `RuleTree::insert_ordered_rules_with_important`,
`PropertyDeclarationBlock::any_important`, `DeclarationImportanceIterator`, and
reverse `DeclarationIterator` traversal. `compute_rule_node` removes adjacent
matching source/exact-priority entries *before* both normal and important
construction. `ensure_child` interns a child under its parent; it does not drop
an important occurrence merely because a parent has the same key.

The theorem quantifies over the list entering bucket construction. A full raw
collector-to-node proof still must relate pre-elision semantic occurrences to
that surviving list, bind heap/lock identity and actual iterator interfaces, and
cover replacement/direct-declaration entry points. Writing-mode observation is
idempotent under repeated blocks; complete evaluator idempotence still needs its
own admission. We do not claim these obligations are discharged by membership
alone.

## Transition provider and prefix

The retained actual provider chain is:

- `RuleCollector::collect_animation_rules` appends the transition declaration
  source after the animation source.
- `get_animation_rule` receives typed `AnimationValueMap` entries from
  `Gecko_GetAnimationRule` and calls `PropertyDeclarationBlock::from_animation_value_map`.
- That constructor uncomputes every value and creates an equal-length bit vector
  filled with `false`.
- `AnimationValue::uncompute` creates concrete longhand variants. Its custom arm
  uses `CustomAnimatedValue::to_declaration`: a present value yields Parsed or
  Unparsed, and an absent value yields the Initial keyword. Those constructors
  do not emit CSS-wide rollback variants.
- Rule-tree construction stores the final transition separately when important
  declarations were found, then inserts it after the important buckets. Reverse
  traversal therefore visits its normal declarations first.

`AnimationConstructors` models those output variants and list/bit construction.
It proves length agreement, absence of important bits, consistency with the zip
importance iterator, normal-only declarations and absence of rollback actions.
The proof derives these facts from construction; they are not free no-Rule
hypotheses on the constructed transition list.

`TransitionObservers` proves a no-Rule prefix keeps exclusions fresh, preserves
raw observations and can be factored before the two-phase relation.
`constructed_transition_observer_refinement` supplies that prefix from the typed
animation constructor, so the previous important-then-normal simplification is
no longer needed for this constructed transition case.

Native boundaries remain explicit: the animation constructor model assumes valid
typed AnimationValue variants. The generated uncompute implementation has unsafe
layout/tag operations; their validity, FFI input validity, complete variants,
provider ownership, freshness and call selection are not proved by the Lean
constructor model. We retain the actual source and classify this as a source
binding with those native admissions, not a universal Rust/FFI theorem. SMIL,
presentation-hint and alternative/direct providers still need their own
normal-only/metadata construction admission. The transition-placement uniqueness
and final-position contract remains tied to the complete collector chain.

## Remaining evaluator obstruction

The new exact relation covers **pre-guard** observations. It does not silently
classify every native mutation as one of those observations.

In the retained cascade source, `substitute_variables_if_needed` runs after the
rollback/seen guards and can set uncacheability, builder flags, shorthand cache
and attribute tracking before the result is recognized as Rule. The existing
control model makes Rule evaluator-state-neutral. A direct instantiation that
hides all substitution mutations in that state-neutral branch is invalid.

`EvaluationBoundary.exact_evaluation_visit_observer_not_quotient_invariant`
proves a precise obstruction to one overly strong extension: two distinct Rule
occurrences visit evaluation twice, while their shared-key execution visits it
once. Selected control state still agrees. Thus arbitrary exact evaluation logs
or invocation counts cannot be preserved by this quotient.

This is a counterexample to an unrestricted abstract observer claim, **not** a
new native computed-style defect or a claim that this exact alias pair is native
reachable. Actual cache flags/dependency collections may admit an idempotent
state abstraction. Completing that proof requires deriving each observer's
algebra and stable associated declaration/provider data, or showing problematic
sharing unreachable. The current theorem must not be instantiated for those
post-guard effects without that work.

## Native evidence authentication

`SOURCE-BINDING.json` records six frozen constructor/collector source hashes and
fresh exact equality with the local files at capture. The repaired cascade and
priority sources remain bound to the earlier frozen candidate:

- cascade: `c24e1a917fadc22ede8737434ff940bc670459c24c77f7d0608b415a4a656684`
- applicable declarations: `e346cc700aee5a322fad664ccde52ae12043adbd7aa30b06403ac2ab78f371e5`

Searchfox discovery initially failed in the restricted network environment;
read-only escalated retrieval succeeded. Retrieved `rule_cache.rs` and custom
value source matched local bytes. The indexed animated-property template differs
from local only at a later variable-substitution call. Both copies and the exact
diff are retained; the reviewed `uncompute` body is unchanged. Indexed source is
not treated as an exact full-file pin for that local template.

## Obligation status

| Obligation | New progress | Still open |
| --- | --- | --- |
| C7 | Mixed-block quotient now composes with exact raw pre-guard observations; writing-mode block repetition is idempotent | Complete source/flag/allocation identity, pre-elision semantic association and evaluator idempotence |
| C10 | Important Rule coverage follows bucket construction; typed transition prefix is composed with corrected cumulative cutoff and occurrence deletion models | Native raw-to-iterator composition, provider/FFI contracts, evaluation stability and all branches |
| C11 | No scope change | Inherited scoped-root no-path refutation and actual root ownership/provider repair |
| C13 | Observer-state plus evaluator-state equality for the separated pre-guard model; exact writing-mode setter/invariant | Full post-guard substitution effects, all observers, custom-property evaluation, prioritary/cross-property passes, publication and scope restoration |

C1–C6, C8–C9 and C12 are not newly declared complete. Full approved scope remains
open, with all original counterexamples and admissions preserved.

## Replay and review

`replay.py` authenticates `INPUTS.json`, copies only retained `.lean` sources to a
fresh temporary directory, compiles the complete dependency closure, and audits
all new theorems. Only standard `propext`, `Classical.choice`, and `Quot.sound`
axioms are accepted. No historical project `.olean` files are imported.

```
python3 replay.py
python3 replay.py --lean /path/to/lean-4.35.0-rc4/bin/lean --output /new/output/path
```

`replay-final-v3/RESULT.json` is the fresh result; development files under `work`
are not accepted inputs. These seven new modules are producer-authored and still
need separate review. Root owns final acceptance.
