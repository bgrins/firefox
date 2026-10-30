import Std

namespace Dag

structure Graph (n : Nat) (V : Type) where
  deps : Fin n → List (Fin n)
  rule : Fin n → List V → V
  rank : Fin n → Nat
  lower : ∀ i j, j ∈ deps i → rank j < rank i

structure State (n : Nat) (V : Type) where
  value : Fin n → V
  dirty : Fin n → Bool

def eval (g : Graph n V) (v : Fin n → V) (i : Fin n) : V :=
  g.rule i ((g.deps i).map v)

def values (g : Graph n V) (s : State n V) (i : Fin n) : V :=
  if s.dirty i then eval g s.value i else s.value i

def round [DecidableEq V] (g : Graph n V) (s : State n V) : State n V :=
  { value := values g s
    dirty := fun i => (g.deps i).any (fun j => decide (values g s j ≠ s.value j)) }

def initial (v : Fin n → V) : State n V := ⟨v, fun _ => true⟩

def run [DecidableEq V] (g : Graph n V) : Nat → State n V → State n V
  | 0, s => s
  | k + 1, s => round g (run g k s)

def Covered (g : Graph n V) (s : State n V) : Prop :=
  ∀ i, s.value i ≠ eval g s.value i → s.dirty i = true

def Ready (s : State n V) : Prop := ∀ i, s.dirty i = false

def Consistent (g : Graph n V) (s : State n V) : Prop :=
  ∀ i, s.value i = eval g s.value i

theorem eval_ext (g : Graph n V) (a b : Fin n → V) (i : Fin n)
    (same : ∀ j, j ∈ g.deps i → a j = b j) : eval g a i = eval g b i := by
  unfold eval
  congr 1
  exact List.map_congr_left same

theorem initial_covered (g : Graph n V) (v : Fin n → V) :
    Covered g (initial v) := by
  intro i _
  rfl

theorem round_covered [DecidableEq V] (g : Graph n V) (s : State n V)
    (covered : Covered g s) : Covered g (round g s) := by
  intro i wrong
  by_cases queued : (round g s).dirty i = true
  · exact queued
  have depsSame : ∀ j, j ∈ g.deps i → values g s j = s.value j := by
    intro j mem
    by_cases same : values g s j = s.value j
    · exact same
    · exact False.elim (queued (List.any_eq_true.mpr ⟨j, mem, by simpa using same⟩))
  have evalSame := eval_ext g (values g s) s.value i depsSame
  have valueCorrect : values g s i = eval g s.value i := by
    by_cases dirty : s.dirty i = true
    · simp [values, dirty]
    · have same : s.value i = eval g s.value i := by
        by_cases good : s.value i = eval g s.value i
        · exact good
        · exact False.elim (dirty (covered i good))
      simp [values, dirty, same]
  exact False.elim (wrong (valueCorrect.trans evalSame.symm))

theorem ready_consistent (g : Graph n V) (s : State n V)
    (covered : Covered g s) (ready : Ready s) : Consistent g s := by
  classical
  intro i
  by_cases good : s.value i = eval g s.value i
  · exact good
  · have := covered i good
    simp [ready i] at this

theorem changed_was_dirty [DecidableEq V] (g : Graph n V) (s : State n V)
    (i : Fin n) (changed : (round g s).value i ≠ s.value i) : s.dirty i = true := by
  by_cases dirty : s.dirty i = true
  · exact dirty
  · exact False.elim (changed (by simp [round, values, dirty]))

def Frontier (g : Graph n V) (k : Nat) (s : State n V) : Prop :=
  ∀ i, s.dirty i = true → k ≤ g.rank i

theorem round_frontier [DecidableEq V] (g : Graph n V) (s : State n V)
    (frontier : Frontier g k s) : Frontier g (k + 1) (round g s) := by
  intro i dirty
  obtain ⟨j, mem, changed⟩ := List.any_eq_true.mp dirty
  have changed' : (round g s).value j ≠ s.value j := by simpa [round] using changed
  have old := frontier j (changed_was_dirty g s j changed')
  have lower := g.lower i j mem
  omega

theorem run_covered [DecidableEq V] (g : Graph n V) (s : State n V)
    (covered : Covered g s) (k : Nat) : Covered g (run g k s) := by
  induction k with
  | zero => exact covered
  | succ k ih => exact round_covered g _ ih

theorem run_frontier [DecidableEq V] (g : Graph n V) (s : State n V) (k : Nat) :
    Frontier g k (run g k s) := by
  induction k with
  | zero => intro i _; exact Nat.zero_le _
  | succ k ih => exact round_frontier g _ ih

theorem bounded_completion [DecidableEq V] (g : Graph n V) (s : State n V)
    (covered : Covered g s) (bound : ∀ i, g.rank i ≤ height) :
    Ready (run g (height + 1) s) ∧ Consistent g (run g (height + 1) s) := by
  have ready : Ready (run g (height + 1) s) := by
    intro i
    have f := run_frontier g s (height + 1) i
    have b := bound i
    cases h : (run g (height + 1) s).dirty i
    · rfl
    · have := f h; omega
  exact ⟨ready, ready_consistent g _ (run_covered g s covered _) ready⟩

theorem ready_value_unchanged [DecidableEq V] (g : Graph n V) (s : State n V)
    (ready : Ready s) : (round g s).value = s.value := by
  funext i
  simp [round, values, ready i]

theorem ready_stays_ready [DecidableEq V] (g : Graph n V) (s : State n V)
    (ready : Ready s) : Ready (round g s) := by
  intro i
  change (g.deps i).any (fun j => decide (values g s j ≠ s.value j)) = false
  have unchanged : ∀ j, values g s j = s.value j := by
    intro j
    simp [values, ready j]
  simp [unchanged]

theorem consistent_unique (g : Graph n V) (a b : State n V)
    (ha : Consistent g a) (hb : Consistent g b) : a.value = b.value := by
  have ranked : ∀ k i, g.rank i < k → a.value i = b.value i := by
    intro k
    induction k with
    | zero => intro i impossible; omega
    | succ k ih =>
      intro i bound
      rw [ha i, hb i]
      apply eval_ext
      intro j mem
      apply ih
      have lower := g.lower i j mem
      omega
  funext i
  exact ranked (g.rank i + 1) i (by omega)

theorem arbitrary_initial_completion [DecidableEq V] (g : Graph n V)
    (v : Fin n → V) (bound : ∀ i, g.rank i ≤ height) :
    Ready (run g (height + 1) (initial v)) ∧
    Consistent g (run g (height + 1) (initial v)) :=
  bounded_completion g _ (initial_covered g v) bound

def edit (g : Graph n V) (nodes : List (Fin n))
    (replacement : Fin n → List V → V) : Graph n V :=
  { g with rule := fun i => if i ∈ nodes then replacement i else g.rule i }

def admit (s : State n V) (nodes : List (Fin n)) : State n V :=
  { s with dirty := fun i => decide (i ∈ nodes) }

theorem edit_admission_covered (g : Graph n V) (s : State n V)
    (consistent : Consistent g s) (nodes : List (Fin n))
    (replacement : Fin n → List V → V) :
    Covered (edit g nodes replacement) (admit s nodes) := by
  intro i wrong
  by_cases changed : i ∈ nodes
  · simp [admit, changed]
  · exact False.elim (wrong (by simpa [admit, eval, edit, changed] using consistent i))

theorem incremental_completion [DecidableEq V] (g : Graph n V) (s : State n V)
    (consistent : Consistent g s) (nodes : List (Fin n))
    (replacement : Fin n → List V → V) (bound : ∀ i, g.rank i ≤ height) :
    Ready (run (edit g nodes replacement) (height + 1) (admit s nodes)) ∧
    Consistent (edit g nodes replacement)
      (run (edit g nodes replacement) (height + 1) (admit s nodes)) :=
  bounded_completion _ _ (edit_admission_covered g s consistent nodes replacement) bound

def diamond : Graph 4 Nat where
  deps := fun i => match i.val with
    | 0 => []
    | 1 => [0]
    | 2 => [0]
    | _ => [1, 2]
  rule := fun i inputs => match i.val with
    | 0 => 2
    | 1 => 3 * inputs.sum
    | 2 => inputs.sum + 1
    | _ => inputs.sum
  rank := fun i => match i.val with
    | 0 => 0
    | 1 => 1
    | 2 => 1
    | _ => 2
  lower := by decide

def diamondInitial : State 4 Nat := initial (fun _ => 0)

def observed (s : State 4 Nat) : List Nat :=
  [s.value 0, s.value 1, s.value 2, s.value 3]

theorem diamond_three_rounds :
    observed (run diamond 1 diamondInitial) = [2, 0, 1, 0] ∧
    observed (run diamond 2 diamondInitial) = [2, 6, 3, 1] ∧
    observed (run diamond 3 diamondInitial) = [2, 6, 3, 9] ∧
    Ready (run diamond 3 diamondInitial) ∧
    Consistent diamond (run diamond 3 diamondInitial) := by
  simp only [Ready, Consistent]
  decide

theorem diamond_late_work :
    (run diamond 2 diamondInitial).dirty 0 = false ∧
    (run diamond 2 diamondInitial).dirty 1 = false ∧
    (run diamond 2 diamondInitial).dirty 2 = false ∧
    (run diamond 2 diamondInitial).dirty 3 = true ∧
    (run diamond 2 diamondInitial).value 3 = 1 ∧
    eval diamond (run diamond 2 diamondInitial).value 3 = 9 := by decide

def discarded : State 4 Nat := ⟨fun _ => 0, fun _ => false⟩

theorem uncovered_empty_is_not_consistent :
    Ready discarded ∧ ¬ Consistent diamond discarded ∧
    observed (run diamond 3 discarded) = [0, 0, 0, 0] := by
  simp only [Ready, Consistent]
  decide

theorem diamond_both_inputs_matter :
    diamond.rule 3 [6, 3] = 9 ∧ diamond.rule 3 [6, 0] = 6 ∧
    diamond.rule 3 [0, 3] = 3 := by decide

def withUnrelated (g : Graph n V) [DecidableEq V]
    (s : State n V × Bool) : State n V × Bool := (round g s.1, s.2)

theorem unrelated_pending_preserved :
    (withUnrelated diamond (run diamond 3 diamondInitial, true)).2 = true ∧
    Ready (withUnrelated diamond (run diamond 3 diamondInitial, true)).1 ∧
    Consistent diamond (withUnrelated diamond (run diamond 3 diamondInitial, true)).1 := by
  simp only [Ready, Consistent]
  decide

def settled : State 4 Nat := run diamond 3 diamondInitial

def editedDiamond : Graph 4 Nat := edit diamond [0] (fun _ _ => 4)

def incremental : State 4 Nat := admit settled [0]

theorem incremental_diamond :
    Consistent diamond settled ∧
    incremental.dirty 0 = true ∧ incremental.dirty 1 = false ∧
    incremental.dirty 2 = false ∧ incremental.dirty 3 = false ∧
    Covered editedDiamond incremental ∧
    observed (run editedDiamond 1 incremental) = [4, 6, 3, 9] ∧
    observed (run editedDiamond 2 incremental) = [4, 12, 5, 9] ∧
    observed (run editedDiamond 3 incremental) = [4, 12, 5, 17] ∧
    Ready (run editedDiamond 3 incremental) ∧
    Consistent editedDiamond (run editedDiamond 3 incremental) := by
  simp only [Ready, Consistent, Covered]
  decide

theorem missed_admission_stays_stale :
    Ready settled ∧ ¬ Covered editedDiamond settled ∧
    observed (run editedDiamond 3 settled) = [2, 6, 3, 9] ∧
    ¬ Consistent editedDiamond (run editedDiamond 3 settled) := by
  simp only [Ready, Consistent, Covered]
  decide

def branchEdit : Graph 4 Nat := edit diamond [2] (fun _ _ => 8)

def branchAdmission : State 4 Nat := admit settled [2]

def firstDependencyOnly [DecidableEq V] (g : Graph n V) (s : State n V) : State n V :=
  { value := values g s
    dirty := fun i => ((g.deps i).take 1).any (fun j => decide (values g s j ≠ s.value j)) }

theorem missing_second_dependency_loses_coverage :
    Covered branchEdit branchAdmission ∧
    observed (round branchEdit branchAdmission) = [2, 6, 8, 9] ∧
    (round branchEdit branchAdmission).dirty 3 = true ∧
    Ready (firstDependencyOnly branchEdit branchAdmission) ∧
    ¬ Covered branchEdit (firstDependencyOnly branchEdit branchAdmission) ∧
    observed (run branchEdit 2 branchAdmission) = [2, 6, 8, 14] := by
  simp only [Ready, Covered]
  decide

end Dag
