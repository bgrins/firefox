import GroupedQuotient
namespace ShadowOrder
variable {σ : Type}

theorem blocked_event_step [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ) (state : List κ × σ)
 (event : OccurrenceEvent κ α) (blocked : occurrenceBlocked eligible state event.identity) :
 occurrenceStateStep eligible apply state event = state := by
 rcases blocked with banned | disabled
 · simp [occurrenceStateStep,banned]
 · simp [occurrenceStateStep,disabled]

theorem prune_blocked_events [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (monotone : ∀ state event value key,
   eligible state key = false → eligible (apply state event value) key = false)
 (keep : κ → Bool) (events : List (OccurrenceEvent κ α)) (state : List κ × σ)
 (blocked : ∀ event ∈ events, keep event.identity = false →
   occurrenceBlocked eligible state event.identity) :
 occurrenceStateExecution eligible apply events state =
 occurrenceStateExecution eligible apply (events.filter fun event => keep event.identity) state := by
 induction events generalizing state with
 | nil => rfl
 | cons event rest ih =>
   cases kept : keep event.identity with
   | false =>
     have step := blocked_event_step eligible apply state event (blocked event (by simp) kept)
     simpa only [occurrenceStateExecution,List.foldl_cons,step,List.filter_cons,kept,
       Bool.false_eq_true,↓reduceIte] using
       ih state (fun other member rejected => blocked other (by simp [member]) rejected)
   | true =>
     have next : ∀ other ∈ rest, keep other.identity = false →
       occurrenceBlocked eligible (occurrenceStateStep eligible apply state event) other.identity := by
       intro other member rejected
       exact step_preserves_blocked eligible apply monotone state event other.identity
         (blocked other (by simp [member]) rejected)
     simpa only [occurrenceStateExecution,List.foldl_cons,List.filter_cons,kept,↓reduceIte]
       using ih _ next

theorem exclusion_membership_local [DecidableEq κ]
 (enabled : σ → OccurrenceEvent κ α → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (events : List (OccurrenceEvent κ α)) (left right : List κ) (state : σ)
 (same : ∀ event ∈ events, event.identity ∈ left ↔ event.identity ∈ right) :
 occurrenceSetExecution enabled apply events left state =
 occurrenceSetExecution enabled apply events right state := by
 induction events generalizing left right state with
 | nil => rfl
 | cons event rest ih =>
   have first := same event (by simp)
   have tail := fun other member => same other (List.mem_cons_of_mem event member)
   simp only [occurrenceSetExecution]
   by_cases banned : event.identity ∈ left
   · simp only [banned,first.mp banned,↓reduceIte]
     exact ih _ _ _ tail
   · have other : event.identity ∉ right := fun h => banned (first.mpr h)
     simp only [banned,other,↓reduceIte]
     cases allow : enabled state event with
     | false => simp only [Bool.false_eq_true,↓reduceIte]; exact ih _ _ _ tail
     | true =>
       simp only [↓reduceIte]
       cases event.action with
       | rule =>
         apply ih
         intro next member
         simp only [List.mem_cons]
         exact or_congr Iff.rfl (tail next member)
       | effect value => exact ih _ _ _ tail

theorem fresh_exclusion_origin [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (events : List (OccurrenceEvent κ α)) (state : List κ × σ)
 (key : κ) (present : key ∈ (occurrenceStateExecution eligible apply events state).1) :
 key ∈ state.1 ∨ ∃ event ∈ events, event.identity = key ∧ event.action = .rule := by
 induction events generalizing state with
 | nil => exact Or.inl present
 | cons event rest ih =>
   have result := ih (occurrenceStateStep eligible apply state event) present
   rcases result with earlier | ⟨later,member,identity,rule⟩
   · unfold occurrenceStateStep at earlier
     split at earlier
     · exact Or.inl earlier
     · split at earlier
       · cases action : event.action with
         | rule =>
           simp only [action,List.mem_cons] at earlier
           rcases earlier with same | old
           · exact Or.inr ⟨event,by simp,same.symm,action⟩
           · exact Or.inl old
         | effect value => exact Or.inl (by simpa only [action] using earlier)
       · exact Or.inl earlier
   · exact Or.inr ⟨later,by simp [member],identity,rule⟩

#print axioms prune_blocked_events
#print axioms exclusion_membership_local
#print axioms fresh_exclusion_origin
end ShadowOrder
