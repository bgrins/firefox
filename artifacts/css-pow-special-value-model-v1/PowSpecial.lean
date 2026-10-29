import Std

namespace CssPowSpecial

inductive Value where
  | nan
  | infinity (negative : Bool)
  | unit (negative : Bool)
  | finite (token : Nat)
  deriving DecidableEq, Repr

def isNaN : Value → Bool
  | .nan => true
  | _ => false

def isInfinite : Value → Bool
  | .infinity _ => true
  | _ => false

def isUnit : Value → Bool
  | .unit _ => true
  | _ => false

def spec (fallback : Value → Value → Value) : Value → Value → Value
  | .nan, _ => .nan
  | _, .nan => .nan
  | .unit _, .infinity _ => .nan
  | a, b => fallback a b

def guarded (fallback : Value → Value → Value) (a b : Value) : Value :=
  if isNaN a || isNaN b || (isUnit a && isInfinite b) then .nan
  else fallback a b

theorem guard_refines_spec (fallback : Value → Value → Value) (a b : Value) :
    guarded fallback a b = spec fallback a b := by
  cases a <;> cases b <;> rfl

theorem nan_left (fallback : Value → Value → Value) (b : Value) :
    guarded fallback .nan b = .nan := by
  rfl

theorem nan_right (fallback : Value → Value → Value) (a : Value) :
    guarded fallback a .nan = .nan := by
  cases a <;> rfl

theorem unit_infinite (fallback : Value → Value → Value) (s t : Bool) :
    guarded fallback (.unit s) (.infinity t) = .nan := by
  rfl

theorem fallback_preserved (fallback : Value → Value → Value) (a b : Value)
    (ha : isNaN a = false) (hb : isNaN b = false)
    (h : (isUnit a && isInfinite b) = false) :
    guarded fallback a b = fallback a b := by
  simp [guarded, ha, hb, h]

inductive Expr where
  | literal (value : Value)
  | variable (name : Nat)
  | pow (base exponent : Expr)
  deriving DecidableEq, Repr

def eval (fallback : Value → Value → Value) (env : Nat → Value) : Expr → Value
  | .literal value => value
  | .variable name => env name
  | .pow base exponent => spec fallback (eval fallback env base) (eval fallback env exponent)

def fold (fallback : Value → Value → Value) : Expr → Expr
  | .literal value => .literal value
  | .variable name => .variable name
  | .pow base exponent =>
    match fold fallback base, fold fallback exponent with
    | .literal a, .literal b => .literal (guarded fallback a b)
    | a, b => .pow a b

theorem folded_pair (fallback : Value → Value → Value) (env : Nat → Value)
    (a b : Expr) :
    eval fallback env
      (match a, b with
       | .literal x, .literal y => .literal (guarded fallback x y)
       | x, y => .pow x y) =
    spec fallback (eval fallback env a) (eval fallback env b) := by
  cases a <;> cases b <;> simp [eval, guard_refines_spec]

theorem folding_preserves_resolution (fallback : Value → Value → Value)
    (env : Nat → Value) (expr : Expr) :
    eval fallback env (fold fallback expr) = eval fallback env expr := by
  induction expr with
  | literal => rfl
  | «variable» => rfl
  | pow a b ha hb =>
    simp only [fold, folded_pair, ha, hb, eval]

theorem folding_preserves_mutation (fallback : Value → Value → Value)
    (before after : Nat → Value) (expr : Expr) :
    (eval fallback before (fold fallback expr), eval fallback after (fold fallback expr)) =
    (eval fallback before expr, eval fallback after expr) := by
  simp [folding_preserves_resolution]

def returnsOne (_ _ : Value) : Value := .unit false

theorem direct_delegate_counterexample :
    returnsOne .nan (.finite 0) ≠ spec returnsOne .nan (.finite 0) := by
  decide

theorem unit_base_depends_on_exponent :
    eval returnsOne (fun _ => .finite 0) (.pow (.literal (.unit false)) (.variable 0)) ≠
    eval returnsOne (fun _ => .nan) (.pow (.literal (.unit false)) (.variable 0)) := by
  decide

theorem not_always_one :
    ¬ ∀ env : Nat → Value,
      eval returnsOne env (.pow (.literal (.unit false)) (.variable 0)) = .unit false := by
  intro h
  have bad := h (fun _ => .nan)
  simp [eval, spec] at bad

end CssPowSpecial
