import Std

namespace LineHeightContext

inductive Length (α : Type) where
  | px : α → Length α
  | em : Nat → Length α
  | lh : Nat → Length α
  deriving DecidableEq, Repr

inductive Leaf (α : Type) where
  | number : α → Leaf α
  | percentage : Nat → Leaf α
  | length : Length α → Leaf α
  | randomKey : Nat → Leaf α
  | siblingIndex
  | siblingCount
  deriving DecidableEq, Repr

inductive Value (α : Type) where
  | number : α → Value α
  | length : α → Value α
  | percentage : Nat → Value α
  deriving DecidableEq, Repr

structure Context (α : Type) where
  emBasis : α
  usedFont : α
  inheritedLineHeight : α
  currentLineHeight : α
  scale : Nat → α → α
  randomBase : Nat → α
  siblingIndex : α
  siblingCount : α

def resolveLength (c : Context α) (inherited : Bool) : Length α → α
  | .px n => n
  | .em n => c.scale n c.emBasis
  | .lh n => c.scale n (if inherited then c.inheritedLineHeight else c.currentLineHeight)

def genericMap (c : Option (Context α)) : Leaf α → Option (Value α)
  | .number n => some (.number n)
  | .percentage n => some (.percentage n)
  | .length l => c.map (fun ctx => .length (resolveLength ctx false l))
  | .randomKey key => c.map (fun ctx => .number (ctx.randomBase key))
  | .siblingIndex => c.map (fun ctx => .number ctx.siblingIndex)
  | .siblingCount => c.map (fun ctx => .number ctx.siblingCount)

def correctedMap (c : Context α) : Leaf α → Option (Value α)
  | .percentage n => some (.length (c.scale n c.emBasis))
  | .length l => some (.length (resolveLength c true l))
  | other => genericMap (some c) other

def referenceLeaf (c : Context α) : Leaf α → Option (Value α)
  | .number n => some (.number n)
  | .percentage n => some (.length (c.scale n c.emBasis))
  | .length (.px n) => some (.length n)
  | .length (.em n) => some (.length (c.scale n c.emBasis))
  | .length (.lh n) => some (.length (c.scale n c.inheritedLineHeight))
  | .randomKey key => some (.number (c.randomBase key))
  | .siblingIndex => some (.number c.siblingIndex)
  | .siblingCount => some (.number c.siblingCount)

def oldCloningMap (c : Context α) : Leaf α → Option (Value α)
  | .randomKey _ | .siblingIndex | .siblingCount => none
  | other => correctedMap c other

inductive Expr (α : Type) where
  | leaf : Leaf α → Expr α
  | unary : Nat → Expr α → Expr α
  | binary : Nat → Expr α → Expr α → Expr α

structure Operations (α : Type) where
  unary : Nat → Value α → Option (Value α)
  binary : Nat → Value α → Value α → Option (Value α)

def evaluate (ops : Operations α) (mapLeaf : Leaf α → Option (Value α)) :
    Expr α → Option (Value α)
  | .leaf l => mapLeaf l
  | .unary op arg => (evaluate ops mapLeaf arg).bind (ops.unary op)
  | .binary op left right => (evaluate ops mapLeaf left).bind fun l =>
      (evaluate ops mapLeaf right).bind fun r => ops.binary op l r

theorem special_bases_preserved (c : Context α) (n : Nat) :
    correctedMap c (.percentage n) = some (.length (c.scale n c.emBasis)) ∧
    correctedMap c (.length (.lh n)) = some (.length (c.scale n c.inheritedLineHeight)) := by
  simp [correctedMap, resolveLength]

theorem context_inputs_resolve (c : Context α) (key : Nat) :
    correctedMap c (.randomKey key) = some (.number (c.randomBase key)) ∧
    correctedMap c .siblingIndex = some (.number c.siblingIndex) ∧
    correctedMap c .siblingCount = some (.number c.siblingCount) := by
  simp [correctedMap, genericMap]

theorem leaf_semantics (c : Context α) (l : Leaf α) :
    correctedMap c l = referenceLeaf c l := by
  cases l with
  | length len => cases len <;> rfl
  | _ => rfl

theorem expression_semantics (c : Context α) (ops : Operations α) (e : Expr α) :
    evaluate ops (correctedMap c) e = evaluate ops (referenceLeaf c) e := by
  induction e with
  | leaf l => exact leaf_semantics c l
  | unary op arg ih => simp only [evaluate, ih]
  | binary op left right ihl ihr => simp only [evaluate, ihl, ihr]

def exampleContext : Context Nat :=
  ⟨10, 10, 40, 70, Nat.mul, fun _ => 1, 2, 3⟩

def exampleOperations : Operations Nat where
  unary := fun _ value => match value with
    | .number base => some (.number (1 + 2 * base))
    | _ => none
  binary := fun _ left right => match left, right with
    | .length n, .length d => if d = 0 then none else some (.number (n / d))
    | _, _ => none

def usedHeight (c : Context Nat) : Option (Value Nat) → Nat
  | some (.number n) => c.usedFont * n
  | _ => 0

def randomExpression : Expr Nat := .unary 0 (.leaf (.randomKey 7))
def lhRatio : Expr Nat := .binary 0 (.leaf (.length (.lh 1))) (.leaf (.length (.em 1)))

theorem old_clone_random_witness :
    evaluate exampleOperations (correctedMap exampleContext) randomExpression = some (.number 3) ∧
    evaluate exampleOperations (oldCloningMap exampleContext) randomExpression = none ∧
    usedHeight exampleContext (evaluate exampleOperations (correctedMap exampleContext) randomExpression) = 30 ∧
    usedHeight exampleContext (evaluate exampleOperations (oldCloningMap exampleContext) randomExpression) = 0 := by
  decide +kernel

theorem generic_only_lh_witness :
    usedHeight exampleContext (evaluate exampleOperations (correctedMap exampleContext) lhRatio) = 40 ∧
    usedHeight exampleContext (evaluate exampleOperations (genericMap (some exampleContext)) lhRatio) = 70 := by
  decide +kernel

end LineHeightContext
