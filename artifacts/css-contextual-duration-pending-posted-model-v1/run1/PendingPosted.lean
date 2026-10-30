import Std

namespace PendingPosted

structure State where
  pending : Bool
  posted : Bool
  insideServo : Bool
  appliedGeneration : Nat
  composedGeneration : Nat
  deriving DecidableEq, Repr

def requestLayer (s : State) : State :=
  { s with pending := true
           posted := s.posted || (!s.pending && !s.insideServo) }

def changeTiming (s : State) : State :=
  requestLayer { s with appliedGeneration := s.appliedGeneration + 1 }

def exitWithoutDrain (s : State) : State := { s with insideServo := false }

def externalRestyle (s : State) : State := { s with posted := true }

def service (s : State) : State :=
  if s.posted && !s.insideServo then
    { s with pending := false, posted := false,
             composedGeneration := s.appliedGeneration }
  else s

def Stalled (s : State) : Prop :=
  s.pending = true ∧ s.posted = false ∧ s.insideServo = false

def step (s : State) : State := service (changeTiming s)

def repeatRequests : Nat → State → State
  | 0, s => s
  | n + 1, s => step (repeatRequests n s)

theorem inside_request_does_not_post (s : State)
    (inside : s.insideServo = true) (unposted : s.posted = false) :
    (changeTiming s).pending = true ∧ (changeTiming s).posted = false := by
  simp [changeTiming, requestLayer, inside, unposted]

theorem final_exit_premise_creates_stalled (s : State)
    (inside : s.insideServo = true) (unposted : s.posted = false) :
    Stalled (exitWithoutDrain (changeTiming s)) := by
  simp [Stalled, exitWithoutDrain, changeTiming, requestLayer, inside, unposted]

theorem stalled_request_coalesces (s : State) (h : Stalled s) :
    step s = { s with appliedGeneration := s.appliedGeneration + 1 } := by
  rcases h with ⟨pending, posted, inside⟩
  cases s
  simp_all [step, service, changeTiming, requestLayer]

theorem arbitrary_requests_remain_unposted (s : State) (h : Stalled s) (n : Nat) :
    repeatRequests n s =
      { s with appliedGeneration := s.appliedGeneration + n } := by
  induction n with
  | zero => simp [repeatRequests]
  | succ n ih =>
    rw [repeatRequests, ih]
    rw [stalled_request_coalesces _ (by simpa [Stalled] using h)]
    simp [Nat.add_assoc]

theorem no_composition_after_arbitrary_requests (s : State) (h : Stalled s)
    (stale : s.composedGeneration < s.appliedGeneration) (n : Nat) :
    Stalled (repeatRequests n s) ∧
    (repeatRequests n s).composedGeneration <
      (repeatRequests n s).appliedGeneration := by
  rw [arbitrary_requests_remain_unposted s h n]
  constructor
  · simpa [Stalled] using h
  · simp only
    omega

theorem external_restyle_can_recompose (s : State) (h : Stalled s) (n : Nat) :
    let result := service (externalRestyle (repeatRequests n s))
    result.composedGeneration = s.appliedGeneration + n ∧
    result.appliedGeneration = s.appliedGeneration + n ∧
    result.pending = false ∧ result.posted = false := by
  rw [arbitrary_requests_remain_unposted s h n]
  rcases h with ⟨_, _, inside⟩
  simp [service, externalRestyle, inside]

theorem fresh_outside_request_does_post (s : State)
    (notPending : s.pending = false) (outside : s.insideServo = false) :
    (changeTiming s).posted = true := by
  simp [changeTiming, requestLayer, notPending, outside]

def witness : State := ⟨true, false, false, 2, 1⟩

end PendingPosted
