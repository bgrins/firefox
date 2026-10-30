import Std

namespace AttrContext

structure Value where
  token : Nat
  animationTainted : Bool
  attrTainted : Bool
  deriving DecidableEq, Repr

inductive Expr where
  | value : Option Value → Expr
  | ref : Expr → Expr → Expr
  | attr : Bool → Expr → Expr → Expr
  deriving DecidableEq, Repr

def markAttr (v : Value) : Value := { v with attrTainted := true }
def allowed (allow : Bool) (v : Value) : Bool := allow || !v.animationTainted

def eval (allow : Bool) : Expr → Option Value
  | .value v => v
  | .ref primary fallback =>
      match eval true primary with
      | some v => if allowed allow v then some v else eval allow fallback
      | none => eval allow fallback
  | .attr parses primary fallback =>
      match eval allow primary with
      | some v => if parses then some (markAttr v) else eval allow fallback
      | none => eval allow fallback

def chain : Nat → Value → Expr → Expr
  | 0, leaf, _ => .value (some leaf)
  | n + 1, leaf, fallback => .ref (chain n leaf fallback) fallback

def attrs : Nat → Expr → Expr → Expr
  | 0, e, _ => e
  | n + 1, e, fallback => .attr true (attrs n e fallback) fallback

def leaf : Value := ⟨1, true, false⟩
def innerValue : Value := ⟨2, false, true⟩
def outerValue : Value := ⟨3, false, false⟩
def inner : Expr := .value (some innerValue)
def outer : Expr := .value (some outerValue)
def body : Expr := .ref (.value (some leaf)) inner
def direct : Expr := .attr true body outer

theorem custom_ready_deferred (allow : Bool) (primary fallback : Expr) :
    eval allow (.ref (.value (eval true primary)) fallback) =
      eval allow (.ref primary fallback) := by rfl

private theorem chain_custom (n : Nat) (v : Value) (fallback : Expr) :
    eval true (chain n v fallback) = some v := by
  induction n with
  | zero => rfl
  | succ n ih => simp [chain, eval, ih, allowed]

private theorem attrs_resolve (n : Nat) (e fallback : Expr) (allow : Bool) (v : Value)
    (resolved : eval allow e = some v) :
    eval allow (attrs (n + 1) e fallback) = some (markAttr v) := by
  induction n with
  | zero =>
      change (match eval allow e with
        | some w => some (markAttr w)
        | none => eval allow fallback) = _
      rw [resolved]
  | succ n ih =>
      change (match eval allow (attrs (n + 1) e fallback) with
        | some w => some (markAttr w)
        | none => eval allow fallback) = _
      rw [ih]
      rfl

theorem arbitrary_depth_boundaries (n m : Nat) :
    eval false (attrs (n + 1) (.ref (chain m leaf outer) inner) outer) = some innerValue ∧
    eval true (attrs (n + 1) (.ref (chain m leaf outer) inner) outer) = some (markAttr leaf) ∧
    eval false (.ref (attrs (n + 1) (.ref (chain m leaf outer) inner) outer) outer) = some outerValue := by
  have blocked : eval false (.ref (chain m leaf outer) inner) = some innerValue := by
    simp [eval, chain_custom, allowed, leaf, inner]
  have admitted : eval true (.ref (chain m leaf outer) inner) = some leaf := by
    simp [eval, chain_custom, allowed]
  have blockedAll := attrs_resolve n _ outer false innerValue blocked
  have admittedAll := attrs_resolve n _ outer true leaf admitted
  refine ⟨blockedAll, admittedAll, ?_⟩
  change (match eval true (attrs (n + 1) (.ref (chain m leaf outer) inner) outer) with
    | some v => if allowed false v then some v else eval false outer
    | none => eval false outer) = _
  rw [admittedAll]
  rfl

theorem no_context_free_final_value :
    ¬ ∃ cached : Option Value, cached = eval false direct ∧ cached = eval true direct := by
  rintro ⟨cached, left, right⟩
  have different : eval false direct ≠ eval true direct := by decide
  exact different (left.symm.trans right)

def resetCache : Option Value := eval false (.attr true (.value (eval true body)) outer)
def rejectWholeAttr : Option Value :=
  match eval true direct with
  | some v => if allowed false v then some v else eval false outer
  | none => eval false outer

theorem repair_discriminator_and_failure_controls :
    eval false direct = some innerValue ∧
    resetCache = some (markAttr leaf) ∧
    rejectWholeAttr = some outerValue ∧
    resetCache ≠ eval false direct ∧ rejectWholeAttr ≠ eval false direct ∧
    eval false (.attr false body outer) = some outerValue ∧
    eval false (.attr true (.value none) (.ref (.value (some leaf)) inner)) = some innerValue := by
  decide

end AttrContext
