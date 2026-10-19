import Std
set_option autoImplicit false

namespace QueryDependencies

inductive Op where
  | and | or
  deriving DecidableEq

mutual
inductive Expr where
  | style (id : Nat)
  | other (id : Nat)
  | neg (child : Expr)
  | parens (child : Expr)
  | operation (op : Op) (children : Forest)
inductive Forest where
  | nil
  | cons (head : Expr) (tail : Forest)
end

mutual
def occurs (e : Expr) (s : Nat) : Prop :=
  match e with
  | .style id => id = s
  | .other _ => False
  | .neg c | .parens c => occurs c s
  | .operation _ cs => occursForest cs s
def occursForest (cs : Forest) (s : Nat) : Prop :=
  match cs with
  | .nil => False
  | .cons c cs => occurs c s ∨ occursForest cs s
end

def depends (deps : Nat → List Nat) (e : Expr) (a : Nat) : Prop :=
  ∃ s, occurs e s ∧ a ∈ deps s

def dependsForest (deps : Nat → List Nat) (cs : Forest) (a : Nat) : Prop :=
  ∃ s, occursForest cs s ∧ a ∈ deps s

mutual
def collect (deps : Nat → List Nat) (e : Expr) (acc : List Nat) : List Nat :=
  match e with
  | .style s => deps s ++ acc
  | .other _ => acc
  | .neg c => collect deps c acc
  | .parens c => collect deps c acc
  | .operation _ cs => collectForest deps cs acc
def collectForest (deps : Nat → List Nat) (cs : Forest) (acc : List Nat) : List Nat :=
  match cs with
  | .nil => acc
  | .cons c cs => collectForest deps cs (collect deps c acc)
end

mutual
theorem collector_complete (deps : Nat → List Nat) (e : Expr) (acc : List Nat) (a : Nat) :
    a ∈ collect deps e acc ↔ a ∈ acc ∨ depends deps e a := by
  cases e with
  | style s => simp [collect, depends, occurs, or_comm]
  | other s => simp [collect, depends, occurs]
  | neg c => exact collector_complete deps c acc a
  | parens c => exact collector_complete deps c acc a
  | operation op cs => exact forest_complete deps cs acc a
theorem forest_complete (deps : Nat → List Nat) (cs : Forest) (acc : List Nat) (a : Nat) :
    a ∈ collectForest deps cs acc ↔ a ∈ acc ∨ dependsForest deps cs a := by
  cases cs with
  | nil => simp [collectForest, dependsForest, occursForest]
  | cons c cs =>
    rw [collectForest, forest_complete, collector_complete]
    simp only [dependsForest, occursForest, or_and_right, exists_or]
    simp only [depends, or_assoc]
end

theorem collector_preserves_existing (deps : Nat → List Nat) (e : Expr)
    (acc : List Nat) (a : Nat) (h : a ∈ acc) : a ∈ collect deps e acc :=
  (collector_complete deps e acc a).mpr (Or.inl h)

theorem collector_no_missing_leaf (deps : Nat → List Nat) (e : Expr)
    (acc : List Nat) (s a : Nat) (h : occurs e s) (ha : a ∈ deps s) :
    a ∈ collect deps e acc :=
  (collector_complete deps e acc a).mpr (Or.inr ⟨s, h, ha⟩)

theorem collector_no_spurious (deps : Nat → List Nat) (e : Expr) (a : Nat) :
    a ∈ collect deps e [] ↔ depends deps e a := by
  simpa using collector_complete deps e [] a

abbrev Tri := Option Bool
def negate : Tri → Tri
  | none => none
  | some b => some (!b)
def combine (op : Op) (a b : Tri) : Tri :=
  match op, a, b with
  | .and, some false, _ | .and, _, some false => some false
  | .and, some true, some true => some true
  | .or, some true, _ | .or, _, some true => some true
  | .or, some false, some false => some false
  | _, _, _ => none
def identity : Op → Tri
  | .and => some true
  | .or => some false

mutual
def evaluate (style other : Nat → Tri) (e : Expr) : Tri :=
  match e with
  | .style s => style s
  | .other s => other s
  | .neg c => negate (evaluate style other c)
  | .parens c => evaluate style other c
  | .operation op cs => evaluateForest style other op cs
def evaluateForest (style other : Nat → Tri) (op : Op) (cs : Forest) : Tri :=
  match cs with
  | .nil => identity op
  | .cons c cs => combine op (evaluate style other c) (evaluateForest style other op cs)
end

mutual
theorem evaluation_congruence (left right other : Nat → Tri) (e : Expr)
    (h : ∀ s, occurs e s → left s = right s) :
    evaluate left other e = evaluate right other e := by
  cases e with
  | style s => exact h s rfl
  | other s => rfl
  | neg c => exact congrArg negate (evaluation_congruence left right other c h)
  | parens c => exact evaluation_congruence left right other c h
  | operation op cs => exact forest_congruence left right other op cs h
theorem forest_congruence (left right other : Nat → Tri) (op : Op) (cs : Forest)
    (h : ∀ s, occursForest cs s → left s = right s) :
    evaluateForest left other op cs = evaluateForest right other op cs := by
  cases cs with
  | nil => rfl
  | cons c cs =>
    simp only [evaluateForest]
    rw [evaluation_congruence left right other c (fun s hs => h s (Or.inl hs)),
        forest_congruence left right other op cs (fun s hs => h s (Or.inr hs))]
end

theorem evaluation_preserved (deps : Nat → List Nat)
    (leaf : (Nat → Nat) → Nat → Tri) (other : Nat → Tri)
    (before after : Nat → Nat) (e : Expr)
    (leafContract : ∀ s, (∀ a, a ∈ deps s → before a = after a) →
      leaf before s = leaf after s)
    (agree : ∀ a, a ∈ collect deps e [] → before a = after a) :
    evaluate (leaf before) other e = evaluate (leaf after) other e := by
  apply evaluation_congruence
  intro s hs
  apply leafContract s
  intro a ha
  exact agree a (collector_no_missing_leaf deps e [] s a hs ha)

def originalCollect (deps : Nat → List Nat) (e : Expr) : List Nat :=
  match e with
  | .style s => deps s
  | _ => []

theorem original_wrapper_counterexample :
    originalCollect (fun s => [s]) (.parens (.style 7)) = [] ∧
    collect (fun s => [s]) (.parens (.style 7)) [] = [7] := by decide

theorem short_circuited_branch_retained :
    collect (fun s => [s])
      (.operation .and (.cons (.style 0) (.cons (.style 1) .nil))) [] = [1, 0] := rfl

theorem noninterference_requires_all_branches :
    evaluate (fun _ => some true) (fun _ => none)
      (.operation .and (.cons (.style 0) (.cons (.style 1) .nil))) ≠
    evaluate (fun s => some (s == 0)) (fun _ => none)
      (.operation .and (.cons (.style 0) (.cons (.style 1) .nil))) := by decide

#print axioms collector_complete
#print axioms forest_complete
#print axioms collector_preserves_existing
#print axioms collector_no_missing_leaf
#print axioms collector_no_spurious
#print axioms evaluation_congruence
#print axioms forest_congruence
#print axioms evaluation_preserved
#print axioms original_wrapper_counterexample
#print axioms short_circuited_branch_retained
#print axioms noninterference_requires_all_branches
end QueryDependencies
