import Std
namespace FallbackPreparation

inductive Kind where | var | env | typedAttr | untypedAttr deriving DecidableEq, Repr
structure Info where
  kind : Kind
  name : Nat
  ns : Option Nat
  deriving DecidableEq, Repr

inductive Ref where
  | mk (info : Info) (fallback : Option (List Ref))
  deriving Repr

def Ref.info : Ref → Info | .mk info _ => info
def Ref.fallback : Ref → Option (List Ref) | .mk _ fallback => fallback

mutual
  def refCost : Ref → Nat
    | .mk _ none => 0
    | .mk _ (some refs) => 1 + refsCost refs
  def refsCost : List Ref → Nat
    | [] => 0
    | ref :: rest => refCost ref + refsCost rest
end

def stackCost : List (List Ref) → Nat
  | [] => 0
  | refs :: rest => 1 + refsCost refs + stackCost rest

def enqueue (ref : Ref) (stack : List (List Ref)) : List (List Ref) :=
  match ref.fallback with | none => stack | some refs => refs :: stack

def scan : List Ref → List (List Ref) → List (List Ref)
  | [], stack => stack
  | ref :: rest, stack => scan rest (enqueue ref stack)

def children : List Ref → List (List Ref)
  | [] => []
  | ref :: rest => match ref.fallback with
    | none => children rest
    | some refs => refs :: children rest

theorem scan_actual_push_order (refs : List Ref) (stack : List (List Ref)) :
    scan refs stack = (children refs).reverse ++ stack := by
  induction refs generalizing stack with
  | nil => simp [scan, children]
  | cons ref rest ih =>
    cases ref with | mk info fallback =>
      cases fallback <;> simp [scan, enqueue, Ref.fallback, children, ih, List.append_assoc]

theorem enqueue_cost (ref : Ref) (stack : List (List Ref)) :
    stackCost (enqueue ref stack) = refCost ref + stackCost stack := by
  cases ref with | mk info fallback =>
    cases fallback <;> simp [enqueue, Ref.fallback, stackCost, refCost]

theorem scan_cost (refs : List Ref) (stack : List (List Ref)) :
    stackCost (scan refs stack) = refsCost refs + stackCost stack := by
  induction refs generalizing stack with
  | nil => simp [scan, refsCost]
  | cons ref rest ih =>
    simp [scan, refsCost, ih, enqueue_cost, Nat.add_left_comm, Nat.add_comm]

theorem each_pop_decreases_one (refs : List Ref) (stack : List (List Ref)) :
    stackCost (refs :: stack) = stackCost (scan refs stack) + 1 := by
  simp [stackCost, scan_cost, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

def run : Nat → List (List Ref) → List Ref
  | 0, _ => []
  | _ + 1, [] => []
  | fuel + 1, refs :: rest => refs ++ run fuel (scan refs rest)

def pending : Nat → List (List Ref) → List (List Ref)
  | 0, stack => stack
  | _ + 1, [] => []
  | fuel + 1, refs :: rest => pending fuel (scan refs rest)

theorem stackCost_zero_iff (stack : List (List Ref)) : stackCost stack = 0 ↔ stack = [] := by
  cases stack <;> simp [stackCost]

theorem finite_worklist_terminates (fuel : Nat) (stack : List (List Ref))
    (enough : stackCost stack ≤ fuel) : pending fuel stack = [] := by
  induction fuel generalizing stack with
  | zero =>
    have h : stackCost stack = 0 := by omega
    have empty := (stackCost_zero_iff stack).mp h
    simp [pending, empty]
  | succ fuel ih =>
    cases stack with
    | nil => rfl
    | cons refs rest =>
      simp only [pending]
      apply ih
      have h := each_pop_decreases_one refs rest
      omega

mutual
  def refMass (weight : Ref → Nat) : Ref → Nat
    | ref@(.mk _ none) => weight ref
    | ref@(.mk _ (some refs)) => weight ref + refsMass weight refs
  def refsMass (weight : Ref → Nat) : List Ref → Nat
    | [] => 0
    | ref :: rest => refMass weight ref + refsMass weight rest
end

def ownMass (weight : Ref → Nat) : List Ref → Nat
  | [] => 0
  | ref :: rest => weight ref + ownMass weight rest

def stackMass (weight : Ref → Nat) : List (List Ref) → Nat
  | [] => 0
  | refs :: rest => refsMass weight refs + stackMass weight rest

theorem enqueue_mass (weight : Ref → Nat) (ref : Ref) (stack : List (List Ref)) :
    weight ref + stackMass weight (enqueue ref stack) = refMass weight ref + stackMass weight stack := by
  cases ref with | mk info fallback =>
    cases fallback <;> simp [enqueue, Ref.fallback, stackMass, refMass, Nat.add_assoc]

theorem scan_mass (weight : Ref → Nat) (refs : List Ref) (stack : List (List Ref)) :
    ownMass weight refs + stackMass weight (scan refs stack) =
      refsMass weight refs + stackMass weight stack := by
  induction refs generalizing stack with
  | nil => simp [scan, ownMass, refsMass]
  | cons ref rest ih =>
    simp only [scan, ownMass, refsMass]
    have h := ih (enqueue ref stack)
    have h' := enqueue_mass weight ref stack
    omega

theorem ownMass_append (weight : Ref → Nat) (a b : List Ref) :
    ownMass weight (a ++ b) = ownMass weight a + ownMass weight b := by
  induction a with
  | nil => simp [ownMass]
  | cons ref rest ih => simp [ownMass, ih, Nat.add_assoc]

theorem run_complete (fuel : Nat) (stack : List (List Ref)) (weight : Ref → Nat)
    (enough : stackCost stack ≤ fuel) :
    ownMass weight (run fuel stack) = stackMass weight stack := by
  induction fuel generalizing stack with
  | zero =>
    have h : stackCost stack = 0 := by omega
    have empty := (stackCost_zero_iff stack).mp h
    simp [run, empty, ownMass, stackMass]
  | succ fuel ih =>
    cases stack with
    | nil => simp [run, ownMass, stackMass]
    | cons refs rest =>
      have step := each_pop_decreases_one refs rest
      have bound : stackCost (scan refs rest) ≤ fuel := by omega
      simp only [run, ownMass_append, ih _ bound]
      exact scan_mass weight refs rest

theorem empty_fallback_is_still_enqueued (info : Info) (stack : List (List Ref)) :
    enqueue (.mk info (some [])) stack = [] :: stack := rfl

theorem metadata_does_not_control_enqueue (a b : Info) (fallback : Option (List Ref))
    (stack : List (List Ref)) :
    enqueue (.mk a fallback) stack = enqueue (.mk b fallback) stack := rfl

end FallbackPreparation
