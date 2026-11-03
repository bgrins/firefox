import Application

namespace CoalescedChain

open EndpointApplication (Version)
abbrev Compute := Nat → Nat → Nat

structure Node where
  endpoint : Version
  installed : Version
  refresh : Bool
  queued : Bool
  inflight : Option Version
  deriving DecidableEq, Repr

def localValid (n : Node) : Prop :=
  n.installed.generation ≤ n.endpoint.generation ∧
  (∀ job, n.inflight = some job → job.generation ≤ n.endpoint.generation ∧
    (job.generation = n.endpoint.generation → job = n.endpoint)) ∧
  (n.installed = n.endpoint ∨ n.queued = true ∨ n.inflight = some n.endpoint)

def coherent (parent : Nat) (compute : Compute) (offset : Nat) : List Node → Prop
  | [] => True
  | n :: rest => localValid n ∧
      (n.refresh = false → n.endpoint.value = compute offset parent) ∧
      coherent n.installed.value compute (offset + 1) rest

def refreshNode (value : Nat) (n : Node) : Node :=
  if value = n.endpoint.value then { n with refresh := false } else
    { n with endpoint := ⟨n.endpoint.generation + 1, value⟩,
             refresh := false, queued := true }

def selectNode (n : Node) : Node :=
  { n with queued := false, inflight := some n.endpoint }

def completeNode (n : Node) : Node :=
  match n.inflight with
  | none => n
  | some job =>
    if job.generation = n.endpoint.generation then
      { n with installed := job, inflight := none }
    else { n with inflight := none }

def markFirst : List Node → List Node
  | [] => []
  | n :: rest => { n with refresh := true } :: rest

def downstream (old new : Nat) (rest : List Node) : List Node :=
  if new = old then rest else markFirst rest

inductive Step : Nat → Compute → Nat → List Node → List Node → Prop
  | refresh {parent : Nat} {compute : Compute} {offset : Nat} (n rest) (pending : n.refresh = true) :
      Step parent compute offset (n :: rest) (refreshNode (compute offset parent) n :: rest)
  | select {parent : Nat} {compute : Compute} {offset : Nat} (n rest) (pending : n.queued = true) (free : n.inflight = none) :
      Step parent compute offset (n :: rest) (selectNode n :: rest)
  | complete {parent : Nat} {compute : Compute} {offset : Nat} (n rest job) (pending : n.inflight = some job) :
      Step parent compute offset (n :: rest)
        (completeNode n :: downstream n.installed.value (completeNode n).installed.value rest)
  | descendant {parent : Nat} {compute : Compute} {offset : Nat} (n rest next) (step : Step n.installed.value compute (offset + 1) rest next) :
      Step parent compute offset (n :: rest) (n :: next)

def localWeight (remaining : Nat) (n : Node) : Nat :=
  (if n.refresh then 3 * remaining else 0) +
  (if n.queued then 3 * remaining - 1 else 0) +
  (if n.inflight.isSome then 3 * remaining - 2 else 0)

def weight : List Node → Nat
  | [] => 0
  | n :: rest => localWeight (rest.length + 1) n + weight rest

def quiet (n : Node) : Prop := n.refresh = false ∧ n.queued = false ∧ n.inflight = none

def allQuiet : List Node → Prop
  | [] => True
  | n :: rest => quiet n ∧ allQuiet rest

def expected (parent : Nat) (compute : Compute) (offset : Nat) : Nat → List Nat
  | 0 => []
  | count + 1 => compute offset parent :: expected (compute offset parent) compute (offset + 1) count

theorem refresh_valid (n : Node) (value : Nat) (h : localValid n) :
    localValid (refreshNode value n) := by
  rcases h with ⟨installed, jobs, coverage⟩
  by_cases same : value = n.endpoint.value
  · simpa [refreshNode, same, localValid] using And.intro installed (And.intro jobs coverage)
  · simp only [refreshNode, same, ↓reduceIte, localValid]
    refine ⟨by omega, ?_, Or.inr (Or.inl trivial)⟩
    intro job pending
    have old := (jobs job pending).1
    exact ⟨by omega, by intro impossible; omega⟩

theorem refresh_value (n : Node) (value : Nat) :
    (refreshNode value n).endpoint.value = value ∧
    (refreshNode value n).installed = n.installed := by
  by_cases same : value = n.endpoint.value <;> simp [refreshNode, same]

theorem select_valid (n : Node) (h : localValid n) : localValid (selectNode n) := by
  refine ⟨h.1, ?_, Or.inr (Or.inr rfl)⟩
  intro job pending
  have same : job = n.endpoint := by simpa [selectNode] using pending.symm
  subst job
  exact ⟨Nat.le_refl _, fun _ => rfl⟩

theorem complete_valid (n : Node) (h : localValid n) : localValid (completeNode n) := by
  cases pending : n.inflight with
  | none => simpa [completeNode, pending] using h
  | some job =>
    have good := h.2.1 job pending
    by_cases current : job.generation = n.endpoint.generation
    · have same := good.2 current
      simp [completeNode, pending, same, localValid]
    · simp only [completeNode, pending, current, ↓reduceIte, localValid]
      refine ⟨h.1, ?_, ?_⟩
      · intro other impossible
        contradiction
      · rcases h.2.2 with installed | queued | active
        · exact Or.inl installed
        · exact Or.inr (Or.inl queued)
        · have same : job = n.endpoint := by simpa [pending] using active
          exact False.elim (current (congrArg Version.generation same))

theorem complete_endpoint_refresh_unchanged (n : Node) :
    (completeNode n).endpoint = n.endpoint ∧ (completeNode n).refresh = n.refresh := by
  cases pending : n.inflight with
  | none => simp [completeNode, pending]
  | some job =>
    by_cases current : job.generation = n.endpoint.generation <;> simp [completeNode, pending, current]

theorem downstream_coherent (old new : Nat) (compute : Compute) (offset : Nat)
    (nodes : List Node) (h : coherent old compute offset nodes) :
    coherent new compute offset (downstream old new nodes) := by
  by_cases same : new = old
  · simpa [downstream, same] using h
  · simp only [downstream, same, ↓reduceIte]
    cases nodes with
    | nil => trivial
    | cons n rest =>
      exact ⟨h.1, by simp, h.2.2⟩

theorem step_coherent {parent : Nat} {compute : Compute} {offset : Nat}
    {before after : List Node} (step : Step parent compute offset before after)
    (h : coherent parent compute offset before) : coherent parent compute offset after := by
  induction step with
  | refresh n rest pending =>
    refine ⟨refresh_valid n _ h.1, fun _ => (refresh_value n _).1, ?_⟩
    simpa only [(refresh_value n _).2] using h.2.2
  | select n rest pending free => exact ⟨select_valid n h.1, h.2.1, h.2.2⟩
  | complete n rest job pending =>
    refine ⟨complete_valid n h.1, ?_, downstream_coherent _ _ _ _ _ h.2.2⟩
    simpa only [(complete_endpoint_refresh_unchanged n).1,
      (complete_endpoint_refresh_unchanged n).2] using h.2.1
  | descendant n rest next step ih => exact ⟨h.1, h.2.1, ih h.2.2⟩

theorem downstream_length (old new : Nat) (nodes : List Node) :
    (downstream old new nodes).length = nodes.length := by
  by_cases same : new = old <;> cases nodes <;> simp [downstream, same, markFirst]

theorem step_length {parent : Nat} {compute : Compute} {offset : Nat}
    {before after : List Node} (step : Step parent compute offset before after) :
    after.length = before.length := by
  induction step with
  | refresh => rfl
  | select => rfl
  | complete n rest job pending => simp [downstream_length]
  | descendant n rest next step ih => simp [ih]

theorem refresh_weight (m : Nat) (positive : 0 < m) (n : Node) (value : Nat)
    (pending : n.refresh = true) :
    localWeight m (refreshNode value n) < localWeight m n := by
  by_cases same : value = n.endpoint.value <;>
    simp only [refreshNode, same, ↓reduceIte, localWeight, pending, Bool.false_eq_true, ↓reduceIte] <;> omega

theorem select_weight (m : Nat) (positive : 0 < m) (n : Node)
    (pending : n.queued = true) (free : n.inflight = none) :
    localWeight m (selectNode n) < localWeight m n := by
  cases refresh : n.refresh <;> simp [selectNode, localWeight, pending, free, refresh] <;> omega

theorem complete_weight (m : Nat) (n : Node) (job : Version)
    (pending : n.inflight = some job) :
    localWeight m (completeNode n) + (3 * m - 2) = localWeight m n := by
  by_cases current : job.generation = n.endpoint.generation <;>
    simp [completeNode, localWeight, pending, current]

theorem downstream_weight (old new : Nat) (nodes : List Node) :
    weight (downstream old new nodes) ≤ weight nodes + 3 * nodes.length := by
  by_cases same : new = old
  · simp [downstream, same]
  · cases nodes with
    | nil => simp [downstream, same, markFirst, weight]
    | cons n rest =>
      simp only [downstream, same, ↓reduceIte, markFirst, weight, localWeight, List.length_cons]
      cases n.refresh <;> simp <;> omega

theorem step_decreases {parent : Nat} {compute : Compute} {offset : Nat}
    {before after : List Node} (step : Step parent compute offset before after) :
    weight after < weight before := by
  induction step with
  | refresh n rest pending =>
    exact Nat.add_lt_add_right (refresh_weight _ (by omega) n _ pending) _
  | select n rest pending free =>
    exact Nat.add_lt_add_right (select_weight _ (by omega) n pending free) _
  | complete n rest job pending =>
    have spent := complete_weight (rest.length + 1) n job pending
    have added := downstream_weight n.installed.value (completeNode n).installed.value rest
    simp only [weight, downstream_length]
    omega
  | descendant n rest next step ih =>
    have same := step_length step
    simp only [weight, same]
    exact Nat.add_lt_add_left ih _

theorem quiet_dependency_values (parent : Nat) (compute : Compute) (offset : Nat)
    (nodes : List Node) (h : coherent parent compute offset nodes) (done : allQuiet nodes) :
    nodes.map (fun n => n.installed.value) = expected parent compute offset nodes.length := by
  induction nodes generalizing parent offset with
  | nil => rfl
  | cons n rest ih =>
    have installed : n.installed = n.endpoint := by
      rcases h.1.2.2 with same | queued | active
      · exact same
      · simp [done.1.2.1] at queued
      · simp [done.1.2.2] at active
    have value : n.installed.value = compute offset parent := by
      rw [installed]
      exact h.2.1 done.1.1
    simp only [List.map_cons, List.length_cons, expected]
    rw [←value]
    exact congrArg (List.cons n.installed.value) (ih _ _ h.2.2 done.2)

theorem progress (parent : Nat) (compute : Compute) (offset : Nat) (nodes : List Node) :
    allQuiet nodes ∨ ∃ next, Step parent compute offset nodes next := by
  induction nodes generalizing parent offset with
  | nil => exact Or.inl trivial
  | cons n rest ih =>
    cases refresh : n.refresh with
    | true => exact Or.inr ⟨_, Step.refresh n rest refresh⟩
    | false =>
      cases active : n.inflight with
      | some job => exact Or.inr ⟨_, Step.complete n rest job active⟩
      | none =>
        cases queued : n.queued with
        | true => exact Or.inr ⟨_, Step.select n rest queued active⟩
        | false =>
          rcases ih n.installed.value (offset + 1) with done | ⟨next, step⟩
          · exact Or.inl ⟨⟨refresh, queued, active⟩, done⟩
          · exact Or.inr ⟨_, Step.descendant n rest next step⟩

inductive History (parent : Nat) (compute : Compute) (offset : Nat) : Nat → List Node → List Node → Prop
  | zero (nodes) : History parent compute offset 0 nodes nodes
  | next {count before middle after} (step : Step parent compute offset before middle)
      (rest : History parent compute offset count middle after) :
      History parent compute offset (count + 1) before after

theorem history_budget {parent : Nat} {compute : Compute} {offset count : Nat}
    {before after : List Node} (history : History parent compute offset count before after) :
    weight after + count ≤ weight before := by
  induction history with
  | zero => omega
  | next step rest ih => have decreases := step_decreases step; omega

theorem history_coherent {parent : Nat} {compute : Compute} {offset count : Nat}
    {before after : List Node} (history : History parent compute offset count before after)
    (h : coherent parent compute offset before) : coherent parent compute offset after := by
  induction history with
  | zero => exact h
  | next step rest ih => exact ih (step_coherent step h)

theorem stopped_values {parent : Nat} {compute : Compute} {offset count : Nat}
    {before after : List Node} (history : History parent compute offset count before after)
    (h : coherent parent compute offset before)
    (stopped : ¬∃ next, Step parent compute offset after next) :
    after.map (fun n => n.installed.value) = expected parent compute offset after.length := by
  have done : allQuiet after := (progress parent compute offset after).resolve_right stopped
  exact quiet_dependency_values _ _ _ _ (history_coherent history h) done

theorem finite_settlement (parent : Nat) (compute : Compute) (offset : Nat)
    (nodes : List Node) :
    ∃ count after, History parent compute offset count nodes after ∧
      allQuiet after ∧ count ≤ weight nodes := by
  have terminate : ∀ budget, ∀ before : List Node, weight before = budget →
      ∃ count after, History parent compute offset count before after ∧
        allQuiet after ∧ count ≤ weight before := by
    intro budget
    induction budget using Nat.strongRecOn with
    | ind budget ih =>
      intro before bound
      rcases progress parent compute offset before with done | ⟨next, step⟩
      · exact ⟨0, before, History.zero before, done, Nat.zero_le _⟩
      · have lower : weight next < budget := by
          have decrease := step_decreases step
          omega
        rcases ih (weight next) lower next rfl with ⟨count, after, history, done, _⟩
        have combined := History.next step history
        have limit := history_budget combined
        exact ⟨count + 1, after, combined, done, by omega⟩
  exact terminate (weight nodes) nodes rfl

theorem finite_ready (parent : Nat) (compute : Compute) (offset : Nat)
    (nodes : List Node) (h : coherent parent compute offset nodes) :
    ∃ count after, History parent compute offset count nodes after ∧
      allQuiet after ∧ count ≤ weight nodes ∧
      after.map (fun n => n.installed.value) = expected parent compute offset after.length := by
  rcases finite_settlement parent compute offset nodes with ⟨count, after, history, done, bound⟩
  exact ⟨count, after, history, done, bound,
    quiet_dependency_values _ _ _ _ (history_coherent history h) done⟩

def pending64 : Node := ⟨⟨1, 64⟩, ⟨0, 46⟩, false, true, none⟩
def selected64 : Node := selectNode pending64
def newer80 : Node := refreshNode 80 { selected64 with refresh := true }
def afterStale : Node := completeNode newer80

def double (_ : Nat) (value : Nat) : Nat := 2 * value
def parentPending : Node := ⟨⟨1, 2⟩, ⟨0, 0⟩, false, false, some ⟨1, 2⟩⟩
def childOld : Node := ⟨⟨0, 0⟩, ⟨0, 0⟩, false, false, none⟩
def droppedChild : List Node := [completeNode parentPending, childOld]

theorem selected_is_not_installed :
    selected64.queued = false ∧ selected64.inflight = some selected64.endpoint ∧
    selected64.installed.value = 46 ∧ selected64.endpoint.value = 64 := by
  decide +kernel

theorem stale_completion_preserves_newest :
    afterStale.queued = true ∧ afterStale.inflight = none ∧
    afterStale.installed.value = 46 ∧ afterStale.endpoint.value = 80 ∧
    (completeNode (selectNode afterStale)).installed.value = 80 := by
  decide +kernel

theorem unchanged_refresh_keeps_application :
    (refreshNode 64 { pending64 with refresh := true }).queued = true := by
  decide +kernel

theorem sample_dependency_coherent : coherent 1 double 0 [parentPending, childOld] := by
  simp [coherent, localValid, parentPending, childOld, double]

theorem real_change_marks_child :
    downstream parentPending.installed.value (completeNode parentPending).installed.value
      [childOld] = [{ childOld with refresh := true }] := by
  decide +kernel

theorem dropped_work_counterexample :
    droppedChild.map (fun n => n.installed.value) = [2, 0] ∧
    expected 1 double 0 droppedChild.length = [2, 4] := by
  decide +kernel

end CoalescedChain
