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
    by_contra changed
    apply queued
    exact List.any_eq_true.mpr ⟨j, mem, by simpa using changed⟩
  have evalSame := eval_ext g (values g s) s.value i depsSame
  have valueCorrect : values g s i = eval g s.value i := by
    by_cases dirty : s.dirty i = true
    · simp [values, dirty]
    · have same : s.value i = eval g s.value i := by
        by_contra bad
        exact dirty (covered i bad)
      simp [values, dirty, same]
  exact False.elim (wrong (valueCorrect.trans evalSame.symm))

theorem ready_consistent (g : Graph n V) (s : State n V)
    (covered : Covered g s) (ready : Ready s) : Consistent g s := by
  intro i
  by_contra wrong
  have := covered i wrong
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

end Dag
