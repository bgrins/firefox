import Std

namespace PriorityClosure

inductive Selection where
  | skipped
  | accepted
  | rejected
  | evaluatedThenReverted
  deriving DecidableEq, Repr

inductive Schedule where
  | beforePop
  | afterPop
  deriving DecidableEq, Repr

def evaluated : Selection → Bool
  | .skipped => false
  | _ => true

def fallbackSelected : Selection → Bool
  | .rejected | .evaluatedThenReverted => true
  | _ => false

-- Nodes: custom root, line-height, font-size, writing-mode, attribute, primary.
def edges (s : Selection) : Nat → List Nat
  | 0 => [1]
  | 1 => [2, 3]
  | 3 => if evaluated s then [4] else []
  | 4 => if fallbackSelected s then [5, 0] else [5]
  | _ => []

def observedEdges (schedule : Schedule) (s : Selection) (v : Nat) : List Nat :=
  if schedule == .afterPop && v == 1 then [2] else edges s v

structure State where
  next : Nat := 0
  indices : Nat → Option Nat := fun _ => none
  low : Nat → Nat := fun _ => 0
  stack : List Nat := []
  components : List (List Nat) := []
  fuelExhausted : Bool := false

def setAt (f : Nat → α) (v : Nat) (a : α) : Nat → α :=
  fun w => if w == v then a else f w

def popThrough (v : Nat) : List Nat → List Nat × List Nat
  | [] => ([], [])
  | w :: ws =>
    if w == v then ([w], ws) else
      let (taken, rest) := popThrough v ws
      (w :: taken, rest)

def visit (schedule : Schedule) (s : Selection) : Nat → State → Nat → State
  | 0, state, _ => { state with fuelExhausted := true }
  | fuel + 1, state, v =>
    if (state.indices v).isSome then state else
      let index := state.next
      let entered : State := { state with
        next := index + 1
        indices := setAt state.indices v (some index)
        low := setAt state.low v index
        stack := v :: state.stack }
      let linked := (observedEdges schedule s v).foldl (fun current w =>
        match current.indices w with
        | none =>
          let after := visit schedule s fuel current w
          { after with low := setAt after.low v (min (after.low v) (after.low w)) }
        | some wi =>
          if current.stack.contains w then
            { current with low := setAt current.low v (min (current.low v) wi) }
          else current) entered
      if linked.low v != index then linked else
        let (component, rest) := popThrough v linked.stack
        let closed := { linked with stack := rest, components := component :: linked.components }
        if schedule == .afterPop && v == 1 then visit schedule s fuel closed 3
        else closed

def run (schedule : Schedule) (s : Selection) : State :=
  [0, 1, 2, 3, 4, 5].foldl (visit schedule s 16) {}

def sameComponent (state : State) (a b : Nat) : Bool :=
  state.components.any (fun group => group.contains a && group.contains b)

-- Independent bounded-walk oracle; it does not inspect discovery order or stacks.
def reachable (s : Selection) : Nat → Nat → Nat → Bool
  | 0, a, b => a == b
  | fuel + 1, a, b => a == b || (edges s a).any (fun w => reachable s fuel w b)

def mutuallyReachable (s : Selection) (a b : Nat) : Bool :=
  reachable s 6 a b && reachable s 6 b a

def agreesWithOracle (schedule : Schedule) (s : Selection) : Bool :=
  [0, 1, 2, 3, 4, 5].all fun a =>
    [0, 1, 2, 3, 4, 5].all fun b =>
      sameComponent (run schedule s) a b == mutuallyReachable s a b

def completed (state : State) : Bool :=
  !state.fuelExhausted && state.next == 6 && state.stack.isEmpty &&
    [0, 1, 2, 3, 4, 5].all (fun v => state.components.flatten.count v == 1)

def finished (schedule : Schedule) (s : Selection) : Bool :=
  completed (run schedule s)

theorem before_pop_matches_walk_oracle :
    ∀ s : Selection, agreesWithOracle .beforePop s = true := by
  intro s
  cases s <;> decide

theorem all_bounded_runs_finish :
    ∀ schedule : Schedule, ∀ s : Selection, finished schedule s = true := by
  intro schedule s
  cases schedule <;> cases s <;> decide

theorem premature_pop_splits_a_real_component :
    mutuallyReachable .rejected 0 1 = true ∧
    sameComponent (run .afterPop .rejected) 0 1 = false ∧
    sameComponent (run .afterPop .rejected) 0 3 = true ∧
    agreesWithOracle .afterPop .rejected = false := by decide

theorem unused_fallback_is_not_a_cycle_edge :
    mutuallyReachable .accepted 0 1 = false ∧
    agreesWithOracle .afterPop .accepted = true ∧
    agreesWithOracle .afterPop .skipped = true := by decide

theorem evaluated_revert_retains_selected_dependencies :
    edges .evaluatedThenReverted = edges .rejected ∧
    agreesWithOracle .afterPop .evaluatedThenReverted = false ∧
    agreesWithOracle .beforePop .evaluatedThenReverted = true := by
  constructor
  · rfl
  · decide

end PriorityClosure
