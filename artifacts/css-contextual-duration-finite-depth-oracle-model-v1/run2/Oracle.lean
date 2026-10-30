import Completion

namespace Oracle

def parity : Nat → Bool
  | 0 => false
  | n + 1 => !parity n

def bit (i : Nat) (value : Bool) : Bool := value != parity i

def metric (i : Nat) (value : Bool) : Nat := if bit i value then 32 else 16

def duration (input : Nat) : Nat := input * 1000 / 16

def transfer (input : Nat) : Nat := if 1500 < duration input then 16 else 32

def opacity (input : Nat) : Nat := if 1500 < duration input then 0 else 1

def leaf (i : Nat) (value : Bool) : Nat := if bit i value then 1 else 0

def view (s : Completion.State) (i : Nat) : Nat := metric i (s.value i)

theorem exact_endpoints :
    duration 16 = 1000 ∧ duration 32 = 2000 ∧
    transfer 16 = 32 ∧ transfer 32 = 16 ∧ opacity 16 = 1 ∧ opacity 32 = 0 := by decide

theorem parity_transfer (i : Nat) (value : Bool) :
    transfer (metric i value) = metric (i + 1) value := by
  cases value <;> cases h : parity i <;>
    simp [transfer, duration, metric, bit, parity, h]

theorem leaf_is_additional_edge (depth : Nat) (value : Bool) :
    opacity (metric depth value) = leaf (depth + 1) value := by
  cases value <;> cases h : parity depth <;>
    simp [opacity, duration, metric, leaf, bit, parity, h]

theorem selected_evaluation_is_metric_transfer (n i : Nat) (s : Completion.State)
    (selected : s.flight (i + 1) = true) :
    view (Completion.finish n s) (i + 1) = transfer (view s i) := by
  simp only [view, Completion.finish, Completion.evaluated, selected, ite_true, Nat.add_sub_cancel]
  exact (parity_transfer i (s.value i)).symm

theorem initial_encoding (depth : Nat) (u : QueueState.Entry) :
    view (Completion.initial (depth + 1) u) 0 = 32 ∧
    (∀ i, 0 < i → i ≤ depth + 1 →
      view (Completion.initial (depth + 1) u) i = metric i false) := by
  constructor
  · rfl
  · intro i pos _
    have h : i ≠ 0 := by omega
    simp [view, Completion.initial, h]

theorem completed_leaf (depth : Nat) (u : QueueState.Entry) :
    leaf (depth + 1) ((Completion.run (depth + 1) (depth + 1)
      (Completion.initial (depth + 1) u)).value (depth + 1)) =
    opacity (metric depth true) := by
  rw [Completion.run_exact]
  simpa [Completion.canonical] using (leaf_is_additional_edge depth true).symm

theorem bit_distinguishes_generations (i : Nat) : leaf i false ≠ leaf i true := by
  cases h : parity i <;> simp [leaf, bit, h]

theorem incomplete_leaf_witness (depth rounds : Nat) (bounded : rounds < depth + 1) :
    leaf (depth + 1) ((Completion.run (depth + 1) rounds
      (Completion.initial (depth + 1) .absent)).value (depth + 1)) ≠
    opacity (metric depth true) := by
  rw [Completion.run_exact, leaf_is_additional_edge]
  have h : ¬ depth + 1 ≤ rounds := by omega
  simpa [Completion.canonical, h] using bit_distinguishes_generations (depth + 1)

theorem fixture_depth_table :
    [(opacity (metric 1 false), opacity (metric 1 true)),
     (opacity (metric 2 false), opacity (metric 2 true)),
     (opacity (metric 4 false), opacity (metric 4 true)),
     (opacity (metric 8 false), opacity (metric 8 true))] =
    [(0, 1), (1, 0), (1, 0), (1, 0)] := by decide

end Oracle
