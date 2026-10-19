import BlockProjection
namespace ShadowOrder
variable {σ : Type}

def atomicEvents (decision : ι → AliasDecision α) (occurrences : List ι) :=
 occurrences.map fun occurrence => (⟨occurrence,decision occurrence⟩ : OccurrenceEvent ι α)

theorem atomic_set_execution [DecidableEq ι]
 (decision : ι → AliasDecision α) (eligible : σ → ι → Bool) (apply : σ → ι → α → σ)
 (occurrences excluded : List ι) (state : σ) :
 occurrenceSetExecution (fun s event => eligible s event.identity)
   (fun s event value => apply s event.identity value)
   (atomicEvents decision occurrences) excluded state =
 aliasExcludedExecution decision eligible apply occurrences excluded state := by
 induction occurrences generalizing excluded state with
 | nil => rfl
 | cons occurrence rest ih =>
   simp only [atomicEvents,List.map_cons,occurrenceSetExecution,aliasExcludedExecution]
   split
   · exact ih _ _
   · split
     · cases decision occurrence <;> exact ih _ _
     · exact ih _ _

theorem atomic_reference_transport (key : ι → κ) (decision : κ → AliasDecision α)
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (occurrences : List ι) (state : σ) :
 occurrenceReference (fun occurrence => decision (key occurrence))
   (fun s occurrence => eligible s (key occurrence))
   (fun s occurrence value => apply s (key occurrence) value) occurrences state =
 occurrenceReference decision eligible apply (occurrences.map key) state := by
 induction occurrences generalizing state with
 | nil => rfl
 | cons occurrence rest ih =>
   simp only [occurrenceReference,List.map_cons]
   exact ih _

theorem atomic_phase_quotient [DecidableEq ι] [DecidableEq κ]
 (key : ι → κ) (decision : κ → AliasDecision α)
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (occurrences : List ι) (state : σ) :
 occurrenceSetExecution (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value)
   (atomicEvents (fun occurrence => decision (key occurrence)) occurrences) [] state =
 occurrenceSetExecution (fun s event => eligible s event.identity)
   (fun s event value => apply s event.identity value)
   (atomicEvents decision (occurrences.map key)) [] state := by
 rw [atomic_set_execution (fun occurrence => decision (key occurrence))
   (fun s occurrence => eligible s (key occurrence))
   (fun s occurrence value => apply s (key occurrence) value),
   atomic_set_execution decision eligible apply,
   empty_exclusion_refinement,empty_exclusion_refinement]
 exact atomic_reference_transport key decision eligible apply occurrences state

def activeOccurrences (key : ι → κ) (actions : κ → List (AliasDecision α))
 (occurrences : List ι) := occurrences.filter fun occurrence => !(actions (key occurrence)).isEmpty

theorem heads_are_atomic (key : ι → κ) (actions : κ → List (AliasDecision α))
 (occurrences : List ι) :
 headHalfStream (occurrences.map fun occurrence => (occurrence, actions (key occurrence))) =
 atomicEvents (fun occurrence => (actions (key occurrence)).headD .rule)
   (activeOccurrences key actions occurrences) := by
 induction occurrences with
 | nil => rfl
 | cons occurrence rest ih =>
   cases value : actions (key occurrence) with
   | nil => simpa [headHalfStream,blockHalfEvents,atomicEvents,activeOccurrences,value] using ih
   | cons action tail =>
     simpa [headHalfStream,blockHalfEvents,atomicEvents,activeOccurrences,value] using
       congrArg (fun xs => (⟨occurrence,action⟩ : OccurrenceEvent ι α)::xs) ih

theorem active_occurrences_map (key : ι → κ) (actions : κ → List (AliasDecision α))
 (occurrences : List ι) :
 activeOccurrences (fun x => x) actions (occurrences.map key) = (activeOccurrences key actions occurrences).map key := by
 induction occurrences with
 | nil => rfl
 | cons occurrence rest ih =>
   simp only [List.map_cons,activeOccurrences,List.filter_cons]
   cases value : (actions (key occurrence)).isEmpty <;>
     simpa [value,activeOccurrences] using ih

theorem mixed_block_phase_quotient [DecidableEq ι] [DecidableEq κ]
 (key : ι → κ) (actions : κ → List (AliasDecision α))
 (eligible : σ → κ → Bool) (apply : σ → κ → α → σ)
 (disables : ∀ state identity value, eligible (apply state identity value) identity = false)
 (occurrences : List ι) (state : σ) :
 occurrenceSetExecution (fun s event => eligible s (key event.identity))
   (fun s event value => apply s (key event.identity) value)
   (halfStream (occurrences.map fun occurrence => (occurrence,actions (key occurrence)))) [] state =
 occurrenceSetExecution (fun s event => eligible s event.identity)
   (fun s event value => apply s event.identity value)
   (halfStream ((occurrences.map key).map fun identity => (identity,actions identity))) [] state := by
 have left := arbitrary_half_stream_atomic
   (fun s occurrence => eligible s (key occurrence))
   (fun s event value => apply s (key event.identity) value)
   (by intro s event value; exact disables s (key event.identity) value)
   (occurrences.map fun occurrence => (occurrence,actions (key occurrence))) ([],state)
 have right := arbitrary_half_stream_atomic eligible
   (fun s event value => apply s event.identity value)
   (by intro s event value; exact disables s event.identity value)
   ((occurrences.map key).map fun identity => (identity,actions identity)) ([],state)
 have leftProjection := congrArg Prod.snd left
 have rightProjection := congrArg Prod.snd right
 rw [occurrence_state_projection,occurrence_state_projection] at leftProjection rightProjection
 rw [leftProjection,rightProjection,heads_are_atomic,heads_are_atomic,active_occurrences_map]
 exact atomic_phase_quotient key (fun identity => (actions identity).headD .rule)
   eligible apply (activeOccurrences key actions occurrences) state

#print axioms atomic_phase_quotient
#print axioms heads_are_atomic
#print axioms active_occurrences_map
#print axioms mixed_block_phase_quotient
end ShadowOrder
