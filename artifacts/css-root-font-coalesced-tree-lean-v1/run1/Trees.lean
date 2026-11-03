import Coalesced

namespace CoalescedTree

open CoalescedChain (Node Compute localValid refreshNode selectNode completeNode localWeight quiet)
open EndpointApplication (Version)

inductive Forest where
  | nil
  | cons (key : Nat) (node : Node) (children siblings : Forest)
  deriving DecidableEq, Repr

inductive Shape where
  | nil
  | cons (key : Nat) (children siblings : Shape)
  deriving DecidableEq, Repr

inductive Values where
  | nil
  | cons (value : Nat) (children siblings : Values)
  deriving DecidableEq, Repr

def shape : Forest → Shape
  | .nil => .nil
  | .cons key _ children siblings => .cons key (shape children) (shape siblings)

def size : Forest → Nat
  | .nil => 0
  | .cons _ _ children siblings => 1 + size children + size siblings

def installed : Forest → Values
  | .nil => .nil
  | .cons _ n children siblings => .cons n.installed.value (installed children) (installed siblings)

def expected (parent : Nat) (compute : Compute) : Shape → Values
  | .nil => .nil
  | .cons key children siblings =>
    let value := compute key parent
    .cons value (expected value compute children) (expected parent compute siblings)

def coherent (parent : Nat) (compute : Compute) : Forest → Prop
  | .nil => True
  | .cons key n children siblings => localValid n ∧
    (n.refresh = false → n.endpoint.value = compute key parent) ∧
    coherent n.installed.value compute children ∧ coherent parent compute siblings

def allQuiet : Forest → Prop
  | .nil => True
  | .cons _ n children siblings => quiet n ∧ allQuiet children ∧ allQuiet siblings

def markRoots : Forest → Forest
  | .nil => .nil
  | .cons key n children siblings =>
    .cons key { n with refresh := true } children (markRoots siblings)

def downstream (old new : Nat) (children : Forest) : Forest :=
  if new = old then children else markRoots children

def weight : Forest → Nat
  | .nil => 0
  | .cons _ n children siblings =>
    localWeight (size children + 1) n + weight children + weight siblings

inductive Step : Nat → Compute → Forest → Forest → Prop
  | refresh {parent compute} (key n children siblings) (pending : n.refresh = true) :
    Step parent compute (.cons key n children siblings)
      (.cons key (refreshNode (compute key parent) n) children siblings)
  | select {parent compute} (key n children siblings)
      (pending : n.queued = true) (free : n.inflight = none) :
    Step parent compute (.cons key n children siblings)
      (.cons key (selectNode n) children siblings)
  | complete {parent compute} (key n children siblings job) (pending : n.inflight = some job) :
    Step parent compute (.cons key n children siblings)
      (.cons key (completeNode n)
        (downstream n.installed.value (completeNode n).installed.value children) siblings)
  | child {parent compute} (key n children next siblings)
      (step : Step n.installed.value compute children next) :
    Step parent compute (.cons key n children siblings) (.cons key n next siblings)
  | sibling {parent compute} (key n children siblings next)
      (step : Step parent compute siblings next) :
    Step parent compute (.cons key n children siblings) (.cons key n children next)

theorem marked_size (forest : Forest) : size (markRoots forest) = size forest := by
  induction forest with
  | nil => rfl
  | cons key n children siblings ihc ihs => simp [markRoots, size, ihs]

theorem marked_shape (forest : Forest) : shape (markRoots forest) = shape forest := by
  induction forest with
  | nil => rfl
  | cons key n children siblings ihc ihs => simp [markRoots, shape, ihs]

theorem downstream_size (old new : Nat) (forest : Forest) :
    size (downstream old new forest) = size forest := by
  by_cases same : new = old <;> simp [downstream, same, marked_size]

theorem downstream_shape (old new : Nat) (forest : Forest) :
    shape (downstream old new forest) = shape forest := by
  by_cases same : new = old <;> simp [downstream, same, marked_shape]

theorem marked_coherent (old new : Nat) (compute : Compute) (forest : Forest)
    (h : coherent old compute forest) : coherent new compute (markRoots forest) := by
  induction forest with
  | nil => trivial
  | cons key n children siblings ihc ihs =>
    exact ⟨h.1, by simp, h.2.2.1, ihs h.2.2.2⟩

theorem downstream_coherent (old new : Nat) (compute : Compute) (forest : Forest)
    (h : coherent old compute forest) : coherent new compute (downstream old new forest) := by
  by_cases same : new = old
  · simpa [downstream, same] using h
  · simpa [downstream, same] using marked_coherent old new compute forest h

theorem step_coherent {parent compute before after} (step : Step parent compute before after)
    (h : coherent parent compute before) : coherent parent compute after := by
  induction step with
  | refresh key n children siblings pending =>
    refine ⟨CoalescedChain.refresh_valid n _ h.1,
      fun _ => (CoalescedChain.refresh_value n _).1, ?_, h.2.2.2⟩
    simpa only [(CoalescedChain.refresh_value n _).2] using h.2.2.1
  | select key n children siblings pending free =>
    exact ⟨CoalescedChain.select_valid n h.1, h.2.1, h.2.2.1, h.2.2.2⟩
  | complete key n children siblings job pending =>
    refine ⟨CoalescedChain.complete_valid n h.1, ?_,
      downstream_coherent _ _ _ _ h.2.2.1, h.2.2.2⟩
    simpa only [(CoalescedChain.complete_endpoint_refresh_unchanged n).1,
      (CoalescedChain.complete_endpoint_refresh_unchanged n).2] using h.2.1
  | child key n children next siblings step ih =>
    exact ⟨h.1, h.2.1, ih h.2.2.1, h.2.2.2⟩
  | sibling key n children siblings next step ih =>
    exact ⟨h.1, h.2.1, h.2.2.1, ih h.2.2.2⟩

theorem step_size {parent compute before after} (step : Step parent compute before after) :
    size after = size before := by
  induction step with
  | refresh => rfl
  | select => rfl
  | complete => simp [size, downstream_size]
  | child _ _ _ _ _ _ ih => simp [size, ih]
  | sibling _ _ _ _ _ _ ih => simp [size, ih]

theorem step_shape {parent compute before after} (step : Step parent compute before after) :
    shape after = shape before := by
  induction step with
  | refresh => rfl
  | select => rfl
  | complete => simp [shape, downstream_shape]
  | child _ _ _ _ _ _ ih => simp [shape, ih]
  | sibling _ _ _ _ _ _ ih => simp [shape, ih]

theorem marked_weight (forest : Forest) : weight (markRoots forest) ≤ weight forest + 3 * size forest := by
  induction forest with
  | nil => simp [markRoots, weight, size]
  | cons key n children siblings ihc ihs =>
    simp only [markRoots, weight, size, localWeight]
    cases n.refresh <;> simp only [Bool.false_eq_true, Bool.true_eq, ↓reduceIte] <;> omega

theorem downstream_weight (old new : Nat) (forest : Forest) :
    weight (downstream old new forest) ≤ weight forest + 3 * size forest := by
  by_cases same : new = old
  · simp [downstream, same]
  · simpa [downstream, same] using marked_weight forest

theorem step_decreases {parent compute before after} (step : Step parent compute before after) :
    weight after < weight before := by
  induction step with
  | refresh key n children siblings pending =>
    have less := CoalescedChain.refresh_weight (size children + 1) (by omega) n _ pending
    simp only [weight]; omega
  | select key n children siblings pending free =>
    have less := CoalescedChain.select_weight (size children + 1) (by omega) n pending free
    simp only [weight]; omega
  | complete key n children siblings job pending =>
    have spent := CoalescedChain.complete_weight (size children + 1) n job pending
    have added := downstream_weight n.installed.value (completeNode n).installed.value children
    simp only [weight, downstream_size]; omega
  | child key n children next siblings step ih =>
    have same := step_size step
    simp only [weight, same]; omega
  | sibling key n children siblings next step ih =>
    simp only [weight]; omega

theorem quiet_values (parent : Nat) (compute : Compute) (forest : Forest)
    (h : coherent parent compute forest) (done : allQuiet forest) :
    installed forest = expected parent compute (shape forest) := by
  induction forest generalizing parent with
  | nil => rfl
  | cons key n children siblings ihc ihs =>
    have same : n.installed = n.endpoint := by
      rcases h.1.2.2 with same | queued | active
      · exact same
      · simp [done.1.2.1] at queued
      · simp [done.1.2.2] at active
    have value : n.installed.value = compute key parent := by
      rw [same]; exact h.2.1 done.1.1
    have child := ihc n.installed.value h.2.2.1 done.2.1
    have siblings := ihs parent h.2.2.2 done.2.2
    simp only [installed, shape, expected]
    rw [child, siblings, value]

theorem progress (parent : Nat) (compute : Compute) (forest : Forest) :
    allQuiet forest ∨ ∃ next, Step parent compute forest next := by
  induction forest generalizing parent with
  | nil => exact Or.inl trivial
  | cons key n children siblings ihc ihs =>
    cases refresh : n.refresh with
    | true => exact Or.inr ⟨_, Step.refresh key n children siblings refresh⟩
    | false =>
      cases active : n.inflight with
      | some job => exact Or.inr ⟨_, Step.complete key n children siblings job active⟩
      | none =>
        cases queued : n.queued with
        | true => exact Or.inr ⟨_, Step.select key n children siblings queued active⟩
        | false =>
          rcases ihc n.installed.value with childDone | ⟨next, step⟩
          · rcases ihs parent with siblingsDone | ⟨next, step⟩
            · exact Or.inl ⟨⟨refresh, queued, active⟩, childDone, siblingsDone⟩
            · exact Or.inr ⟨_, Step.sibling key n children siblings next step⟩
          · exact Or.inr ⟨_, Step.child key n children next siblings step⟩

inductive History (parent : Nat) (compute : Compute) : Nat → Forest → Forest → Prop
  | zero (forest) : History parent compute 0 forest forest
  | next {count before middle after} (step : Step parent compute before middle)
      (rest : History parent compute count middle after) : History parent compute (count + 1) before after

theorem history_budget {parent compute count before after}
    (history : History parent compute count before after) : weight after + count ≤ weight before := by
  induction history with
  | zero => omega
  | next step rest ih => have less := step_decreases step; omega

theorem history_coherent {parent compute count before after}
    (history : History parent compute count before after) (h : coherent parent compute before) :
    coherent parent compute after := by
  induction history with
  | zero => exact h
  | next step rest ih => exact ih (step_coherent step h)

theorem history_shape {parent compute count before after}
    (history : History parent compute count before after) : shape after = shape before := by
  induction history with
  | zero => rfl
  | next step rest ih => exact ih.trans (step_shape step)

theorem finite_settlement (parent : Nat) (compute : Compute) (forest : Forest) :
    ∃ count after, History parent compute count forest after ∧ allQuiet after ∧ count ≤ weight forest := by
  have terminate : ∀ budget, ∀ before : Forest, weight before = budget →
      ∃ count after, History parent compute count before after ∧ allQuiet after ∧ count ≤ weight before := by
    intro budget
    induction budget using Nat.strongRecOn with
    | ind budget ih =>
      intro before bound
      rcases progress parent compute before with done | ⟨next, step⟩
      · exact ⟨0, before, History.zero before, done, Nat.zero_le _⟩
      · have lower : weight next < budget := by have less := step_decreases step; omega
        rcases ih (weight next) lower next rfl with ⟨count, after, history, done, _⟩
        have combined := History.next step history
        have limit := history_budget combined
        exact ⟨count + 1, after, combined, done, by omega⟩
  exact terminate (weight forest) forest rfl

theorem finite_ready (parent : Nat) (compute : Compute) (forest : Forest)
    (h : coherent parent compute forest) :
    ∃ count after, History parent compute count forest after ∧ allQuiet after ∧ count ≤ weight forest ∧
      installed after = expected parent compute (shape forest) := by
  rcases finite_settlement parent compute forest with ⟨count, after, history, done, bound⟩
  refine ⟨count, after, history, done, bound, ?_⟩
  rw [←history_shape history]
  exact quiet_values _ _ _ (history_coherent history h) done

def oldLeaf : Node := ⟨⟨0, 0⟩, ⟨0, 0⟩, false, false, none⟩
def parentJob : Node := ⟨⟨1, 2⟩, ⟨0, 0⟩, false, false, some ⟨1, 2⟩⟩
def leaves : Forest := .cons 1 oldLeaf .nil (.cons 2 oldLeaf .nil .nil)
def star : Forest := .cons 0 parentJob leaves .nil
def starAfter : Forest := .cons 0 (completeNode parentJob) (markRoots leaves) .nil
def dropped : Forest := .cons 0 (completeNode parentJob) leaves .nil
def double (_ : Nat) (parent : Nat) : Nat := 2 * parent

def height : Forest → Nat
  | .nil => 0
  | .cons _ _ children siblings => max (height children + 1) (height siblings)

def depthWeight : Forest → Nat
  | .nil => 0
  | .cons _ n children siblings =>
    localWeight (height children + 1) n + depthWeight children + depthWeight siblings

theorem branching_step : Step 1 double star starAfter := by
  exact Step.complete 0 parentJob leaves .nil ⟨1, 2⟩ rfl

theorem branching_coherent : coherent 1 double star := by
  simp [coherent, localValid, star, leaves, oldLeaf, parentJob, double]

theorem branching_rank_counterexample :
    depthWeight star = 4 ∧ depthWeight starAfter = 6 ∧ weight star = 7 ∧ weight starAfter = 6 := by
  decide +kernel

theorem dropped_branch_counterexample :
    allQuiet dropped ∧ installed dropped ≠ expected 1 double (shape dropped) := by
  decide +kernel

end CoalescedTree
