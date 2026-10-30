import Std

namespace DispatchAttempt

structure State where
  pending : Bool
  attempted : Bool
  inServo : Bool
  inPreTraverse : Bool
  inStyleRefresh : Bool
  attempts : Nat
  rootQueued : Bool
  timingVersion : Nat
  composedVersion : Nat
  deriving DecidableEq, Repr

def canDispatch (s : State) : Bool :=
  !s.inServo && !s.inPreTraverse && !s.inStyleRefresh

def request (s : State) : State :=
  let marked := { s with pending := true }
  if s.attempted || !canDispatch s then marked
  else { marked with attempted := true, attempts := s.attempts + 1 }

def repeatRequests : Nat → State → State
  | 0, s => s
  | n + 1, s => request (repeatRequests n s)

def leaveTraversal (s : State) : State :=
  { s with inServo := false, inPreTraverse := false }

def externalBoundary (s : State) : State :=
  { leaveTraversal s with inStyleRefresh := false }

def consume (s : State) : State :=
  { s with pending := false, attempted := false }

def invalidateAttempt (s : State) : State := { s with attempted := false }

theorem request_preserves_eligibility_and_observations (s : State) :
    (request s).pending = true ∧
    (request s).rootQueued = s.rootQueued ∧
    (request s).timingVersion = s.timingVersion ∧
    (request s).composedVersion = s.composedVersion := by
  simp only [request]
  split <;> simp

theorem blocked_batch_remains_retryable (s : State)
    (unattempted : s.attempted = false) (blocked : canDispatch s = false)
    (n : Nat) :
    repeatRequests (n + 1) s = { s with pending := true } := by
  induction n with
  | zero => simp [repeatRequests, request, unattempted, blocked]
  | succ n ih =>
    simp only [repeatRequests, ih]
    simp [request, canDispatch, unattempted, canDispatch] at blocked ⊢
    simp_all

theorem traversal_exit_is_not_external (s : State)
    (unattempted : s.attempted = false) (refresh : s.inStyleRefresh = true) :
    request (leaveTraversal s) =
      { leaveTraversal s with pending := true } := by
  simp [request, leaveTraversal, canDispatch, unattempted, refresh]

theorem attempted_pending_requests_coalesce (s : State)
    (pending : s.pending = true) (attempted : s.attempted = true) (n : Nat) :
    repeatRequests n s = s := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [repeatRequests, ih, request, attempted]
    cases s
    simp_all

theorem external_retry_makes_exactly_one_attempt (s : State)
    (unattempted : s.attempted = false) (blocked : canDispatch s = false)
    (deferred later : Nat) :
    repeatRequests later
      (request (externalBoundary (repeatRequests (deferred + 1) s))) =
      { externalBoundary s with pending := true, attempted := true,
                                attempts := s.attempts + 1 } := by
  rw [blocked_batch_remains_retryable s unattempted blocked deferred]
  have first : request (externalBoundary { s with pending := true }) =
      { externalBoundary s with pending := true, attempted := true,
                                attempts := s.attempts + 1 } := by
    simp [request, externalBoundary, leaveTraversal, canDispatch, unattempted]
  rw [first]
  exact attempted_pending_requests_coalesce _ rfl rfl later

theorem reset_obligations_are_distinct (s : State) :
    (invalidateAttempt s).pending = s.pending ∧
    (invalidateAttempt s).attempted = false ∧
    (consume s).pending = false ∧ (consume s).attempted = false ∧
    (consume s).rootQueued = s.rootQueued ∧
    (consume s).composedVersion = s.composedVersion := by
  simp [invalidateAttempt, consume]

def deferredWitness : State := ⟨true, false, true, true, true, 0, false, 2, 1⟩
def safeWitness : State := externalBoundary deferredWitness

end DispatchAttempt
