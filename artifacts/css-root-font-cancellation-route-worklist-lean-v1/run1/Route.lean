import Delivery

namespace CancellationRoute

structure Node where
  id : Nat
  animated : Bool
  fontChanged : Bool
  deriving DecidableEq, Repr

structure State where
  pending : Option Node
  suffix : List Node
  visited : List Node
  deriving DecidableEq, Repr

def load : List Node → List Node → State
  | [], visited => ⟨none, [], visited⟩
  | node :: rest, visited => ⟨some node, rest, visited⟩

def step (forward : Node → Bool) (s : State) : State :=
  match s.pending with
  | none => s
  | some node =>
    let visited := s.visited ++ [node]
    match s.suffix with
    | [] => load [] visited
    | next :: rest =>
      if forward next then ⟨some next, rest, visited⟩
      else ⟨none, next :: rest, visited⟩

def run (forward : Node → Bool) : Nat → State → State
  | 0, s => s
  | n + 1, s => run forward n (step forward s)

def forwardAll : Node → Bool := fun _ => true
def onlyAnimated : Node → Bool := (·.animated)

theorem handoff (node : Node) (rest prefix : List Node) :
    step forwardAll (load (node :: rest) prefix) = load rest (prefix ++ [node]) := by
  cases rest <;> simp [step, load, forwardAll]

theorem scheduled_route_visits_in_order (route prefix : List Node) :
    run forwardAll route.length (load route prefix) = load [] (prefix ++ route) := by
  induction route generalizing prefix with
  | nil => simp [run, load]
  | cons node rest ih =>
    simp only [List.length_cons, run, handoff]
    rw [ih]
    simp [List.append_assoc]

theorem scheduled_target_visited (ancestors : List Node) (target : Node) :
    target ∈ (run forwardAll (ancestors ++ [target]).length
      (load (ancestors ++ [target]) [])).visited := by
  rw [scheduled_route_visits_in_order]
  simp [load]

def visitWitness (route : List Node) (s : State) : List CancellationDelivery.Hop :=
  route.map fun node => ⟨s.visited.contains node, node.fontChanged⟩

theorem completed_route_supplies_visitation (route : List Node) :
    CancellationDelivery.reached
      (visitWitness route (run forwardAll route.length (load route []))) = true := by
  rw [scheduled_route_visits_in_order]
  simp only [visitWitness, load, List.nil_append, CancellationDelivery.reached,
    List.all_map, Function.comp_def]
  apply List.all_eq_true.mpr
  intro node member
  exact List.contains_iff_mem.mpr member

theorem no_scheduled_work_no_visitation (forward : Node → Bool) (n : Nat)
    (rest visited : List Node) :
    run forward n ⟨none, rest, visited⟩ = ⟨none, rest, visited⟩ := by
  induction n with
  | zero => rfl
  | succ n ih => simpa [run, step] using ih

def root : Node := ⟨1, false, true⟩
def fixedMiddle : Node := ⟨2, false, false⟩
def dependent : Node := ⟨3, true, false⟩
def deepRoute : List Node := [root, fixedMiddle, dependent]
def completed : State := run forwardAll deepRoute.length (load deepRoute [])
def prematurelyStopped : State := run onlyAnimated deepRoute.length (load deepRoute [])

theorem fixed_unanimated_hop_preserved :
    completed.visited = [root, fixedMiddle, dependent] ∧ completed.pending = none := by decide +kernel

theorem animated_child_only_loses_descendant :
    prematurelyStopped.visited = [root] ∧
    dependent ∉ prematurelyStopped.visited ∧
    prematurelyStopped.suffix = [fixedMiddle, dependent] := by decide +kernel

theorem immediate_animated_child_control :
    (run onlyAnimated 2 (load [root, dependent] [])).visited = [root, dependent] := by decide +kernel

theorem insufficient_dispatches_counterexample :
    dependent ∉ (run forwardAll 2 (load deepRoute [])).visited := by decide +kernel

end CancellationRoute
