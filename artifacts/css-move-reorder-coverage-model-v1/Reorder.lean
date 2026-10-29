import Parent

namespace ReorderCoverage
open ParentCoverage
variable {Node Parent : Type} [DecidableEq Node] [DecidableEq Parent]

def reorder (w : World Node Parent) (parent : Parent) (node : Node)
    (front back : List Node) : World Node Parent where
  children := fun p => if p = parent then front ++ node :: back else w.children p
  owner := w.owner

theorem reorder_well_formed (w : World Node Parent) (wf : WellFormed w)
    (parent : Parent) (node : Node) (front back : List Node)
    (owned : w.owner node = parent)
    (gap : (w.children parent).erase node = front ++ back) :
    WellFormed (reorder w parent node front back) := by
  have removed := List.Nodup.erase node (wf.1 parent)
  have absent := (wf.1 parent).not_mem_erase (a := node)
  rw [gap] at removed absent
  have inserted : (front ++ node :: back).Nodup := by
    simp only [List.nodup_append, List.nodup_cons, List.mem_append, List.mem_cons] at *
    grind
  constructor
  · intro p
    by_cases same : p = parent
    · subst p
      simpa [reorder] using inserted
    · simpa [reorder, same] using wf.1 p
  · intro n p
    by_cases same : p = parent
    · subst p
      have membership := (wf.1 parent).mem_erase_iff (a := n) (b := node)
      rw [gap] at membership
      have original := wf.2 n parent
      simp only [reorder, ↓reduceIte, List.mem_append, List.mem_cons]
      simp only [List.mem_append] at membership
      grind
    · simpa [reorder, same] using wf.2 n p

theorem reinsert_length (children : List Node) (node : Node)
    (front back : List Node) (present : node ∈ children)
    (gap : children.erase node = front ++ back) :
    (front ++ node :: back).length = children.length := by
  have erased := List.length_erase_of_mem present
  have splitLength := congrArg List.length gap
  have positive := List.idxOf_lt_length_of_mem present
  simp only [List.length_append, List.length_cons] at *
  omega

theorem every_count_unchanged (w : World Node Parent) (wf : WellFormed w)
    (parent : Parent) (node : Node) (front back : List Node)
    (owned : w.owner node = parent)
    (gap : (w.children parent).erase node = front ++ back) :
    ∀ n, (values (reorder w parent node front back) n).1 = (values w n).1 := by
  have lengthEq := reinsert_length (w.children parent) node front back
    ((wf.2 node parent).mpr owned) gap
  intro n
  by_cases same : w.owner n = parent
  · simp [values, siblings, reorder, same, lengthEq]
  · simp [values, siblings, reorder, same]

omit [DecidableEq Node] in
theorem outside_siblings_unchanged (w : World Node Parent) (wf : WellFormed w)
    (parent : Parent) (node n : Node) (front back : List Node)
    (outside : n ∉ w.children parent) :
    siblings (reorder w parent node front back) n = siblings w n := by
  have other : w.owner n ≠ parent := fun h => outside ((wf.2 n parent).mpr h)
  simp [siblings, reorder, other]

theorem outside_values_unchanged (w : World Node Parent) (wf : WellFormed w)
    (parent : Parent) (node n : Node) (front back : List Node)
    (outside : n ∉ w.children parent) :
    values (reorder w parent node front back) n = values w n := by
  unfold values
  rw [outside_siblings_unchanged w wf parent node n front back outside]

theorem counts_need_no_refresh (w : World Node Parent) (wf : WellFormed w)
    (parent : Parent) (node : Node) (front back : List Node)
    (owned : w.owner node = parent)
    (gap : (w.children parent).erase node = front ++ back) :
    ∀ n, MoveCoverage.refresh (fun n => (values w n).1)
      (fun n => (values (reorder w parent node front back) n).1) (fun _ => false) n =
      (values (reorder w parent node front back) n).1 := by
  intro n
  simp only [MoveCoverage.refresh, Bool.false_eq_true, ↓reduceIte]
  exact (every_count_unchanged w wf parent node front back owned gap n).symm

theorem parent_notification_fresh (w : World Node Parent) (wf : WellFormed w)
    (parent : Parent) (node : Node) (front back : List Node) :
    ∀ n, MoveCoverage.refresh (values w) (values (reorder w parent node front back))
      (fun n => decide (n ∈ w.children parent)) n =
      values (reorder w parent node front back) n := by
  intro n
  by_cases inside : n ∈ w.children parent
  · simp [MoveCoverage.refresh, inside]
  · have equal := outside_values_unchanged w wf parent node n front back inside
    simp [MoveCoverage.refresh, inside, equal]

omit [DecidableEq Parent] in
theorem shared_prefix_index (left a b : List Node) (n : Node) (inside : n ∈ left) :
    (left ++ a).idxOf n = (left ++ b).idxOf n := by
  simp [List.idxOf_append, inside]

omit [DecidableEq Parent] in
theorem shared_suffix_index (a b right : List Node) (n : Node)
    (outsideA : n ∉ a) (outsideB : n ∉ b) (sameLength : a.length = b.length) :
    (a ++ right).idxOf n = (b ++ right).idxOf n := by
  simp [List.idxOf_append, outsideA, outsideB, sameLength]

omit [DecidableEq Parent] in
theorem outside_moved_interval_index (left middle right : List Node) (node n : Node)
    (notMoved : n ≠ node) (outsideMiddle : n ∉ middle) :
    ((left ++ (node :: middle)) ++ right).idxOf n =
      ((left ++ (middle ++ [node])) ++ right).idxOf n := by
  by_cases insideLeft : n ∈ left
  · simpa only [List.append_assoc] using
      shared_prefix_index left ((node :: middle) ++ right) ((middle ++ [node]) ++ right) n insideLeft
  · apply shared_suffix_index
    · simp [List.mem_append, List.mem_cons, insideLeft, notMoved, outsideMiddle]
    · simp [List.mem_append, insideLeft, notMoved, outsideMiddle]
    · simp only [List.length_append, List.length_cons, List.length_nil]

def exampleBefore : World (Fin 4) (Fin 1) where
  children := fun _ => [0, 1, 2, 3]
  owner := fun _ => 0

def exampleAfter := reorder exampleBefore 0 2 [] [0, 1, 3]
def movedOnly (n : Fin 4) : Bool := n == 2

theorem example_count_stable_index_changes :
    WellFormed exampleBefore ∧ WellFormed exampleAfter ∧
    (∀ n, (values exampleBefore n).1 = (values exampleAfter n).1) ∧
    values exampleBefore 0 = (4, 1) ∧ values exampleAfter 0 = (4, 2) ∧
    values exampleBefore 2 = (4, 3) ∧ values exampleAfter 2 = (4, 1) := by
  unfold WellFormed
  decide

end ReorderCoverage
