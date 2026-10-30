import Std

namespace AliasGuard

structure Value where
  token : Nat
  animationTainted : Bool
  attrTainted : Bool
  deriving DecidableEq, Repr

inductive Expr where
  | value : Option Value → Expr
  | ref : Expr → Expr → Expr
  deriving DecidableEq, Repr

def allowed (allowTaint : Bool) (v : Value) : Bool :=
  allowTaint || !v.animationTainted

def eval (allowTaint : Bool) : Expr → Option Value
  | .value v => v
  | .ref primary fallback =>
      match eval true primary with
      | some v => if allowed allowTaint v then some v else eval allowTaint fallback
      | none => eval allowTaint fallback

def chain : Nat → Value → Expr → Expr
  | 0, leaf, _ => .value (some leaf)
  | n + 1, leaf, innerFallback => .ref (chain n leaf innerFallback) innerFallback

theorem ready_and_deferred_agree (allowTaint : Bool) (alias fallback : Expr) :
    eval allowTaint (.ref (.value (eval true alias)) fallback) =
    eval allowTaint (.ref alias fallback) := by rfl

theorem chain_resolves_in_custom_context (n : Nat) (leaf : Value) (inner : Expr) :
    eval true (chain n leaf inner) = some leaf := by
  induction n with
  | zero => rfl
  | succ n ih => simp [chain, eval, ih, allowed]

theorem reject_only_at_outer_sink (n : Nat) (leaf : Value) (inner outer : Expr)
    (tainted : leaf.animationTainted = true) :
    eval false (.ref (chain n leaf inner) outer) = eval false outer ∧
    eval true (.ref (chain n leaf inner) outer) = some leaf := by
  simp [eval, chain_resolves_in_custom_context, allowed, tainted]

def leaf : Value := ⟨2, true, true⟩
def inner : Expr := .value (some ⟨3, false, false⟩)
def outer : Expr := .value (some ⟨5, false, false⟩)
def nested : Expr := .ref (chain 2 leaf inner) outer

theorem fallback_and_metadata_controls :
    eval false nested = some ⟨5, false, false⟩ ∧
    eval true nested = some leaf ∧
    eval false (.ref (.ref (.value none) inner) outer) = some ⟨3, false, false⟩ ∧
    eval false (.ref (.value none) (.ref (.value (some leaf)) (.value none))) = none := by
  decide

end AliasGuard
