import Reorder

namespace GapCoverage
variable {Node : Type} [DecidableEq Node]

def IntervalMove (before after : List Node) (node : Node)
    (left middle right : List Node) : Prop :=
  (before = (left ++ node :: middle) ++ right ∧
   after = (left ++ (middle ++ [node])) ++ right) ∨
  (before = (left ++ (middle ++ [node])) ++ right ∧
   after = (left ++ node :: middle) ++ right)

theorem arbitrary_gap_interval (before : List Node) (node : Node)
    (front back : List Node) (present : node ∈ before)
    (gap : before.erase node = front ++ back) :
    ∃ left middle right, IntervalMove before (front ++ node :: back) node left middle right := by
  obtain ⟨oldFront, oldBack, original, absent⟩ := List.eq_append_cons_of_mem present
  have erased : before.erase node = oldFront ++ oldBack := by
    rw [original, List.erase_append_right _ absent, List.erase_cons_head]
  have splits : oldFront ++ oldBack = front ++ back := erased.symm.trans gap
  rcases List.append_eq_append_iff.mp splits with ⟨middle, nextFront, oldTail⟩ | ⟨middle, oldPrefix, nextTail⟩
  · refine ⟨oldFront, middle, back, Or.inl ?_⟩
    constructor
    · simp [original, oldTail, List.append_assoc]
    · simp [nextFront, List.append_assoc]
  · refine ⟨front, middle, oldBack, Or.inr ?_⟩
    constructor
    · simp [original, oldPrefix, List.append_assoc]
    · simp [nextTail, List.append_assoc]

theorem interval_index_locality (before after : List Node) (node : Node)
    (left middle right : List Node) (shape : IntervalMove before after node left middle right)
    (n : Node) (notMoved : n ≠ node) (outside : n ∉ middle) :
    before.idxOf n = after.idxOf n := by
  rcases shape with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
  · exact ReorderCoverage.outside_moved_interval_index left middle right node n notMoved outside
  · exact (ReorderCoverage.outside_moved_interval_index left middle right node n notMoved outside).symm

theorem arbitrary_gap_index_locality (before : List Node) (node : Node)
    (front back : List Node) (present : node ∈ before)
    (gap : before.erase node = front ++ back) :
    ∃ left middle right,
      IntervalMove before (front ++ node :: back) node left middle right ∧
      ∀ n, n ≠ node → n ∉ middle → before.idxOf n = (front ++ node :: back).idxOf n := by
  obtain ⟨left, middle, right, shape⟩ := arbitrary_gap_interval before node front back present gap
  exact ⟨left, middle, right, shape, interval_index_locality before _ node left middle right shape⟩

theorem original_gap_identity (before : List Node) (node : Node)
    (oldFront oldBack front back : List Node)
    (original : before = oldFront ++ node :: oldBack)
    (absent : node ∉ oldFront)
    (gap : before.erase node = front ++ back)
    (sameGap : front.length = oldFront.length) :
    before = front ++ node :: back := by
  have erased : before.erase node = oldFront ++ oldBack := by
    rw [original, List.erase_append_right _ absent, List.erase_cons_head]
  have parts := List.append_inj (erased.symm.trans gap) sameGap.symm
  simpa [parts.1, parts.2] using original

theorem member_block_bound (left block right : List Node) (n : Node)
    (unique : ((left ++ block) ++ right).Nodup) (inside : n ∈ block) :
    left.length ≤ ((left ++ block) ++ right).idxOf n ∧
    ((left ++ block) ++ right).idxOf n < left.length + block.length := by
  have outside : n ∉ left := by
    simp only [List.nodup_append] at unique
    grind
  have bound := List.idxOf_lt_length_of_mem inside
  have memPrefix : n ∈ left ++ block := List.mem_append_right left inside
  simp only [List.idxOf_append, ite_eq_left memPrefix, ite_eq_right outside]
  omega

theorem interval_members_bounded (before after : List Node) (node : Node)
    (left middle right : List Node) (shape : IntervalMove before after node left middle right)
    (unique : before.Nodup) (n : Node) (inside : n = node ∨ n ∈ middle) :
    left.length ≤ before.idxOf n ∧ before.idxOf n ≤ left.length + middle.length := by
  rcases shape with ⟨rfl, _⟩ | ⟨rfl, _⟩
  · have bound := member_block_bound left (node :: middle) right n unique (by simpa using inside)
    simp only [List.length_cons] at bound
    omega
  · have bound := member_block_bound left (middle ++ [node]) right n unique (by simpa [List.mem_append, or_comm] using inside)
    simp only [List.length_append, List.length_cons, List.length_nil] at bound
    omega

theorem arbitrary_gap_numeric_locality (before : List Node) (node : Node)
    (front back : List Node) (unique : before.Nodup) (present : node ∈ before)
    (gap : before.erase node = front ++ back) :
    ∃ left middle right,
      IntervalMove before (front ++ node :: back) node left middle right ∧
      ∀ n, before.idxOf n < left.length ∨ left.length + middle.length < before.idxOf n →
        before.idxOf n = (front ++ node :: back).idxOf n := by
  obtain ⟨left, middle, right, shape, locality⟩ := arbitrary_gap_index_locality before node front back present gap
  refine ⟨left, middle, right, shape, ?_⟩
  intro n outside
  have excluded : ¬ (n = node ∨ n ∈ middle) := by
    intro inside
    have bound := interval_members_bounded before _ node left middle right shape unique n inside
    omega
  exact locality n (fun h => excluded (Or.inl h)) (fun h => excluded (Or.inr h))

theorem interval_refresh_fresh (before : List Node) (node : Node)
    (front back : List Node) (present : node ∈ before)
    (gap : before.erase node = front ++ back) :
    ∃ left middle right,
      IntervalMove before (front ++ node :: back) node left middle right ∧
      ∀ n, MoveCoverage.refresh (fun n => before.idxOf n + 1)
        (fun n => (front ++ node :: back).idxOf n + 1)
        (fun n => decide (n = node ∨ n ∈ middle)) n =
        (front ++ node :: back).idxOf n + 1 := by
  obtain ⟨left, middle, right, shape, locality⟩ := arbitrary_gap_index_locality before node front back present gap
  refine ⟨left, middle, right, shape, ?_⟩
  intro n
  by_cases inside : n = node ∨ n ∈ middle
  · simp [MoveCoverage.refresh, inside]
  · have equal := locality n (fun h => inside (Or.inl h)) (fun h => inside (Or.inr h))
    simp [MoveCoverage.refresh, inside, equal]

open ParentCoverage ReorderCoverage

theorem valid_world_interval_fresh {Parent : Type} [DecidableEq Parent]
    (w : World Node Parent) (wf : WellFormed w) (parent : Parent) (node : Node)
    (front back : List Node) (owned : w.owner node = parent)
    (gap : (w.children parent).erase node = front ++ back) :
    ∃ left middle right,
      IntervalMove (w.children parent) (front ++ node :: back) node left middle right ∧
      WellFormed (reorder w parent node front back) ∧
      (∀ n, (values (reorder w parent node front back) n).1 = (values w n).1) ∧
      ∀ n, MoveCoverage.refresh (values w) (values (reorder w parent node front back))
        (fun n => decide (n ∈ w.children parent ∧
          left.length ≤ (w.children parent).idxOf n ∧
          (w.children parent).idxOf n ≤ left.length + middle.length)) n =
        values (reorder w parent node front back) n := by
  have present := (wf.2 node parent).mpr owned
  obtain ⟨left, middle, right, shape, locality⟩ :=
    arbitrary_gap_numeric_locality (w.children parent) node front back (wf.1 parent) present gap
  have counts := every_count_unchanged w wf parent node front back owned gap
  refine ⟨left, middle, right, shape,
    reorder_well_formed w wf parent node front back owned gap, counts, ?_⟩
  intro n
  by_cases notify : n ∈ w.children parent ∧ left.length ≤ (w.children parent).idxOf n ∧
      (w.children parent).idxOf n ≤ left.length + middle.length
  · simp [MoveCoverage.refresh, notify]
  · have equal : values w n = values (reorder w parent node front back) n := by
      by_cases inside : n ∈ w.children parent
      · have owner := (wf.2 n parent).mp inside
        have outside : (w.children parent).idxOf n < left.length ∨
            left.length + middle.length < (w.children parent).idxOf n := by
          simp only [inside, true_and, not_and] at notify
          omega
        have indexEq := locality n outside
        apply Prod.ext
        · exact (counts n).symm
        · simpa [values, siblings, reorder, owner] using indexEq
      · exact (outside_values_unchanged w wf parent node n front back inside).symm
    simp [MoveCoverage.refresh, notify, equal]

theorem boundary_examples :
    ([0,1,2,3] : List Nat).erase 2 = [] ++ [0,1,3] ∧
    IntervalMove [0,1,2,3] [2,0,1,3] 2 [] [0,1] [3] ∧
    ([0,1,2,3] : List Nat).erase 0 = [1,2,3] ++ [] ∧
    IntervalMove [0,1,2,3] [1,2,3,0] 0 [] [1,2,3] [] ∧
    ([0,1,2,3] : List Nat).erase 2 = [0,1] ++ [3] ∧
    IntervalMove [0,1,2,3] [0,1,2,3] 2 [0,1] [] [3] ∧
    ([0] : List Nat).erase 0 = [] ++ [] ∧
    IntervalMove [0] [0] 0 [] [] [] := by
  unfold IntervalMove
  decide

end GapCoverage
