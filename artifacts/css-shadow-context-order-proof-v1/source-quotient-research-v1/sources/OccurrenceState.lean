import HalfBlockAtomic
namespace ShadowOrder

def occurrenceStateStep [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (state : List κ × σ) (event : OccurrenceEvent κ α) : List κ × σ :=
 if event.identity ∈ state.1 then state
 else if eligible state.2 event.identity then
   match event.action with
   | .rule => (event.identity::state.1,state.2)
   | .effect value => (state.1,apply state.2 event value)
 else state

def occurrenceStateExecution [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (events : List (OccurrenceEvent κ α)) (state : List κ × σ) : List κ × σ :=
 events.foldl (occurrenceStateStep eligible apply) state

theorem occurrence_state_projection [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (events : List (OccurrenceEvent κ α)) (state : List κ × σ) :
 (occurrenceStateExecution eligible apply events state).2 =
 occurrenceSetExecution (fun s e => eligible s e.identity) apply events state.1 state.2 := by
 induction events generalizing state with
 | nil => rfl
 | cons event rest ih =>
   simp only [occurrenceStateExecution,List.foldl_cons]
   rw [← occurrenceStateExecution,ih]
   simp only [occurrenceStateStep,occurrenceSetExecution]
   split
   · rfl
   · split
     · cases event.action <;> rfl
     · rfl

theorem occurrence_state_append [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (first rest : List (OccurrenceEvent κ α)) (state : List κ × σ) :
 occurrenceStateExecution eligible apply (first ++ rest) state =
 occurrenceStateExecution eligible apply rest
   (occurrenceStateExecution eligible apply first state) := by
 exact List.foldl_append

theorem uniform_key_state_skipped [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (events : List (OccurrenceEvent κ α)) (key : κ) (state : List κ × σ)
 (uniform : ∀ event ∈ events, event.identity = key)
 (blocked : key ∈ state.1 ∨ eligible state.2 key = false) :
 occurrenceStateExecution eligible apply events state = state := by
 induction events with
 | nil => rfl
 | cons event rest ih =>
   have identity := uniform event (by simp)
   have tail := ih (fun e he => uniform e (by simp [he]))
   have step : occurrenceStateStep eligible apply state event = state := by
     rcases blocked with banned | disabled
     · simp [occurrenceStateStep,identity,banned]
     · simp [occurrenceStateStep,identity,disabled]
   simpa only [occurrenceStateExecution,List.foldl_cons,step] using tail

theorem mixed_half_state_first_effect [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (disables : ∀ state event value, eligible (apply state event value) event.identity = false)
 (first : OccurrenceEvent κ α) (rest : List (OccurrenceEvent κ α))
 (uniform : ∀ event ∈ rest, event.identity = first.identity) (state : List κ × σ) :
 occurrenceStateExecution eligible apply (first::rest) state =
 occurrenceStateExecution eligible apply [first] state := by
 have blocked : first.identity ∈ (occurrenceStateStep eligible apply state first).1 ∨
   eligible (occurrenceStateStep eligible apply state first).2 first.identity = false := by
   by_cases banned : first.identity ∈ state.1
   · simp [occurrenceStateStep,banned]
   · cases enabled : eligible state.2 first.identity with
     | false => simp [occurrenceStateStep,banned,enabled]
     | true =>
       cases action : first.action with
       | rule => simp [occurrenceStateStep,banned,enabled,action]
       | effect value => simp [occurrenceStateStep,banned,enabled,action,disables]
 have skipped := uniform_key_state_skipped eligible apply rest first.identity
   (occurrenceStateStep eligible apply state first) uniform blocked
 simpa only [occurrenceStateExecution,List.foldl_cons,List.foldl_nil] using skipped

theorem half_first_effect_in_context [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (disables : ∀ state event value, eligible (apply state event value) event.identity = false)
 (first : OccurrenceEvent κ α) (rest before after : List (OccurrenceEvent κ α))
 (uniform : ∀ event ∈ rest, event.identity = first.identity) (state : List κ × σ) :
 occurrenceStateExecution eligible apply (before ++ (first::rest) ++ after) state =
 occurrenceStateExecution eligible apply (before ++ [first] ++ after) state := by
 simp only [occurrence_state_append]
 rw [mixed_half_state_first_effect eligible apply disables first rest uniform]

def halfStream (halves : List (κ × List (AliasDecision α))) : List (OccurrenceEvent κ α) :=
 halves.flatMap fun half => blockHalfEvents half.1 half.2

def headHalfStream (halves : List (κ × List (AliasDecision α))) : List (OccurrenceEvent κ α) :=
 halves.flatMap fun half => blockHalfEvents half.1 (half.2.take 1)

theorem block_half_state_atomic [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (disables : ∀ state event value, eligible (apply state event value) event.identity = false)
 (key : κ) (actions : List (AliasDecision α)) (state : List κ × σ) :
 occurrenceStateExecution eligible apply (blockHalfEvents key actions) state =
 occurrenceStateExecution eligible apply (blockHalfEvents key (actions.take 1)) state := by
 cases actions with
 | nil => rfl
 | cons action rest =>
   simp only [List.take_succ_cons,List.take_zero,blockHalfEvents,List.map_cons,List.map_nil]
   apply mixed_half_state_first_effect eligible apply disables
   intro event member
   rcases List.mem_map.mp member with ⟨a,ha,rfl⟩
   rfl

theorem arbitrary_half_stream_atomic [DecidableEq κ] (eligible : σ → κ → Bool)
 (apply : σ → OccurrenceEvent κ α → α → σ)
 (disables : ∀ state event value, eligible (apply state event value) event.identity = false)
 (halves : List (κ × List (AliasDecision α))) (state : List κ × σ) :
 occurrenceStateExecution eligible apply (halfStream halves) state =
 occurrenceStateExecution eligible apply (headHalfStream halves) state := by
 induction halves generalizing state with
 | nil => rfl
 | cons half rest ih =>
   simp only [halfStream,headHalfStream,List.flatMap_cons,occurrence_state_append]
   rw [block_half_state_atomic eligible apply disables]
   exact ih _

#print axioms half_first_effect_in_context
#print axioms arbitrary_half_stream_atomic
end ShadowOrder
