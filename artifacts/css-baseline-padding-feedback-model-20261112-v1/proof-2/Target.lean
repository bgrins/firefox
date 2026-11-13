import Lean.Elab.Tactic.Omega

namespace BaselineFeedback

structure State where
  raw : Int
  adjustment : Int
  used : Int
  deriving DecidableEq, Repr

inductive Event where
  | parent (raw adjustment : Int)
  | child
  deriving DecidableEq, Repr

def consistent (s : State) : Prop := s.used = s.raw + s.adjustment

def parent (raw adjustment : Int) : State := ⟨raw, adjustment, raw + adjustment⟩

def step (s : State) : Event → State
  | .parent raw adjustment => parent raw adjustment
  | .child => s

def oldStep (s : State) : Event → State
  | .parent raw adjustment => parent raw adjustment
  | .child => { s with used := s.used + s.adjustment }

def run (s : State) (events : List Event) : State := events.foldl step s

def oldRun (s : State) (events : List Event) : State := events.foldl oldStep s

structure Obligations : Prop where
  parent_consistent : ∀ raw adjustment, consistent (parent raw adjustment)
  step_consistent : ∀ s event, consistent s → consistent (step s event)
  history_consistent : ∀ s events, consistent s → consistent (run s events)
  repeated_child : ∀ s n, run s (List.replicate n .child) = s
  old_repeated_child : ∀ s n,
    (oldRun s (List.replicate n .child)).used = s.used + (n : Int) * s.adjustment
  old_nonzero_drift : ∀ raw adjustment, adjustment ≠ 0 →
    ¬ consistent (oldStep (parent raw adjustment) .child)
  reset_independent : ∀ s t raw adjustment events,
    run s (.parent raw adjustment :: events) = run t (.parent raw adjustment :: events)
  zero_adjustment_control : ∀ raw n,
    oldRun (parent raw 0) (List.replicate n .child) = parent raw 0
  concrete_old_witness : consistent (parent 3 18) ∧
    (oldRun (parent 3 18) [.child, .child]).used = 57 ∧
    ¬ consistent (oldRun (parent 3 18) [.child, .child])
  concrete_fixed_witness :
    (run (parent 3 18) [.child, .child]).used = 21 ∧
    (run (parent 3 18) [.child, .parent 4 8, .child]).used = 12

end BaselineFeedback
