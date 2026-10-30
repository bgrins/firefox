namespace DurationScheduling

inductive Owner where
  | css | script
  deriving DecidableEq, Repr

inductive Traversal where
  | normal | animation
  deriving DecidableEq, Repr

structure State where
  computed : Nat
  applied : Nat
  owner : Owner
  deriving DecidableEq, Repr

structure Event where
  traversal : Traversal
  computed : Nat
  deriving DecidableEq, Repr

def commit (s : State) (e : Event) (dispatch : Bool) : State :=
  { computed := e.computed
    applied := if dispatch && s.owner == .css then e.computed else s.applied
    owner := s.owner }

def equalityStep (s : State) (e : Event) : State :=
  commit s e (e.traversal == .normal && s.computed != e.computed)

def scopedStep (s : State) (e : Event) : State :=
  commit s e (s.computed != e.computed)

def skipStep (s : State) (e : Event) : State := commit s e false

def overwriteStep (s : State) (e : Event) : State :=
  { computed := e.computed, applied := e.computed, owner := s.owner }

def Synced (s : State) : Prop := s.owner = .css → s.applied = s.computed

def trace (step : State → Event → State) (s : State) : List Event → List State
  | [] => [s]
  | e :: es => s :: trace step (step s e) es

def cssStart : State := ⟨1000, 1000, .css⟩
def scriptStart : State := ⟨1000, 1250, .script⟩
def fourSamples : List Event :=
  [⟨.animation, 1000⟩, ⟨.animation, 1500⟩,
   ⟨.animation, 1000⟩, ⟨.animation, 1500⟩]
def withDiagnostic : List Event := fourSamples ++ [⟨.normal, 1500⟩]
def timingPair (s : State) : Nat × Nat := (s.computed, s.applied)
def progressRatio (s : State) : Nat × Nat := (750, s.applied)

theorem equality_misses_committed_stale (s : State) :
    equalityStep s ⟨.normal, s.computed⟩ = s := by
  cases s
  simp [equalityStep, commit]

theorem skipped_change_survives_normal (old fresh : Nat) (h : old ≠ fresh) :
    let s := equalityStep ⟨old, old, .css⟩ ⟨.animation, fresh⟩
    let after := equalityStep s ⟨.normal, fresh⟩
    after.computed = fresh ∧ after.applied = old ∧ ¬ Synced after := by
  simp [equalityStep, commit, Synced, h]

theorem scoped_sync_and_script_preservation (s : State) (e : Event) (initial : Synced s) :
    Synced (scopedStep s e) ∧
    (scopedStep s e).owner = s.owner ∧
    (s.owner = .script → (scopedStep s e).applied = s.applied) := by
  cases h : s.owner <;> simp_all [scopedStep, commit, Synced]

theorem scoped_fixed_input_idempotent (s : State) (e : Event) :
    scopedStep (scopedStep s e) e = scopedStep s e := by
  cases s with
  | mk computed applied owner =>
    cases owner <;> simp [scopedStep, commit]
  
theorem scoped_history (s : State) (events : List Event) (h : Synced s) :
    ∀ state ∈ trace scopedStep s events, Synced state := by
  induction events generalizing s with
  | nil => simpa [trace] using h
  | cons event events ih =>
    intro state member
    simp only [trace, List.mem_cons] at member
    rcases member with rfl | member
    · exact h
    · exact ih (scopedStep s event)
        (scoped_sync_and_script_preservation s event h).1 state member

theorem observed_six_state_trace :
    (trace equalityStep cssStart withDiagnostic).map timingPair =
      [(1000, 1000), (1000, 1000), (1500, 1000),
       (1000, 1000), (1500, 1000), (1500, 1000)] ∧
    (trace equalityStep cssStart withDiagnostic).map progressRatio =
      List.replicate 6 (750, 1000) := by decide

theorem scoped_four_sample_and_override_traces :
    (trace scopedStep cssStart fourSamples).tail.map timingPair =
      [(1000, 1000), (1500, 1500), (1000, 1000), (1500, 1500)] ∧
    (trace scopedStep scriptStart withDiagnostic).map timingPair =
      [(1000, 1250), (1000, 1250), (1500, 1250),
       (1000, 1250), (1500, 1250), (1500, 1250)] ∧
    (trace equalityStep scriptStart withDiagnostic).map progressRatio =
      List.replicate 6 (750, 1250) := by decide

end DurationScheduling
