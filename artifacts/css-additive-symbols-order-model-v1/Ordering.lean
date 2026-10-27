import Range

namespace AdditiveOrder
open CounterRangeRepresentation

def values : List IntegerRep → Option (List Int)
  | [] => some []
  | x :: xs => do
    let n ← resolve x
    let ns ← values xs
    return n :: ns

def descending : List Int → Bool
  | [] | [_] => true
  | a :: b :: rest => decide (a > b) && descending (b :: rest)

def resolvedOrder (xs : List IntegerRep) : Option Bool :=
  (values xs).map descending

inductive Meaning : List IntegerRep → List Int → Prop
  | nil : Meaning [] []
  | cons {r n rs ns} : resolve r = some n → Meaning rs ns → Meaning (r :: rs) (n :: ns)

theorem resolution_list (xs : List IntegerRep) (ns : List Int)
    (meaning : Meaning xs ns) : values xs = some ns := by
  induction meaning with
  | nil => rfl
  | cons head tail ih => simp [values, head, ih]

theorem ordered_resolution (xs : List IntegerRep) (ns : List Int)
    (meaning : Meaning xs ns) :
    resolvedOrder xs = some (descending ns) := by
  simp [resolvedOrder, resolution_list xs ns meaning]

theorem representation_independence (a b : List IntegerRep) (ns : List Int)
    (left : Meaning a ns)
    (right : Meaning b ns) :
    resolvedOrder a = resolvedOrder b := by
  rw [ordered_resolution a ns left, ordered_resolution b ns right]

def inlineGreater (a b : IntegerRep) : Bool :=
  match inlineGet a, inlineGet b with
  | some x, some y => decide (x > y)
  | some _, none => true
  | _, _ => false

example : resolvedOrder [.inline 3, .boxedResolved 1] = some true := by decide +kernel
example : resolvedOrder [.boxedResolved 3, .boxedResolved 1] = some true := by decide +kernel
example : resolvedOrder [.inline 1, .boxedResolved 1] = some false := by decide +kernel
example : resolvedOrder [.inline 1, .boxedResolved 3] = some false := by decide +kernel
example : resolvedOrder [.unresolved] = none := by decide +kernel
example : resolvedOrder [] = some true := by decide +kernel
example : resolvedOrder [.boxedResolved 3] = some true := by decide +kernel
example : resolvedOrder [.boxedResolved (-1), .boxedResolved (-2)] = some true ∧
    resolvedOrder [.boxedResolved 0, .boxedResolved 0] = some false := by decide +kernel

#print axioms resolution_list
#print axioms ordered_resolution
#print axioms representation_independence
end AdditiveOrder
