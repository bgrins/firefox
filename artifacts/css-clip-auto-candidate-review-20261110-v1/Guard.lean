import Std

namespace ClipGuardReview

inductive Component (α : Type) where
  | auto
  | length (value : α)
  deriving DecidableEq, Repr

structure Rect (α : Type) where
  top : α
  right : α
  bottom : α
  left : α
  deriving DecidableEq, Repr

structure Computations (α : Type) where
  top : Unit → Option (Component α)
  right : Unit → Option (Component α)
  bottom : Unit → Option (Component α)
  left : Unit → Option (Component α)

def guardComponent : Component α → Option (Component α)
  | .auto => none
  | .length a => some (.length a)

def isAuto : Component α → Bool
  | .auto => true
  | .length _ => false

def anyAuto (r : Rect (Component α)) : Bool :=
  isAuto r.top || isAuto r.right || isAuto r.bottom || isAuto r.left

def rawRect (c : Computations α) : Option (Rect (Component α)) := do
  let top ← c.top ()
  let right ← c.right ()
  let bottom ← c.bottom ()
  let left ← c.left ()
  some ⟨top, right, bottom, left⟩

def oldRect (c : Computations α) : Option (Rect (Component α)) := do
  let top ← (c.top ()).bind guardComponent
  let right ← (c.right ()).bind guardComponent
  let bottom ← (c.bottom ()).bind guardComponent
  let left ← (c.left ()).bind guardComponent
  some ⟨top, right, bottom, left⟩

def guardRect (r : Rect (Component α)) : Option (Rect (Component α)) :=
  if anyAuto r then none else some r

def newRect (c : Computations α) : Option (Rect (Component α)) :=
  (rawRect c).bind guardRect

theorem rectangle_guard_relocation (c : Computations α) : oldRect c = newRect c := by
  cases ht : c.top () with
  | none => simp [oldRect, newRect, rawRect, ht]
  | some top =>
    cases hr : c.right () with
    | none => cases top <;> simp [oldRect, newRect, rawRect, ht, hr, guardComponent]
    | some right =>
      cases hb : c.bottom () with
      | none => cases top <;> cases right <;> simp [oldRect, newRect, rawRect, ht, hr, hb, guardComponent]
      | some bottom =>
        cases hl : c.left () with
        | none => cases top <;> cases right <;> cases bottom <;>
            simp [oldRect, newRect, rawRect, ht, hr, hb, hl, guardComponent]
        | some left => cases top <;> cases right <;> cases bottom <;> cases left <;>
            simp [oldRect, newRect, rawRect, ht, hr, hb, hl, guardComponent, guardRect, anyAuto, isAuto]

inductive Arithmetic where
  | add
  | accumulate (count : Nat)
  deriving DecidableEq, Repr

inductive Value (α β : Type) where
  | rect (value : Rect (Component α))
  | outerAuto
  | nonClip (value : β)
  deriving DecidableEq, Repr

inductive Input (α β : Type) where
  | rect (compute : Arithmetic → Computations α)
  | outerAuto
  | nonClip (compute : Arithmetic → Option β)
  | mismatch

def oldValue (op : Arithmetic) : Input α β → Option (Value α β)
  | .rect compute => (oldRect (compute op)).map .rect
  | .outerAuto => some .outerAuto
  | .nonClip compute => (compute op).map .nonClip
  | .mismatch => none

def rawValue (op : Arithmetic) : Input α β → Option (Value α β)
  | .rect compute => (rawRect (compute op)).map .rect
  | .outerAuto => some .outerAuto
  | .nonClip compute => (compute op).map .nonClip
  | .mismatch => none

def guardValue : Value α β → Option (Value α β)
  | .rect r => (guardRect r).map .rect
  | .outerAuto => some .outerAuto
  | .nonClip b => some (.nonClip b)

def newValue (op : Arithmetic) (input : Input α β) : Option (Value α β) :=
  (rawValue op input).bind guardValue

theorem arithmetic_compatibility (op : Arithmetic) (input : Input α β) :
    oldValue op input = newValue op input := by
  cases input with
  | rect compute =>
    simp only [oldValue, rectangle_guard_relocation, newRect, newValue, rawValue]
    cases rawRect (compute op) <;> rfl
  | outerAuto => rfl
  | nonClip compute => cases h : compute op <;> simp [oldValue, newValue, rawValue, guardValue, h]
  | mismatch => rfl

theorem count_zero_compatibility (input : Input α β) :
    oldValue (.accumulate 0) input = newValue (.accumulate 0) input :=
  arithmetic_compatibility _ _

theorem outer_auto_preserved (op : Arithmetic) :
    newValue op (.outerAuto : Input α β) = some .outerAuto := rfl

theorem nonclip_preserved (op : Arithmetic) (compute : Arithmetic → Option β) :
    newValue op (.nonClip compute : Input α β) = (compute op).map .nonClip := by
  cases h : compute op <;> simp [newValue, rawValue, guardValue, h]

theorem mismatch_preserved (op : Arithmetic) :
    newValue op (.mismatch : Input α β) = none := rfl

def caller (compose : Input α β → Option (Value α β))
    (prepare : σ → σ × Option (Input α β)) (state : σ) : σ × Option (Value α β) :=
  let (updated, input) := prepare state
  (updated, input.bind compose)

theorem preparation_order_preserved (op : Arithmetic)
    (prepare : σ → σ × Option (Input α β)) (state : σ) :
    caller (oldValue op) prepare state = caller (newValue op) prepare state := by
  have same : oldValue (α := α) (β := β) op = newValue op := by
    funext input
    exact arithmetic_compatibility op input
  rw [same]

theorem prepared_state_preserved (compose : Input α β → Option (Value α β))
    (prepare : σ → σ × Option (Input α β)) (state : σ) :
    (caller compose prepare state).1 = (prepare state).1 := rfl

theorem failed_preparation_preserved (compose : Input α β → Option (Value α β))
    (prepare : σ → σ × Option (Input α β)) (state : σ)
    (failed : (prepare state).2 = none) :
    caller compose prepare state = ((prepare state).1, none) := by
  simp [caller, failed]

def allAuto : Computations Nat :=
  ⟨fun _ => some .auto, fun _ => some .auto, fun _ => some .auto, fun _ => some .auto⟩
def numeric : Computations Nat :=
  ⟨fun _ => some (.length 1), fun _ => some (.length 2), fun _ => some (.length 3), fun _ => some (.length 4)⟩
def mixed : Computations Nat := { numeric with top := fun _ => some .auto }
def failedLater : Computations Nat := { mixed with left := fun _ => none }

theorem matching_auto_css_admitted : (rawRect mixed).isSome = true := by decide
theorem matching_auto_smil_rejected : newRect mixed = none := by decide
theorem later_failure_preserved : oldRect failedLater = none ∧ newRect failedLater = none := by decide
theorem numeric_preserved : oldRect numeric = rawRect numeric ∧ newRect numeric = rawRect numeric := by decide
theorem count_zero_auto_rejected :
    newValue (.accumulate 0) (.rect (fun _ => mixed) : Input Nat Nat) = none := by decide

def wrongCountZero (op : Arithmetic) (input : Input Nat Nat) : Option (Value Nat Nat) :=
  match op with
  | .accumulate 0 => rawValue op input
  | _ => newValue op input

end ClipGuardReview
