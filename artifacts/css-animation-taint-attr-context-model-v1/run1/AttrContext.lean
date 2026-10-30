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

private theorem attrs_stable (n : Nat) (e fallback : Expr) (allow : Bool) (v : Value)
    (resolved : eval allow e = some v) (marked : v.attrTainted = true) :
    eval allow (attrs n e fallback) = some v := by
  induction n with
  | zero => exact resolved
  | succ n ih =>
      simp [attrs, eval, ih, markAttr, marked]

theorem arbitrary_depth_boundaries (n m : Nat) :
    eval false (attrs (n + 1) (.ref (chain m leaf outer) inner) outer) = some innerValue ∧
    eval true (attrs (n + 1) (.ref (chain m leaf outer) inner) outer) = some (markAttr leaf) ∧
    eval false (.ref (attrs (n + 1) (.ref (chain m leaf outer) inner) outer) outer) = some outerValue := by
  have blocked : eval false (.ref (chain m leaf outer) inner) = some innerValue := by
    simp [eval, chain_custom, allowed, leaf, inner]
  have admitted : eval true (.ref (chain m leaf outer) inner) = some leaf := by
    simp [eval, chain_custom, allowed]
  have firstBlocked : eval false (.attr true (.ref (chain m leaf outer) inner) outer) = some innerValue := by
    simp [eval, blocked, markAttr, innerValue]
  have firstAdmitted : eval true (.attr true (.ref (chain m leaf outer) inner) outer) = some (markAttr leaf) := by
    simp [eval, admitted]
  have blockedAll : eval false (attrs (n + 1) (.ref (chain m leaf outer) inner) outer) = some innerValue := by
    have shift : ∀ k, attrs (k + 1) (.ref (chain m leaf outer) inner) outer = attrs k (.attr true (.ref (chain m leaf outer) inner) outer) outer := by
      intro k; induction k with
      | zero => rfl
      | succ k ih => simp only [attrs, ih]
    rw [shift]
    exact attrs_stable n _ _ false innerValue firstBlocked rfl
  have admittedAll : eval true (attrs (n + 1) (.ref (chain m leaf outer) inner) outer) = some (markAttr leaf) := by
    have shift : ∀ k, attrs (k + 1) (.ref (chain m leaf outer) inner) outer = attrs k (.attr true (.ref (chain m leaf outer) inner) outer) outer := by
      intro k; induction k with
      | zero => rfl
      | succ k ih => simp only [attrs, ih]
    rw [shift]
    exact attrs_stable n _ _ true (markAttr leaf) firstAdmitted rfl
  exact ⟨blockedAll, admittedAll, by simp [eval, admittedAll, allowed, markAttr, leaf, outer]⟩

theorem no_context_free_final_value :
    ¬ ∃ cached : Option Value, cached = eval false direct ∧ cached = eval true direct := by
  decide

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
