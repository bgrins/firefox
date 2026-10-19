import ObservedPhases
namespace ShadowOrder
variable {σ ω : Type}

theorem pre_guard_fresh_deletion [DecidableEq κ]
 (observe : ω → β → ω) (eligible : σ → OccurrenceEvent κ α → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (entries : List (AnnotatedOccurrence κ α β)) (observation : ω) (state : σ) :
 preObservedExecution observe eligible apply entries [] observation state =
 observedDeletionReference observe eligible apply entries observation state := by
 rw [pre_guard_observation_factorization,fresh_occurrence_deletion]
 rfl

theorem no_rule_observed_prefix [DecidableEq κ]
 (observe : ω → β → ω) (eligible : σ → OccurrenceEvent κ α → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (leading suffix : List (AnnotatedOccurrence κ α β))
 (noRule : ∀ entry ∈ leading, entry.event.action ≠ .rule)
 (observation : ω) (state : σ) :
 preObservedExecution observe eligible apply (leading ++ suffix) [] observation state =
 let advanced := preObservedExecution observe eligible apply leading [] observation state
 preObservedExecution observe eligible apply suffix [] advanced.1 advanced.2 := by
 induction leading generalizing observation state with
 | nil => rfl
 | cons first rest ih =>
   have tail : ∀ entry ∈ rest, entry.event.action ≠ .rule :=
     fun entry member => noRule entry (by simp [member])
   have firstNoRule := noRule first (by simp)
   cases action : first.event.action with
   | rule => exact False.elim (firstNoRule action)
   | effect value =>
     simp only [List.cons_append,preObservedExecution,List.not_mem_nil,↓reduceIte,action]
     cases enabled : eligible state first.event <;>
       simp only [Bool.false_eq_true,↓reduceIte] <;> exact ih tail _ _

theorem no_rule_prefix_key_quotient [DecidableEq ι] [DecidableEq κ]
 (key : ι → κ) (observe : ω → β → ω)
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (leading : List (AnnotatedOccurrence ι α β))
 (noRule : ∀ entry ∈ leading, entry.event.action ≠ .rule)
 (observation : ω) (state : σ) :
 preObservedExecution observe (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value) leading [] observation state =
 preObservedExecution observe (fun s event => eligible s event.identity)
   (fun s event value => apply s event.identity value)
   (leading.map (mapAnnotatedKey key)) [] observation state := by
 induction leading generalizing observation state with
 | nil => rfl
 | cons first rest ih =>
   have tail : ∀ entry ∈ rest, entry.event.action ≠ .rule :=
     fun entry member => noRule entry (by simp [member])
   have firstNoRule := noRule first (by simp)
   cases action : first.event.action with
   | rule => exact False.elim (firstNoRule action)
   | effect value =>
     simp only [List.map_cons,preObservedExecution,List.not_mem_nil,↓reduceIte,
       mapAnnotatedKey,action]
     cases enabled : eligible state (key first.event.identity) <;>
       simp only [Bool.false_eq_true,↓reduceIte] <;> exact ih tail _ _

theorem mapped_prefix_no_rule (key : ι → κ)
 (leading : List (AnnotatedOccurrence ι α β))
 (noRule : ∀ entry ∈ leading, entry.event.action ≠ .rule) :
 ∀ entry ∈ leading.map (mapAnnotatedKey key), entry.event.action ≠ .rule := by
 intro entry member
 rcases List.mem_map.mp member with ⟨original,present,rfl⟩
 exact noRule original present

theorem transition_prefixed_observer_refinement [DecidableEq ι] [DecidableEq κ]
 (key : ι → κ) (important normal : κ → List (AliasDecision α × β))
 (observe : ω → β → ω) (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (disables : ∀ state identity value, eligible (apply state identity value) identity = false)
 (monotone : ∀ state identity value other,
   eligible state other = false → eligible (apply state identity value) other = false)
 (leading : List (AnnotatedOccurrence ι α β))
 (noRule : ∀ entry ∈ leading, entry.event.action ≠ .rule)
 (is ns : List ι)
 (coverage : ∀ occurrence ∈ ns,
   AliasDecision.rule ∈ (important (key occurrence)).map Prod.fst → occurrence ∈ is)
 (observation : ω) (state : σ) :
 observedDeletionReference observe (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value)
   (leading ++ (annotatedPhase key important is ++ annotatedPhase key normal ns)) observation state =
 preObservedExecution observe (fun s event => eligible s event.identity)
   (fun s event value => apply s event.identity value)
   (leading.map (mapAnnotatedKey key) ++
    (annotatedPhase (fun x => x) important (is.map key) ++
     annotatedPhase (fun x => x) normal (ns.map key))) [] observation state := by
 rw [← pre_guard_fresh_deletion,
   no_rule_observed_prefix _ _ _ leading _ noRule,
   no_rule_observed_prefix _ _ _ (leading.map (mapAnnotatedKey key)) _
     (mapped_prefix_no_rule key leading noRule),
   no_rule_prefix_key_quotient key observe eligible apply leading noRule]
 dsimp only
 rw [pre_guard_fresh_deletion]
 exact two_phase_full_pre_guard_refinement key important normal observe eligible apply
   disables monotone is ns coverage _ _

#print axioms pre_guard_fresh_deletion
#print axioms no_rule_observed_prefix
#print axioms no_rule_prefix_key_quotient
#print axioms transition_prefixed_observer_refinement
end ShadowOrder
