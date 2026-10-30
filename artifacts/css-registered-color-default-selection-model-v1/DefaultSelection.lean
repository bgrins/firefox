import Selection

namespace DefaultSelection
open SelectedColor

inductive Default where
  | computed (value : Nat)
  | specified (value : Value)
  | absent
  deriving DecidableEq, Repr

inductive Chosen where
  | selected (value : Value)
  | inheritedOrComputed (value : Nat)
  | recomputeInitial (value : Value)
  | absent
  deriving DecidableEq, Repr

def choose (parsed : Option Value) (fallback : Default) : Chosen :=
  match parsed with
  | some v => .selected v
  | none => match fallback with
    | .computed n => .inheritedOrComputed n
    | .specified v => .recomputeInitial v
    | .absent => .absent

def needed : Chosen → Bool
  | .selected v | .recomputeInitial v => depends (some v)
  | .inheritedOrComputed _ | .absent => false

def compute (v : Value) (dark : Bool) : Nat :=
  match v with
  | .system => if dark then 1 else 0
  | .absolute => 2
  | .ident _ => 3

def evaluate : Chosen → Bool → Option Nat
  | .selected v, scheme | .recomputeInitial v, scheme => some (compute v scheme)
  | .inheritedOrComputed n, _ => some n
  | .absent, _ => none

def scheduled (dependency : Bool) (chosen : Chosen) (oldScheme newScheme : Bool) : Option Nat :=
  evaluate chosen (if dependency then newScheme else oldScheme)

def invalidMeansIndependent (parsed : Option Value) : Bool := depends parsed

theorem inherited_has_no_recomputation_edge (n : Nat) :
    needed (choose none (.computed n)) = false := by rfl

theorem initial_system_keeps_edge :
    needed (choose none (.specified .system)) = true := by rfl

theorem initial_absolute_has_no_scheme_edge :
    needed (choose none (.specified .absolute)) = false := by rfl

theorem successful_parse_ignores_default (v : Value) (fallback : Default) :
    choose (some v) fallback = .selected v := by rfl

theorem initial_and_computed_are_distinct :
    choose none (.specified .system) ≠ choose none (.computed 0) := by decide

theorem computed_copy_is_stable (n : Nat) (a b : Bool) :
    evaluate (choose none (.computed n)) a = evaluate (choose none (.computed n)) b := by rfl

theorem invalid_parse_counterexample :
    invalidMeansIndependent none = false ∧
    scheduled (invalidMeansIndependent none) (choose none (.specified .system)) false true = some 0 ∧
    evaluate (choose none (.specified .system)) true = some 1 := by decide

theorem retained_default_repairs_counterexample :
    scheduled (needed (choose none (.specified .system)))
      (choose none (.specified .system)) false true = some 1 := by decide

theorem chosen_scheduler_matches_evaluation (chosen : Chosen) (a b : Bool) :
    scheduled (needed chosen) chosen a b = evaluate chosen b := by
  cases chosen with
  | selected v => cases v <;> simp [scheduled, needed, depends, evaluate, compute]
  | recomputeInitial v => cases v <;> simp [scheduled, needed, depends, evaluate, compute]
  | inheritedOrComputed n => rfl
  | absent => rfl

theorem absent_stays_absent (a b : Bool) :
    scheduled false (choose none .absent) a b = none := by rfl

end DefaultSelection
