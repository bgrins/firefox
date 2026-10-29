import Std

namespace MoveCoverage

def refresh {Node Value : Type} (before after : Node → Value)
    (notify : Node → Bool) (node : Node) : Value :=
  if notify node = true then after node else before node

theorem fresh_iff_covered {Node Value : Type} (before after : Node → Value)
    (alive notify : Node → Bool) :
    (∀ node, alive node = true → refresh before after notify node = after node) ↔
    (∀ node, alive node = true → before node ≠ after node → notify node = true) := by
  classical
  constructor
  · intro fresh node living changed
    by_cases marked : notify node = true
    · exact marked
    · have unchanged := fresh node living
      simp only [refresh, marked, ↓reduceIte] at unchanged
      exact False.elim (changed unchanged)
  · intro covered node living
    by_cases marked : notify node = true
    · simp [refresh, marked]
    · have unchanged : before node = after node :=
        Classical.byContradiction fun changed => marked (covered node living changed)
      simp [refresh, marked, unchanged]

theorem adding_notifications_preserves_freshness {Node Value : Type}
    (before after : Node → Value) (alive small large : Node → Bool)
    (fresh : ∀ node, alive node = true → refresh before after small node = after node)
    (includes : ∀ node, small node = true → large node = true) :
    ∀ node, alive node = true → refresh before after large node = after node := by
  apply (fresh_iff_covered before after alive large).mpr
  intro node living changed
  exact includes node ((fresh_iff_covered before after alive small).mp fresh node living changed)

abbrev Node := Fin 4
abbrev Forest := List (List Node)

def siblings (forest : Forest) (node : Node) : List Node :=
  (forest.find? (fun children => children.contains node)).getD []

def count (forest : Forest) (node : Node) : Nat := (siblings forest node).length

def index (forest : Forest) (node : Node) : Nat := (siblings forest node).idxOf node + 1

def before : Forest := [[0, 1], [2, 3]]
def after : Forest := [[0], [2, 3, 1]]
def destination (node : Node) : Bool := [2, 3, 1].contains node
def bothParents (node : Node) : Bool := [0, 1, 2, 3].contains node

theorem destination_only_stale_count :
    count before 0 = 2 ∧ count after 0 = 1 ∧
    refresh (count before) (count after) destination 0 = 2 := by decide

theorem unchanged_source_index_can_pass :
    ∀ node, refresh (index before) (index after) destination node = index after node := by decide

theorem both_parent_notifications_fresh :
    (∀ node, refresh (count before) (count after) bothParents node = count after node) ∧
    (∀ node, refresh (index before) (index after) bothParents node = index after node) := by decide

def reorderBefore : Forest := [[0, 1, 2, 3]]
def reorderAfter : Forest := [[1, 2, 3, 0]]
def reorderDestination (node : Node) : Bool := [1, 2, 3, 0].contains node

theorem same_parent_destination_fresh :
    (∀ node, refresh (count reorderBefore) (count reorderAfter) reorderDestination node = count reorderAfter node) ∧
    (∀ node, refresh (index reorderBefore) (index reorderAfter) reorderDestination node = index reorderAfter node) := by decide

def firstBefore : Forest := [[1, 0], [2, 3]]

theorem moving_first_exposes_stale_index :
    index firstBefore 0 = 2 ∧ index after 0 = 1 ∧
    refresh (index firstBefore) (index after) destination 0 = 2 := by decide

end MoveCoverage
