import AliasEquivalence
namespace ShadowOrder
structure OccurrenceEvent (κ α : Type) where
 identity : κ
 action : AliasDecision α

def remaining [DecidableEq κ] (excluded : List κ) (events : List (OccurrenceEvent κ α)) :=
 events.filter fun event => decide (event.identity ∉ excluded)

def occurrenceSetExecution [DecidableEq κ]
 (enabled : σ → OccurrenceEvent κ α → Bool) (apply : σ → OccurrenceEvent κ α → α → σ) :
 List (OccurrenceEvent κ α) → List κ → σ → σ
 | [], _, state => state
 | event::rest, excluded, state =>
   if event.identity ∈ excluded then occurrenceSetExecution enabled apply rest excluded state
   else if enabled state event then
     match event.action with
     | .rule => occurrenceSetExecution enabled apply rest (event.identity::excluded) state
     | .effect value => occurrenceSetExecution enabled apply rest excluded (apply state event value)
   else occurrenceSetExecution enabled apply rest excluded state

def occurrenceDeletionReference [DecidableEq κ]
 (enabled : σ → OccurrenceEvent κ α → Bool) (apply : σ → OccurrenceEvent κ α → α → σ)
 (events : List (OccurrenceEvent κ α)) (state : σ) : σ :=
 match events with
 | [] => state
 | event::rest =>
   if enabled state event then
     match event.action with
     | .rule => occurrenceDeletionReference enabled apply (remaining [event.identity] rest) state
     | .effect value => occurrenceDeletionReference enabled apply rest (apply state event value)
   else occurrenceDeletionReference enabled apply rest state
termination_by events.length
decreasing_by
 all_goals simp_wf
 · exact Nat.lt_succ_of_le (List.length_filter_le _ _)

theorem remaining_cons [DecidableEq κ] (key : κ) (excluded : List κ)
 (events : List (OccurrenceEvent κ α)) :
 remaining [key] (remaining excluded events) = remaining (key::excluded) events := by
 simp only [remaining,List.filter_filter]
 congr 1
 funext event
 simp only [List.mem_cons]
 by_cases a : event.identity = key <;> by_cases b : event.identity ∈ excluded <;> simp [a,b]

theorem arbitrary_occurrence_deletion [DecidableEq κ]
 (enabled : σ → OccurrenceEvent κ α → Bool) (apply : σ → OccurrenceEvent κ α → α → σ)
 (events : List (OccurrenceEvent κ α)) (excluded : List κ) (state : σ) :
 occurrenceSetExecution enabled apply events excluded state =
 occurrenceDeletionReference enabled apply (remaining excluded events) state := by
 induction events generalizing excluded state with
 | nil => simp [occurrenceSetExecution,remaining,occurrenceDeletionReference]
 | cons event rest ih =>
   by_cases banned : event.identity ∈ excluded
   · simp [occurrenceSetExecution,remaining,banned,ih]
   · simp only [occurrenceSetExecution,banned,↓reduceIte]
     have remain : remaining excluded (event::rest) = event::remaining excluded rest := by
       simp [remaining,banned]
     rw [remain,occurrenceDeletionReference]
     cases allow : enabled state event
     · simp [ih]
     · simp only [↓reduceIte]
       cases action : event.action with
       | rule => rw [remaining_cons]; exact ih _ _
       | effect value => simp [ih]

theorem fresh_occurrence_deletion [DecidableEq κ]
 (enabled : σ → OccurrenceEvent κ α → Bool) (apply : σ → OccurrenceEvent κ α → α → σ)
 (events : List (OccurrenceEvent κ α)) (state : σ) :
 occurrenceSetExecution enabled apply events [] state =
 occurrenceDeletionReference enabled apply events state := by
 have empty : remaining ([] : List κ) events = events := by
   apply List.filter_eq_self.mpr
   intro event member
   simp
 have result := arbitrary_occurrence_deletion enabled apply events [] state
 rw [empty] at result
 exact result

#print axioms arbitrary_occurrence_deletion
#print axioms fresh_occurrence_deletion
end ShadowOrder
