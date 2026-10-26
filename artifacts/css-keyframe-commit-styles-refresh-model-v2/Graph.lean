import Sampling

namespace KeyframeGraph
open KeyframeContext

structure Graph (n : Nat) where
  dependencies : Fin n → List (Fin n)
  rank : Fin n → Nat
  lower : ∀ node dep, dep ∈ dependencies node → rank dep < rank node
  compute : Fin n → Rat → List Rat → Rat


inductive DependencyPath (graph : Graph n) : Fin n → Fin n → Prop where
  | edge (member : dep ∈ graph.dependencies node) : DependencyPath graph node dep
  | trans : DependencyPath graph a b → DependencyPath graph b c → DependencyPath graph a c

theorem dependency_path_decreases (graph : Graph n) (path : DependencyPath graph node dep) :
    graph.rank dep < graph.rank node := by
  induction path with
  | edge member => exact graph.lower _ _ member
  | trans _ _ first second => exact Nat.lt_trans second first

theorem no_dependency_cycle (graph : Graph n) (node : Fin n) :
    ¬ DependencyPath graph node node := by
  intro path
  exact Nat.lt_irrefl _ (dependency_path_decreases graph path)

def value (graph : Graph n) (progress : Fin n → Rat) (node : Fin n) : Rat :=
  graph.compute node (progress node) ((graph.dependencies node).attach.map
    fun dep => value graph progress dep.val)
termination_by graph.rank node
decreasing_by exact graph.lower node dep.val dep.property

structure State (n : Nat) where
  cache : Fin n → Rat
  ready : List (Fin n) := []

def step (graph : Graph n) (progress : Fin n → Rat) (state : State n)
    (node : Fin n) : State n :=
  let result := graph.compute node (progress node) ((graph.dependencies node).attach.map
    fun dep => state.cache dep.val)
  ⟨fun other => if other = node then result else state.cache other, node :: state.ready⟩

def run (graph : Graph n) (progress : Fin n → Rat) : State n → List (Fin n) → State n
  | state, [] => state
  | state, node :: rest => run graph progress (step graph progress state node) rest

def admitted (graph : Graph n) : List (Fin n) → List (Fin n) → Bool
  | _, [] => true
  | ready, node :: rest =>
    (graph.dependencies node).all (fun dep => decide (dep ∈ ready)) &&
      admitted graph (node :: ready) rest

def Current (graph : Graph n) (progress : Fin n → Rat) (state : State n) : Prop :=
  ∀ node, node ∈ state.ready → state.cache node = value graph progress node

theorem step_current (graph : Graph n) (progress : Fin n → Rat) (state : State n)
    (node : Fin n) (current : Current graph progress state)
    (dependenciesReady : ∀ dep ∈ graph.dependencies node, dep ∈ state.ready) :
    Current graph progress (step graph progress state node) := by
  intro other ready
  by_cases same : other = node
  · subst other
    simp only [step, ↓reduceIte]
    rw [value]
    congr 1
    apply List.map_congr_left
    intro dep _
    exact current dep.val (dependenciesReady dep.val dep.property)
  · simp only [step, ite_eq_right same]
    apply current other
    simp only [step, List.mem_cons] at ready
    exact ready.resolve_left same

theorem run_current (graph : Graph n) (progress : Fin n → Rat) (tasks : List (Fin n))
    (state : State n) (current : Current graph progress state)
    (order : admitted graph state.ready tasks = true) :
    Current graph progress (run graph progress state tasks) := by
  induction tasks generalizing state with
  | nil => exact current
  | cons node rest ih =>
    have pair := Bool.and_eq_true_iff.mp order
    apply ih
    · apply step_current graph progress state node current
      intro dep member
      exact of_decide_eq_true ((List.all_eq_true.mp pair.1) dep member)
    · exact pair.2

theorem run_ready (graph : Graph n) (progress : Fin n → Rat) (tasks : List (Fin n))
    (state : State n) (node : Fin n) :
    node ∈ (run graph progress state tasks).ready ↔ node ∈ tasks ∨ node ∈ state.ready := by
  induction tasks generalizing state with
  | nil => simp [run]
  | cons first rest ih =>
    simp only [run, ih, step, List.mem_cons]
    grind

def beginSample (cache : Fin n → Rat) : State n := ⟨cache, []⟩

theorem admitted_node_correct (graph : Graph n) (progress : Fin n → Rat)
    (tasks : List (Fin n)) (cache : Fin n → Rat)
    (order : admitted graph [] tasks = true) (node : Fin n) (present : node ∈ tasks) :
    (run graph progress (beginSample cache) tasks).cache node = value graph progress node := by
  apply run_current graph progress tasks (beginSample cache)
  · intro i member
    simp [beginSample] at member
  · exact order
  · exact (run_ready graph progress tasks (beginSample cache) node).mpr (Or.inl present)

theorem complete_sample_correct (graph : Graph n) (progress : Fin n → Rat)
    (tasks : List (Fin n)) (cache : Fin n → Rat)
    (order : admitted graph [] tasks = true) (complete : ∀ node, node ∈ tasks) :
    (run graph progress (beginSample cache) tasks).cache = value graph progress := by
  funext node
  exact admitted_node_correct graph progress tasks cache order node (complete node)

theorem evaluation_order_independent (graph : Graph n) (progress : Fin n → Rat)
    (left right : List (Fin n)) (oldLeft oldRight : Fin n → Rat)
    (leftOrder : admitted graph [] left = true) (rightOrder : admitted graph [] right = true)
    (leftComplete : ∀ node, node ∈ left) (rightComplete : ∀ node, node ∈ right) :
    (run graph progress (beginSample oldLeft) left).cache =
      (run graph progress (beginSample oldRight) right).cache := by
  rw [complete_sample_correct graph progress left oldLeft leftOrder leftComplete,
      complete_sample_correct graph progress right oldRight rightOrder rightComplete]

structure Plan (graph : Graph n) where
  progress : Fin n → Rat
  tasks : List (Fin n)
  ordered : admitted graph [] tasks = true
  complete : ∀ node, node ∈ tasks

def history (graph : Graph n) : (Fin n → Rat) → List (Plan graph) → List (Fin n → Rat)
  | _, [] => []
  | cache, plan :: rest =>
    let fresh := (run graph plan.progress (beginSample cache) plan.tasks).cache
    fresh :: history graph fresh rest

theorem history_correct (graph : Graph n) (plans : List (Plan graph)) (cache : Fin n → Rat) :
    history graph cache plans = plans.map (fun plan => value graph plan.progress) := by
  induction plans generalizing cache with
  | nil => rfl
  | cons plan rest ih =>
    simp only [history, List.map_cons]
    rw [complete_sample_correct graph plan.progress plan.tasks cache plan.ordered plan.complete]
    rw [ih]

end KeyframeGraph
