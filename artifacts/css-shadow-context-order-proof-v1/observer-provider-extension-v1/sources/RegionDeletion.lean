import Std
namespace ShadowOrder
inductive RegionAction (κ α : Type) where
 | rollback (constraint : κ)
 | terminal (value : α)
 | skip

def regionReference (action : ε → RegionAction κ α) (region : κ → ε → Bool)
 (events : List ε) : Option α :=
 match events with
 | [] => none
 | event::rest =>
   match action event with
   | .rollback constraint => regionReference action region (rest.filter (region constraint))
   | .terminal value => some value
   | .skip => regionReference action region rest
termination_by events.length
decreasing_by
 all_goals simp_wf
 · exact Nat.lt_succ_of_le (List.length_filter_le _ _)

def summarizedControl (action : ε → RegionAction κ α)
 (allowed : σ → ε → Bool) (add : σ → κ → σ) : List ε → σ → Option α
 | [], _ => none
 | event::rest, state =>
   if allowed state event then
     match action event with
     | .rollback constraint => summarizedControl action allowed add rest (add state constraint)
     | .terminal value => some value
     | .skip => summarizedControl action allowed add rest state
   else summarizedControl action allowed add rest state

theorem summarized_region_filter (allowed : σ → ε → Bool) (add : σ → κ → σ)
 (region : κ → ε → Bool)
 (intersection : ∀ state constraint event,
   allowed (add state constraint) event = (allowed state event && region constraint event))
 (state : σ) (constraint : κ) (events : List ε) :
 (events.filter (allowed state)).filter (region constraint) =
 events.filter (allowed (add state constraint)) := by
 rw [List.filter_filter]
 congr 1
 funext event
 simpa [Bool.and_comm] using (intersection state constraint event).symm

theorem arbitrary_region_deletion (action : ε → RegionAction κ α)
 (allowed : σ → ε → Bool) (add : σ → κ → σ) (region : κ → ε → Bool)
 (intersection : ∀ state constraint event,
   allowed (add state constraint) event = (allowed state event && region constraint event))
 (events : List ε) (state : σ) :
 summarizedControl action allowed add events state =
 regionReference action region (events.filter (allowed state)) := by
 induction events generalizing state with
 | nil => simp [summarizedControl,regionReference]
 | cons event rest ih =>
   cases acceptance : allowed state event
   · simp [summarizedControl,acceptance,ih]
   · simp only [summarizedControl,acceptance,↓reduceIte,List.filter_cons,↓reduceIte]
     rw [regionReference]
     cases classification : action event with
     | terminal value => rfl
     | skip => exact ih state
     | rollback constraint =>
       change summarizedControl action allowed add rest (add state constraint) =
         regionReference action region ((rest.filter (allowed state)).filter (region constraint))
       rw [summarized_region_filter allowed add region intersection]
       exact ih (add state constraint)

#print axioms arbitrary_region_deletion
end ShadowOrder
