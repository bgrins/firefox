import TwoPhaseQuotient
namespace ShadowOrder
variable {σ ω : Type}

structure AnnotatedOccurrence (κ α β : Type) where
 event : OccurrenceEvent κ α
 annotation : β

def preObservedExecution [DecidableEq κ]
 (observe : ω → β → ω) (eligible : σ → OccurrenceEvent κ α → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ) :
 List (AnnotatedOccurrence κ α β) → List κ → ω → σ → ω × σ
 | [], _, observation, state => (observation,state)
 | entry::rest, excluded, observation, state =>
   let observation := observe observation entry.annotation
   if entry.event.identity ∈ excluded then
     preObservedExecution observe eligible apply rest excluded observation state
   else if eligible state entry.event then
     match entry.event.action with
     | .rule => preObservedExecution observe eligible apply rest
         (entry.event.identity::excluded) observation state
     | .effect value => preObservedExecution observe eligible apply rest excluded observation
         (apply state entry.event value)
   else preObservedExecution observe eligible apply rest excluded observation state

def rawObservation (observe : ω → β → ω)
 (entries : List (AnnotatedOccurrence κ α β)) (observation : ω) :=
 entries.foldl (fun current entry => observe current entry.annotation) observation

theorem pre_guard_observation_factorization [DecidableEq κ]
 (observe : ω → β → ω) (eligible : σ → OccurrenceEvent κ α → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (entries : List (AnnotatedOccurrence κ α β)) (excluded : List κ)
 (observation : ω) (state : σ) :
 preObservedExecution observe eligible apply entries excluded observation state =
 (rawObservation observe entries observation,
  occurrenceSetExecution eligible apply (entries.map (·.event)) excluded state) := by
 induction entries generalizing excluded observation state with
 | nil => rfl
 | cons entry rest ih =>
   simp only [preObservedExecution,rawObservation,List.foldl_cons,List.map_cons,occurrenceSetExecution]
   split
   · exact ih _ _ _
   · split
     · cases entry.event.action <;> exact ih _ _ _
     · exact ih _ _ _

def mapAnnotatedKey (key : ι → κ) (entry : AnnotatedOccurrence ι α β) :
 AnnotatedOccurrence κ α β :=
 ⟨⟨key entry.event.identity,entry.event.action⟩,entry.annotation⟩

theorem quotient_preserves_raw_observation (key : ι → κ) (observe : ω → β → ω)
 (entries : List (AnnotatedOccurrence ι α β)) (observation : ω) :
 rawObservation observe (entries.map (mapAnnotatedKey key)) observation =
 rawObservation observe entries observation := by
 induction entries generalizing observation with
 | nil => rfl
 | cons entry rest ih => exact ih _

def observedDeletionReference [DecidableEq ι]
 (observe : ω → β → ω) (eligible : σ → OccurrenceEvent ι α → Bool)
 (apply : σ → OccurrenceEvent ι α → α → σ)
 (entries : List (AnnotatedOccurrence ι α β)) (observation : ω) (state : σ) :=
 (rawObservation observe entries observation,
  occurrenceDeletionReference eligible apply (entries.map (·.event)) state)

theorem full_pre_guard_observer_refinement [DecidableEq ι] [DecidableEq κ]
 (key : ι → κ) (observe : ω → β → ω)
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (entries : List (AnnotatedOccurrence ι α β)) (observation : ω) (state : σ)
 (quotient : occurrenceSetExecution (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value) (entries.map (·.event)) [] state =
   occurrenceSetExecution (fun s event => eligible s event.identity)
     (fun s event value => apply s event.identity value)
     ((entries.map (mapAnnotatedKey key)).map (·.event)) [] state) :
 observedDeletionReference observe (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value) entries observation state =
 preObservedExecution observe (fun s event => eligible s event.identity)
   (fun s event value => apply s event.identity value)
   (entries.map (mapAnnotatedKey key)) [] observation state := by
 rw [pre_guard_observation_factorization,quotient_preserves_raw_observation]
 unfold observedDeletionReference
 rw [← fresh_occurrence_deletion,quotient]

structure WritingModeAnnotation where
 selected : Bool
 logical : Bool
 deriving DecidableEq, Repr

def observeWritingMode (writingMode : Nat) (current : Option Nat)
 (annotation : WritingModeAnnotation) : Option Nat :=
 if annotation.selected && annotation.logical then some writingMode else current

theorem writing_mode_observer_exact (writingMode : Nat)
 (entries : List (AnnotatedOccurrence κ α WritingModeAnnotation)) (current : Option Nat) :
 rawObservation (observeWritingMode writingMode) entries current =
 if entries.any (fun entry => entry.annotation.selected && entry.annotation.logical)
 then some writingMode else current := by
 induction entries generalizing current with
 | nil => rfl
 | cons entry rest ih =>
   simp only [rawObservation,List.foldl_cons]
   rw [← rawObservation,ih]
   cases selected : entry.annotation.selected <;> cases logical : entry.annotation.logical <;>
     cases tail : rest.any (fun entry => entry.annotation.selected && entry.annotation.logical) <;>
     simp [observeWritingMode,selected,logical,tail]

theorem writing_mode_debug_invariant_preserved (writingMode : Nat)
 (entries : List (AnnotatedOccurrence κ α WritingModeAnnotation)) (current : Option Nat)
 (valid : current = none ∨ current = some writingMode) :
 rawObservation (observeWritingMode writingMode) entries current = none ∨
 rawObservation (observeWritingMode writingMode) entries current = some writingMode := by
 rw [writing_mode_observer_exact]
 split
 · exact Or.inr rfl
 · exact valid

theorem writing_mode_repeated_block_idempotent (writingMode : Nat)
 (entries : List (AnnotatedOccurrence κ α WritingModeAnnotation)) (current : Option Nat) :
 rawObservation (observeWritingMode writingMode) (entries ++ entries) current =
 rawObservation (observeWritingMode writingMode) entries current := by
 rw [writing_mode_observer_exact,writing_mode_observer_exact,List.any_append]
 cases observed : entries.any (fun entry => entry.annotation.selected && entry.annotation.logical) <;>
   rfl

#print axioms writing_mode_repeated_block_idempotent
#print axioms pre_guard_observation_factorization
#print axioms full_pre_guard_observer_refinement
#print axioms writing_mode_observer_exact
#print axioms writing_mode_debug_invariant_preserved
end ShadowOrder
