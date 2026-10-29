import Coverage

namespace ParentCoverage

structure World (Node Parent : Type) where
  children : Parent → List Node
  owner : Node → Parent

def WellFormed {Node Parent : Type} (w : World Node Parent) : Prop :=
  (∀ p, (w.children p).Nodup) ∧
  (∀ n p, n ∈ w.children p ↔ w.owner n = p)

variable {Node Parent : Type} [DecidableEq Node] [DecidableEq Parent]

def move (w : World Node Parent) (old dest : Parent) (node : Node)
    (front back : List Node) : World Node Parent where
  children := fun p => if p = old then (w.children old).erase node
    else if p = dest then front ++ node :: back else w.children p
  owner := fun n => if n = node then dest else w.owner n

def siblings (w : World Node Parent) (n : Node) := w.children (w.owner n)
def values (w : World Node Parent) (n : Node) : Nat × Nat :=
  ((siblings w n).length, (siblings w n).idxOf n + 1)
def affected (w : World Node Parent) (old dest : Parent) (n : Node) : Bool :=
  decide (n ∈ w.children old ∨ n ∈ w.children dest)

omit [DecidableEq Node] [DecidableEq Parent] in
theorem destination_excludes_moved (w : World Node Parent) (wf : WellFormed w)
    (old dest : Parent) (node : Node) (cross : old ≠ dest)
    (owned : w.owner node = old) : node ∉ w.children dest := by
  intro present
  exact cross (owned.symm.trans ((wf.2 node dest).mp present))

theorem old_list_removes_one (w : World Node Parent) (wf : WellFormed w)
    (old dest : Parent) (node : Node) (front back : List Node)
    (owned : w.owner node = old) :
    ((move w old dest node front back).children old).length =
      (w.children old).length - 1 := by
  simp [move, List.length_erase_of_mem ((wf.2 node old).mpr owned)]

theorem moved_changes_parent (w : World Node Parent) (wf : WellFormed w)
    (old dest : Parent) (node : Node) (front back : List Node)
    (cross : old ≠ dest) :
    node ∉ (move w old dest node front back).children old ∧
    node ∈ (move w old dest node front back).children dest ∧
    (move w old dest node front back).owner node = dest := by
  have distinct : dest ≠ old := Ne.symm cross
  simp [move, distinct, (wf.1 old).not_mem_erase]

theorem move_well_formed (w : World Node Parent) (wf : WellFormed w)
    (old dest : Parent) (node : Node) (front back : List Node)
    (cross : old ≠ dest) (owned : w.owner node = old)
    (split : w.children dest = front ++ back) :
    WellFormed (move w old dest node front back) := by
  have noDest := destination_excludes_moved w wf old dest node cross owned
  have inserted : (front ++ node :: back).Nodup := by
    have source := wf.1 dest
    rw [split] at source noDest
    simp only [List.nodup_append, List.nodup_cons, List.mem_append, List.mem_cons] at *
    grind
  constructor
  · intro p
    by_cases hOld : p = old
    · subst p
      simpa [move] using List.Nodup.erase node (wf.1 old)
    · by_cases hDest : p = dest
      · subst p
        simpa [move, hOld] using inserted
      · simpa [move, hOld, hDest] using wf.1 p
  · intro n p
    by_cases hOld : p = old
    · subst p
      have membership := (wf.1 old).mem_erase_iff (a := n) (b := node)
      by_cases equal : n = node
      · subst n
        simp [move, membership, Ne.symm cross]
      · simp [move, membership, equal, wf.2 n old]
    · by_cases hDest : p = dest
      · subst p
        have membership := wf.2 n dest
        rw [split] at membership
        by_cases equal : n = node
        · subst n
          simp [move, hOld]
        · simpa [move, hOld, equal, List.mem_append, List.mem_cons] using membership
      · by_cases equal : n = node
        · subst n
          have absent : node ∉ w.children p := by
            intro h
            exact hOld (((wf.2 node p).mp h).symm.trans owned)
          simp [move, hOld, hDest, absent, Ne.symm hDest]
        · simpa [move, hOld, hDest, equal] using wf.2 n p

theorem outside_siblings_unchanged (w : World Node Parent) (wf : WellFormed w)
    (old dest : Parent) (node n : Node) (front back : List Node)
    (owned : w.owner node = old)
    (outsideOld : n ∉ w.children old) (outsideDest : n ∉ w.children dest) :
    siblings (move w old dest node front back) n = siblings w n := by
  have noOld : w.owner n ≠ old := fun h => outsideOld ((wf.2 n old).mpr h)
  have noDest : w.owner n ≠ dest := fun h => outsideDest ((wf.2 n dest).mpr h)
  have notMoved : n ≠ node := by
    intro h
    subst n
    exact noOld owned
  simp [siblings, move, notMoved, noOld, noDest]

theorem outside_values_unchanged (w : World Node Parent) (wf : WellFormed w)
    (old dest : Parent) (node n : Node) (front back : List Node)
    (owned : w.owner node = old)
    (outsideOld : n ∉ w.children old) (outsideDest : n ∉ w.children dest) :
    values (move w old dest node front back) n = values w n := by
  unfold values
  rw [outside_siblings_unchanged w wf old dest node n front back owned outsideOld outsideDest]

theorem both_domains_fresh (w : World Node Parent) (wf : WellFormed w)
    (old dest : Parent) (node : Node) (front back : List Node)
    (owned : w.owner node = old) :
    ∀ n, MoveCoverage.refresh (values w) (values (move w old dest node front back))
      (affected w old dest) n = values (move w old dest node front back) n := by
  intro n
  by_cases inside : n ∈ w.children old ∨ n ∈ w.children dest
  · simp [MoveCoverage.refresh, affected, inside]
  · have oldOut : n ∉ w.children old := fun h => inside (Or.inl h)
    have destOut : n ∉ w.children dest := fun h => inside (Or.inr h)
    have unchanged := outside_values_unchanged w wf old dest node n front back owned oldOut destOut
    simp [MoveCoverage.refresh, affected, inside, unchanged]

theorem valid_move_fresh (w : World Node Parent) (wf : WellFormed w)
    (old dest : Parent) (node : Node) (front back : List Node)
    (cross : old ≠ dest) (owned : w.owner node = old)
    (split : w.children dest = front ++ back) :
    WellFormed (move w old dest node front back) ∧
    ∀ n, MoveCoverage.refresh (values w) (values (move w old dest node front back))
      (affected w old dest) n = values (move w old dest node front back) n := by
  exact ⟨move_well_formed w wf old dest node front back cross owned split,
    both_domains_fresh w wf old dest node front back owned⟩

def exampleBefore : World (Fin 4) (Fin 2) where
  children := fun p => if p = 0 then [1, 0] else [2, 3]
  owner := fun n => if n.val < 2 then 0 else 1

def exampleAfter := move exampleBefore 0 1 1 [2, 3] []
def destinationOnly (n : Fin 4) : Bool := [2, 3, 1].contains n

theorem concrete_valid_move_and_stale_source :
    WellFormed exampleBefore ∧ WellFormed exampleAfter ∧
    values exampleBefore 0 = (2, 2) ∧ values exampleAfter 0 = (1, 1) ∧
    MoveCoverage.refresh (values exampleBefore) (values exampleAfter) destinationOnly 0 = (2, 2) := by
  unfold WellFormed
  decide

end ParentCoverage
