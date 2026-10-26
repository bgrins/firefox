import Graph

namespace KeyframeGraph

def rankMaximum (graph : Graph n) : List (Fin n) → Nat
  | [] => 0
  | node :: rest => max (graph.rank node) (rankMaximum graph rest)

theorem rank_le_maximum (graph : Graph n) (nodes : List (Fin n))
    (node : Fin n) (member : node ∈ nodes) :
    graph.rank node ≤ rankMaximum graph nodes := by
  induction nodes with
  | nil => simp at member
  | cons first rest ih =>
    rcases List.mem_cons.mp member with same | later
    · subst node
      exact Nat.le_max_left _ _
    · exact Nat.le_trans (ih later) (Nat.le_max_right _ _)

def rankLayers (graph : Graph n) : Nat → List (Fin n)
  | 0 => []
  | height + 1 => rankLayers graph height ++
      (List.finRange n).filter (fun node => decide (graph.rank node = height))

theorem mem_rankLayers (graph : Graph n) (height : Nat) (node : Fin n) :
    node ∈ rankLayers graph height ↔ graph.rank node < height := by
  induction height with
  | zero => simp [rankLayers]
  | succ height ih =>
    simp only [rankLayers, List.mem_append, ih, List.mem_filter]
    simp only [List.mem_finRange, decide_eq_true_eq, true_and]
    omega

theorem admitted_ready (graph : Graph n) (tasks ready : List (Fin n))
    (available : ∀ node ∈ tasks, ∀ dep ∈ graph.dependencies node, dep ∈ ready) :
    admitted graph ready tasks = true := by
  induction tasks generalizing ready with
  | nil => rfl
  | cons node rest ih =>
    apply Bool.and_eq_true_iff.mpr
    constructor
    · apply List.all_eq_true.mpr
      intro dep member
      exact decide_eq_true (available node (by simp) dep member)
    · apply ih
      intro next member dep dependency
      exact List.mem_cons_of_mem node (available next (by simp [member]) dep dependency)

theorem admitted_append (graph : Graph n) (first rest ready : List (Fin n))
    (left : admitted graph ready first = true)
    (right : admitted graph (first.reverse ++ ready) rest = true) :
    admitted graph ready (first ++ rest) = true := by
  induction first generalizing ready with
  | nil => simpa using right
  | cons node tail ih =>
    have pair := Bool.and_eq_true_iff.mp left
    apply Bool.and_eq_true_iff.mpr
    constructor
    · exact pair.1
    · apply ih (node :: ready) pair.2
      simpa [List.reverse_cons, List.append_assoc] using right

theorem rankLayers_admitted (graph : Graph n) (height : Nat) :
    admitted graph [] (rankLayers graph height) = true := by
  induction height with
  | zero => rfl
  | succ height ih =>
    apply admitted_append graph _ _ [] ih
    apply admitted_ready
    intro node member dep dependency
    have rank : graph.rank node = height := by
      simpa using (List.mem_filter.mp member).2
    have lower : graph.rank dep < height := by
      simpa [rank] using graph.lower node dep dependency
    have present := (mem_rankLayers graph height dep).mpr lower
    simpa using present

def schedule (graph : Graph n) : List (Fin n) :=
  rankLayers graph (rankMaximum graph (List.finRange n) + 1)

theorem schedule_admitted (graph : Graph n) :
    admitted graph [] (schedule graph) = true := rankLayers_admitted graph _

theorem schedule_complete (graph : Graph n) (node : Fin n) :
    node ∈ schedule graph := by
  apply (mem_rankLayers graph _ node).mpr
  exact Nat.lt_succ_of_le (rank_le_maximum graph (List.finRange n) node (by simp))

theorem constructed_sample_correct (graph : Graph n) (progress : Fin n → Rat)
    (cache : Fin n → Rat) :
    (run graph progress (beginSample cache) (schedule graph)).cache = value graph progress := by
  exact complete_sample_correct graph progress (schedule graph) cache
    (schedule_admitted graph) (schedule_complete graph)

def scheduledPlan (graph : Graph n) (progress : Fin n → Rat) : Plan graph :=
  ⟨progress, schedule graph, schedule_admitted graph, schedule_complete graph⟩

theorem constructed_history_correct (graph : Graph n) (samples : List (Fin n → Rat))
    (cache : Fin n → Rat) :
    history graph cache (samples.map (scheduledPlan graph)) = samples.map (value graph) := by
  rw [history_correct]
  simp [List.map_map, scheduledPlan]

end KeyframeGraph
