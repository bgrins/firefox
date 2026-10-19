import OccurrenceState
namespace ShadowOrder

def occurrenceBlocked [DecidableEq κ] (eligible : σ → κ → Bool)
 (state : List κ × σ) (key : κ) : Prop :=
 key ∈ state.1 ∨ eligible state.2 key = false

theorem step_preserves_blocked [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (monotone : ∀ state event value key,
   eligible state key = false → eligible (apply state event value) key = false)
 (state : List κ × σ) (event : OccurrenceEvent κ α) (key : κ)
 (blocked : occurrenceBlocked eligible state key) :
 occurrenceBlocked eligible (occurrenceStateStep eligible apply state event) key := by
 unfold occurrenceStateStep
 split
 · exact blocked
 · split
   · cases event.action with
     | rule =>
       rcases blocked with banned | disabled
       · exact Or.inl (by simp [banned])
       · exact Or.inr disabled
     | effect value =>
       rcases blocked with banned | disabled
       · exact Or.inl banned
       · exact Or.inr (monotone state.2 event value key disabled)
   · exact blocked

theorem execution_preserves_blocked [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (monotone : ∀ state event value key,
   eligible state key = false → eligible (apply state event value) key = false)
 (events : List (OccurrenceEvent κ α)) (state : List κ × σ) (key : κ)
 (blocked : occurrenceBlocked eligible state key) :
 occurrenceBlocked eligible (occurrenceStateExecution eligible apply events state) key := by
 induction events generalizing state with
 | nil => exact blocked
 | cons event rest ih =>
   exact ih _ (step_preserves_blocked eligible apply monotone state event key blocked)

theorem rule_step_blocks [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ) (state : List κ × σ)
 (event : OccurrenceEvent κ α) (rule : event.action = .rule) :
 occurrenceBlocked eligible (occurrenceStateStep eligible apply state event) event.identity := by
 unfold occurrenceStateStep
 split
 · exact Or.inl (by assumption)
 · split
   · simp [rule,occurrenceBlocked]
   · exact Or.inr (by simpa using ‹¬eligible state.2 event.identity = true›)

theorem encountered_rule_blocks [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (monotone : ∀ state event value key,
   eligible state key = false → eligible (apply state event value) key = false)
 (events : List (OccurrenceEvent κ α)) (state : List κ × σ)
 (event : OccurrenceEvent κ α) (member : event ∈ events) (rule : event.action = .rule) :
 occurrenceBlocked eligible (occurrenceStateExecution eligible apply events state) event.identity := by
 induction events generalizing state with
 | nil => simp at member
 | cons first rest ih =>
   rcases List.mem_cons.mp member with same | later
   · subst first
     exact execution_preserves_blocked eligible apply monotone rest _ event.identity
       (rule_step_blocks eligible apply state event rule)
   · exact ih _ later

theorem covered_normal_occurrence_blocked [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (monotone : ∀ state event value key,
   eligible state key = false → eligible (apply state event value) key = false)
 (important normal : List (OccurrenceEvent κ α)) (state : List κ × σ)
 (coverage : ∀ event ∈ normal, ∃ earlier ∈ important,
   earlier.identity = event.identity ∧ earlier.action = .rule) :
 ∀ event ∈ normal,
 occurrenceBlocked eligible (occurrenceStateExecution eligible apply important state) event.identity := by
 intro event member
 rcases coverage event member with ⟨earlier,present,same,rule⟩
 rw [← same]
 exact encountered_rule_blocks eligible apply monotone important state earlier present rule

#print axioms covered_normal_occurrence_blocked
end ShadowOrder
