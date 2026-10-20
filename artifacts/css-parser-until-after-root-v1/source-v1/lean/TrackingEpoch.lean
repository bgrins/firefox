import Std
namespace TrackingEpoch
inductive Event where
  | fresh (relevant : Bool)
  | raw (relevant : Bool)
  | cached
  | reset
  deriving DecidableEq, Repr
structure State where
  cache : Bool
  seen : Bool
  deriving DecidableEq, Repr

def nativeStep (s : State) : Event → State
  | .fresh b => ⟨b, s.seen || b⟩
  | .raw b => ⟨s.cache, s.seen || b⟩
  | .cached | .reset => s

def emitted (cache : Bool) : Event → List Bool
  | .fresh b | .raw b => [b]
  | .cached => [cache]
  | .reset => []
def nextCache (cache : Bool) : Event → Bool
  | .fresh b => b
  | _ => cache
def reference (cache : Bool) : List Event → List Bool
  | [] => []
  | e :: es => emitted cache e ++ reference (nextCache cache e) es

def Inv (s : State) : Prop := s.cache = true → s.seen = true

theorem step_inv (s : State) (e : Event) (h : Inv s) : Inv (nativeStep s e) := by
  cases s with | mk cache seen =>
    cases e <;> cases cache <;> cases seen <;> simp_all [Inv, nativeStep]

theorem cache_step (s : State) (e : Event) :
    (nativeStep s e).cache = nextCache s.cache e := by cases e <;> rfl

theorem step_seen (s : State) (e : Event) (h : Inv s) :
    (nativeStep s e).seen = (s.seen || (emitted s.cache e).any id) := by
  cases s with | mk cache seen =>
    cases e <;> cases cache <;> cases seen <;> simp_all [Inv, nativeStep, emitted]

theorem execution (es : List Event) (s : State) (h : Inv s) :
    (es.foldl nativeStep s).seen = (s.seen || (reference s.cache es).any id) := by
  induction es generalizing s with
  | nil => simp [reference]
  | cons e es ih =>
    rw [List.foldl_cons, ih _ (step_inv s e h)]
    rw [step_seen s e h, cache_step]
    simp [reference, Bool.or_assoc]

theorem cold_epoch (es : List Event) :
    (es.foldl nativeStep ⟨false, false⟩).seen = (reference false es).any id := by
  simpa using execution es ⟨false, false⟩ (by simp [Inv])

def beginEpoch (s : State) : State := { s with seen := false }

theorem colon_entry (es : List Event) (previous : State) :
    (es.foldl nativeStep (beginEpoch (nativeStep previous (.fresh false)))).seen =
      (reference false es).any id := by
  exact cold_epoch es

theorem prefix_inv (es : List Event) (s : State) (h : Inv s) :
    Inv (es.foldl nativeStep s) := by
  induction es generalizing s with
  | nil => exact h
  | cons e es ih => exact ih _ (step_inv s e h)

theorem reset_preserves_seen (s : State) : (nativeStep s .reset).seen = s.seen := rfl

theorem late_enable_counterexample :
    ([Event.cached].foldl nativeStep ⟨true, false⟩).seen = false ∧
    (reference true [Event.cached]).any id = true := by decide

theorem query_then_reenable_counterexample :
    let before := [Event.fresh true].foldl nativeStep ⟨false, false⟩
    let enabledAgain := { before with seen := false }
    ([Event.cached].foldl nativeStep enabledAgain).seen = false ∧
    (reference enabledAgain.cache [Event.cached]).any id = true := by decide

end TrackingEpoch
