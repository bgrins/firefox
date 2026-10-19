import PreGuardObservers
namespace ShadowOrder
variable {σ ω : Type}

def annotatedPhase (key : ι → κ) (actions : κ → List (AliasDecision α × β))
 (occurrences : List ι) : List (AnnotatedOccurrence ι α β) :=
 occurrences.flatMap fun occurrence =>
   (actions (key occurrence)).map fun action => ⟨⟨occurrence,action.1⟩,action.2⟩

theorem annotated_phase_projection (key : ι → κ)
 (actions : κ → List (AliasDecision α × β)) (occurrences : List ι) :
 (annotatedPhase key actions occurrences).map (·.event) =
 phaseEvents key (fun identity => (actions identity).map Prod.fst) occurrences := by
 simp [annotatedPhase,phaseEvents,halfStream,blockHalfEvents,List.map_flatMap,List.flatMap_map,List.map_map,Function.comp_def]

theorem annotated_phase_key_map (key : ι → κ)
 (actions : κ → List (AliasDecision α × β)) (occurrences : List ι) :
 (annotatedPhase key actions occurrences).map (mapAnnotatedKey key) =
 annotatedPhase (fun x => x) actions (occurrences.map key) := by
 simp [annotatedPhase,mapAnnotatedKey,List.map_flatMap,List.flatMap_map,List.map_map,Function.comp_def]

theorem two_phase_full_pre_guard_refinement [DecidableEq ι] [DecidableEq κ]
 (key : ι → κ) (important normal : κ → List (AliasDecision α × β))
 (observe : ω → β → ω) (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (disables : ∀ state identity value, eligible (apply state identity value) identity = false)
 (monotone : ∀ state identity value other,
   eligible state other = false → eligible (apply state identity value) other = false)
 (is ns : List ι)
 (coverage : ∀ occurrence ∈ ns,
   AliasDecision.rule ∈ (important (key occurrence)).map Prod.fst → occurrence ∈ is)
 (observation : ω) (state : σ) :
 observedDeletionReference observe (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value)
   (annotatedPhase key important is ++ annotatedPhase key normal ns) observation state =
 preObservedExecution observe (fun s event => eligible s event.identity)
   (fun s event value => apply s event.identity value)
   (annotatedPhase (fun x => x) important (is.map key) ++
    annotatedPhase (fun x => x) normal (ns.map key)) [] observation state := by
 have mapping :
   ((annotatedPhase key important is ++ annotatedPhase key normal ns).map (mapAnnotatedKey key)) =
   annotatedPhase (fun x => x) important (is.map key) ++
   annotatedPhase (fun x => x) normal (ns.map key) := by
   simp only [List.map_append,annotated_phase_key_map]
 rw [← mapping]
 apply full_pre_guard_observer_refinement
 rw [mapping,List.map_append,List.map_append,
   annotated_phase_projection,annotated_phase_projection,
   annotated_phase_projection,annotated_phase_projection]
 have quotient := two_phase_occurrence_quotient key
   (fun identity => (important identity).map Prod.fst)
   (fun identity => (normal identity).map Prod.fst)
   eligible apply disables monotone is ns coverage state
 simpa only [twoPhaseExecution,occurrence_state_projection] using quotient

#print axioms annotated_phase_projection
#print axioms annotated_phase_key_map
#print axioms two_phase_full_pre_guard_refinement
end ShadowOrder
