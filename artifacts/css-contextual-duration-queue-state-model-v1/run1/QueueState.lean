import DispatchAttempt

namespace QueueState

inductive Entry where
  | absent | throttled | pending | attempted
  deriving DecidableEq, Repr

inductive Kind where
  | throttled | standard | layer
  deriving DecidableEq, Repr

structure Context where
  presContext : Bool
  contentShell : Bool
  target : Bool
  servo : Bool
  preTraverse : Bool
  styleRefresh : Bool
  deriving DecidableEq, Repr

structure Result where
  entry : Entry
  postCalled : Bool := false
  attempt : Bool := false
  throttledFlush : Bool := false
  layerGeneration : Bool := false
  deriving DecidableEq, Repr

def outside (c : Context) : Bool :=
  !c.servo && !c.preTraverse && !c.styleRefresh

def admitted (c : Context) : Bool := c.presContext && c.contentShell

def insert (e : Entry) : Entry := if e == .absent then .throttled else e

def post (e : Entry) (c : Context) : Result :=
  if c.presContext && c.target && outside c then
    ⟨if e == .absent then .absent else .attempted, true, true, false, false⟩
  else ⟨e, true, false, false, false⟩

def request (e : Entry) (k : Kind) (c : Context) : Result :=
  if !admitted c then ⟨e⟩ else
  let previous := insert e
  let marked := if k != .throttled && previous == .throttled then .pending else previous
  let result :=
    if k == .throttled then { Result.mk marked with throttledFlush := true }
    else if previous != .attempted && (previous == .throttled || outside c) then
      post marked c
    else ⟨marked⟩
  { result with layerGeneration := k == .layer }

def forced (e : Entry) (c : Context) : Result :=
  if e == .throttled then post .pending c else ⟨e⟩

def projection : Entry → Option Bool
  | .absent => none
  | .throttled => some false
  | .pending | .attempted => some true

def oldRequest (e : Option Bool) (k : Kind) (c : Context) : Option Bool :=
  if !admitted c then e
  else if k == .throttled then some (e.getD false) else some true

def oldForced (e : Option Bool) : Option Bool :=
  match e with
  | some false => some true
  | other => other

def eligible (e : Entry) (flush : Bool) : Bool :=
  e != .absent && (flush || e != .throttled)

def oldEligible (e : Option Bool) (flush : Bool) : Bool :=
  match e with
  | none => false
  | some bit => flush || bit

def safe : Context := ⟨true, true, true, false, false, false⟩
def blocked : Context := { safe with servo := true }

theorem request_bool_projection (e : Entry) (k : Kind) (c : Context) :
    projection (request e k c).entry = oldRequest (projection e) k c := by
  cases e <;> cases k <;> cases c with
  | mk a b t s p r =>
    cases a <;> cases b <;> cases t <;> cases s <;> cases p <;> cases r <;> decide

theorem forced_bool_projection (e : Entry) (c : Context) :
    projection (forced e c).entry = oldForced (projection e) := by
  cases e <;> cases c with
  | mk a b t s p r =>
    cases a <;> cases b <;> cases t <;> cases s <;> cases p <;> cases r <;> decide

theorem eligibility_projection (e : Entry) (flush : Bool) :
    eligible e flush = oldEligible (projection e) flush := by
  cases e <;> cases flush <;> decide

theorem throttled_request_never_posts (e : Entry) (c : Context) :
    (request e .throttled c).postCalled = false ∧
    (request e .throttled c).attempt = false ∧
    (request e .throttled c).throttledFlush = admitted c ∧
    (request e .throttled c).layerGeneration = false := by
  cases e <;> cases c with
  | mk a b t s p r =>
    cases a <;> cases b <;> cases t <;> cases s <;> cases p <;> cases r <;> decide

theorem forced_skips_non_throttled (c : Context) :
    forced .absent c = ⟨.absent⟩ ∧
    forced .pending c = ⟨.pending⟩ ∧
    forced .attempted c = ⟨.attempted⟩ := by
  simp [forced]

theorem blocked_forced_retains_eligibility (c : Context)
    (blockedContext : outside c = false) :
    forced .throttled c = ⟨.pending, true, false, false, false⟩ ∧
    eligible (forced .throttled c).entry false = true ∧
    forced (forced .throttled c).entry c = ⟨.pending⟩ := by
  simp [forced, post, blockedContext, eligible]

theorem safe_forced_attempt_then_skip :
    forced .throttled safe = ⟨.attempted, true, true, false, false⟩ ∧
    forced (forced .throttled safe).entry safe = ⟨.attempted⟩ := by decide

theorem direct_post_does_not_insert (c : Context) :
    (post .absent c).entry = .absent := by
  simp only [post]
  split <;> rfl

theorem layer_generation_is_not_dispatch (e : Entry) (c : Context) :
    (request e .layer c).layerGeneration = admitted c ∧
    (request .attempted .layer c).attempt = false := by
  cases e <;> cases c with
  | mk a b t s p r =>
    cases a <;> cases b <;> cases t <;> cases s <;> cases p <;> cases r <;> decide

def priorState (attempted : Bool) (s p r : Bool) : DispatchAttempt.State :=
  ⟨true, attempted, s, p, r, 0, false, 0, 0⟩

def fromAttempt (a : Bool) : Entry := if a then .attempted else .pending

theorem pending_protocol_join (a s p r : Bool) :
    let c : Context := ⟨true, true, true, s, p, r⟩
    let old := priorState a s p r
    (request (fromAttempt a) .standard c).entry =
      fromAttempt (DispatchAttempt.request old).attempted ∧
    ((request (fromAttempt a) .standard c).attempt = true ↔
      (DispatchAttempt.request old).attempts = 1) := by
  cases a <;> cases s <;> cases p <;> cases r <;> decide

def consume (_ : Entry) : Entry := .absent

theorem consume_clears_presence (e : Entry) (flush : Bool) :
    projection (consume e) = none ∧ eligible (consume e) flush = false := by
  simp [consume, projection, eligible]

end QueueState
