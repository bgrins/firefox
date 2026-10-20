import Ownership

namespace Destruction.Ownership

def roomy : Capacity := fun _ => 8

def validNested : PropertyTable :=
  ⟨some 90, [.itemCache 30,
    .shared 50 (some 60) [⟨some 70, [0, 2, 0]⟩, ⟨some 80, []⟩]]⟩

theorem valid_nested_shape : TableShape roomy validNested := by
  simp [TableShape, PropertyShape, ArrayShape, validNested, roomy]

theorem missing_item_buffer_rejected :
    ¬ TableShape roomy ⟨some 90, [.shared 50 (some 60) [⟨none, [0]⟩]]⟩ := by
  simp [TableShape, PropertyShape, ArrayShape]

theorem missing_line_buffer_rejected :
    ¬ TableShape roomy ⟨some 90, [.shared 50 none [⟨some 70, []⟩]]⟩ := by
  simp [TableShape, PropertyShape, ArrayShape]

theorem missing_property_buffer_rejected :
    ¬ TableShape roomy ⟨none, [.itemCache 30]⟩ := by
  simp [TableShape, ArrayShape]

theorem allocated_empty_property_buffer_admitted :
    TableShape roomy ⟨some 90, []⟩ := by
  simp [TableShape, ArrayShape, roomy]

theorem allocated_empty_line_buffer_admitted :
    PropertyShape roomy (.shared 50 (some 60) []) := by
  simp [PropertyShape, ArrayShape, roomy]

theorem repeated_raw_references_admitted :
    PropertyShape roomy (.shared 50 (some 60)
      [⟨some 70, [0, 0, 2, 2]⟩, ⟨some 80, [2, 0]⟩]) := by
  simp [PropertyShape, ArrayShape, roomy]

theorem cross_owner_same_root_rejected :
    ¬ SeparatePlans [⟨30, .itemCache⟩, ⟨90, .propertiesBuffer⟩]
      [⟨30, .itemCache⟩, ⟨91, .propertiesBuffer⟩] := by
  intro separate
  exact separate ⟨30, .itemCache⟩ (by simp) ⟨30, .itemCache⟩ (by simp) rfl

theorem cross_owner_same_buffer_rejected :
    ¬ SeparatePlans [⟨70, .itemsBuffer⟩, ⟨50, .shared⟩]
      [⟨70, .itemsBuffer⟩, ⟨51, .shared⟩] := by
  intro separate
  exact separate ⟨70, .itemsBuffer⟩ (by simp) ⟨70, .itemsBuffer⟩ (by simp) rfl

theorem root_buffer_alias_rejected_independently_of_roles :
    ¬ SeparatePlans [⟨30, .itemCache⟩] [⟨30, .itemsBuffer⟩] :=
  cross_role_alias_rejected 30 30 .itemCache .itemsBuffer rfl

def oneTable : PropertyTable := ⟨some 90, [.itemCache 30]⟩
def twoTable : PropertyTable := ⟨some 91, [.itemCache 40]⟩

def twoOwners : Heap := fun a =>
  if a = 0 then some (.frame 1 true oneTable)
  else if a = 2 then some (.frame 3 true twoTable)
  else if a = 1 then some (.content (some 0))
  else if a = 3 then some (.content (some 2))
  else ([(30, Role.itemCache), (40, .itemCache),
    (90, .propertiesBuffer), (91, .propertiesBuffer)].lookup a).map Cell.allocation

theorem one_table_represented : Represented twoOwners roomy oneTable := by
  refine ⟨?_, [⟨30, .itemCache⟩, ⟨90, .propertiesBuffer⟩], rfl, by decide, ?_⟩
  · simp [TableShape, ArrayShape, PropertyShape, oneTable, roomy]
  · intro x member
    simp only [List.mem_cons, List.not_mem_nil, or_false] at member
    rcases member with rfl | rfl <;> unfold Allocation <;> decide

theorem two_table_represented : Represented twoOwners roomy twoTable := by
  refine ⟨?_, [⟨40, .itemCache⟩, ⟨91, .propertiesBuffer⟩], rfl, by decide, ?_⟩
  · simp [TableShape, ArrayShape, PropertyShape, twoTable, roomy]
  · intro x member
    simp only [List.mem_cons, List.not_mem_nil, or_false] at member
    rcases member with rfl | rfl <;> unfold Allocation <;> decide

theorem two_owner_residents (f c : Address) (b : Bool) (p : PropertyTable)
    (present : twoOwners f = some (.frame c b p)) :
    (f = 0 ∧ p = oneTable) ∨ (f = 2 ∧ p = twoTable) := by
  by_cases zero : f = 0
  · subst f
    simp [twoOwners] at present
    exact Or.inl ⟨rfl, present.2.2.symm⟩
  · by_cases two : f = 2
    · subst f
      simp [twoOwners] at present
      exact Or.inr ⟨rfl, present.2.2.symm⟩
    · by_cases one : f = 1
      · subst f; simp [twoOwners] at present
      · by_cases three : f = 3
        · subst f; simp [twoOwners] at present
        · simp only [twoOwners, ite_eq_right zero, ite_eq_right two, ite_eq_right one, ite_eq_right three] at present
          cases entry : ([(30, Role.itemCache), (40, .itemCache),
            (90, .propertiesBuffer), (91, .propertiesBuffer)].lookup f) <;>
            simp [entry] at present

theorem two_owners_world : World twoOwners roomy := by
  constructor
  · intro f c b p present
    rcases two_owner_residents f c b p present with ⟨_, rfl⟩ | ⟨_, rfl⟩
    · exact one_table_represented
    · exact two_table_represented
  · intro f g c d b e p q xs ys atF atG different px py
    rcases two_owner_residents f c b p atF with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;>
      rcases two_owner_residents g d e q atG with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
    · exact False.elim (different rfl)
    · simp [tablePlan, plan, footprint, optional, oneTable, twoTable] at px py
      subst xs; subst ys
      simp [SeparatePlans]
    · simp [tablePlan, plan, footprint, optional, oneTable, twoTable] at px py
      subst xs; subst ys
      simp [SeparatePlans]
    · exact False.elim (different rfl)

theorem first_cleanup_preserves_second_ownership :
    ∃ next, removeAll twoOwners 0 = some next ∧ World next roomy ∧
      next 2 = some (.frame 3 true twoTable) ∧
      next 40 = some (.allocation .itemCache) ∧ next 30 = none := by
  obtain ⟨next, success, after⟩ := represented_cleanup_executes twoOwners roomy
    0 1 true oneTable (by decide) two_owners_world
  refine ⟨next, success, after, ?_, ?_, ?_⟩
  · exact other_frame_survives twoOwners next 0 1 true oneTable (by decide)
      success 2 3 true twoTable (by decide) (by decide)
  · have allocated : Allocated twoOwners
        [⟨40, .itemCache⟩, ⟨91, .propertiesBuffer⟩] := by
      intro x member
      simp only [List.mem_cons, List.not_mem_nil, or_false] at member
      rcases member with rfl | rfl <;> unfold Allocation <;> decide
    have ready := other_allocations_survive twoOwners next 0 1 true oneTable
      [⟨30, .itemCache⟩, ⟨90, .propertiesBuffer⟩]
      [⟨40, .itemCache⟩, ⟨91, .propertiesBuffer⟩]
      (by decide) rfl success (by simp [SeparatePlans]) allocated
    exact ready ⟨40, .itemCache⟩ (by simp)
  · obtain ⟨xs, planned, execution⟩ := phase_execution twoOwners next 0 1 true
      oneTable (by decide) success
    have xsEq : xs = [⟨30, .itemCache⟩, ⟨90, .propertiesBuffer⟩] := by
      simpa [tablePlan, plan, footprint, optional, oneTable] using planned.symm
    subst xs
    exact freed_allocation _ _ _ ⟨30, .itemCache⟩ (by simp) execution

end Destruction.Ownership
