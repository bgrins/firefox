import Std

namespace CssSemantics.GuardedState

variable {Name : Type} [DecidableEq Name]

def prefixThrough : List Name → Name → List Name
  | [], _ => []
  | head :: rest, repeated =>
      if head = repeated then [head] else head :: prefixThrough rest repeated

def markCycle (active marked : List Name) (repeated : Name) : List Name :=
  marked ++ prefixThrough active repeated

def pop (owner : Name) (marked : List Name) : List Name :=
  marked.filter fun name => decide (name ≠ owner)

theorem prefixThrough_subset (active : List Name) (repeated name : Name)
    (member : name ∈ prefixThrough active repeated) : name ∈ active := by
  induction active with
  | nil => simp [prefixThrough] at member
  | cons head rest ih =>
    by_cases equal : head = repeated
    · have same : name = head := by simpa [prefixThrough, equal] using member
      exact List.mem_cons.mpr (Or.inl same)
    · simp only [prefixThrough, equal, ite_false, List.mem_cons] at member
      rcases member with rfl | member
      · exact List.mem_cons_self
      · exact List.mem_cons_of_mem _ (ih member)

theorem repeated_mem_prefixThrough (active : List Name) (repeated : Name)
    (member : repeated ∈ active) : repeated ∈ prefixThrough active repeated := by
  induction active with
  | nil => simp at member
  | cons head rest ih =>
    by_cases equal : head = repeated
    · simp [prefixThrough, equal]
    · simp only [List.mem_cons] at member
      rcases member with equal' | member
      · exact False.elim (equal equal'.symm)
      · simp [prefixThrough, equal, ih member]

theorem head_mem_prefixThrough (head repeated : Name) (rest : List Name) :
    head ∈ prefixThrough (head :: rest) repeated := by
  simp only [prefixThrough]
  split <;> simp

theorem prefixThrough_boundary (before after : List Name) (repeated : Name)
    (absent : repeated ∉ before) :
    prefixThrough (before ++ repeated :: after) repeated = before ++ [repeated] := by
  induction before with
  | nil => simp [prefixThrough]
  | cons head rest ih =>
    have unequal : head ≠ repeated := by
      intro equal
      subst head
      exact absent List.mem_cons_self
    have restAbsent : repeated ∉ rest := fun member => absent (List.mem_cons_of_mem _ member)
    simp [prefixThrough, unequal, ih restAbsent]

theorem mem_markCycle (active marked : List Name) (repeated name : Name) :
    name ∈ markCycle active marked repeated ↔
      name ∈ marked ∨ name ∈ prefixThrough active repeated := by
  simp [markCycle]

theorem markCycle_preserves (active marked : List Name) (repeated name : Name)
    (member : name ∈ marked) : name ∈ markCycle active marked repeated :=
  (mem_markCycle active marked repeated name).mpr (Or.inl member)

theorem markCycle_subset (active marked : List Name) (repeated : Name)
    (contained : ∀ name, name ∈ marked → name ∈ active) :
    ∀ name, name ∈ markCycle active marked repeated → name ∈ active := by
  intro name member
  rcases (mem_markCycle active marked repeated name).mp member with old | cycle
  · exact contained name old
  · exact prefixThrough_subset active repeated name cycle

theorem repeated_mem_markCycle (active marked : List Name) (repeated : Name)
    (member : repeated ∈ active) : repeated ∈ markCycle active marked repeated :=
  (mem_markCycle active marked repeated repeated).mpr
    (Or.inr (repeated_mem_prefixThrough active repeated member))

theorem current_mem_markCycle (current repeated : Name) (rest marked : List Name) :
    current ∈ markCycle (current :: rest) marked repeated :=
  (mem_markCycle _ marked repeated current).mpr
    (Or.inr (head_mem_prefixThrough current repeated rest))

theorem mem_pop (owner name : Name) (marked : List Name) :
    name ∈ pop owner marked ↔ name ∈ marked ∧ name ≠ owner := by
  simp [pop]

theorem owner_not_mem_pop (owner : Name) (marked : List Name) :
    owner ∉ pop owner marked := by
  simp [mem_pop]

theorem pop_preserves_other (owner name : Name) (marked : List Name) (unequal : name ≠ owner) :
    name ∈ pop owner marked ↔ name ∈ marked := by
  simp [mem_pop, unequal]

theorem pop_subset_tail (owner : Name) (active marked : List Name)
    (contained : ∀ name, name ∈ marked → name ∈ owner :: active) :
    ∀ name, name ∈ pop owner marked → name ∈ active := by
  intro name member
  obtain ⟨old, unequal⟩ := (mem_pop owner name marked).mp member
  rcases List.mem_cons.mp (contained name old) with equal | member
  · exact False.elim (unequal equal)
  · exact member

end CssSemantics.GuardedState
