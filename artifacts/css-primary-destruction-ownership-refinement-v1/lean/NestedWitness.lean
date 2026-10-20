import RefinementWitnesses

namespace Destruction.Ownership

def nestedTable : PropertyTable :=
  ⟨some 90, [.itemCache 30,
    .shared 50 (some 60) [⟨some 70, [0, 2, 0, 999]⟩, ⟨some 80, []⟩]]⟩

def nestedReleases : List Release :=
  [⟨30, .itemCache⟩, ⟨70, .itemsBuffer⟩, ⟨80, .itemsBuffer⟩,
   ⟨60, .linesBuffer⟩, ⟨50, .shared⟩, ⟨90, .propertiesBuffer⟩]

def nestedOwners : Heap := fun a =>
  if a = 0 then some (.frame 1 true nestedTable)
  else if a = 2 then some (.frame 3 true twoTable)
  else if a = 1 then some (.content (some 0))
  else if a = 3 then some (.content (some 2))
  else ([(30, Role.itemCache), (40, .itemCache), (50, .shared),
    (60, .linesBuffer), (70, .itemsBuffer), (80, .itemsBuffer),
    (90, .propertiesBuffer), (91, .propertiesBuffer)].lookup a).map Cell.allocation

theorem nested_plan : tablePlan nestedTable = some nestedReleases := by decide

theorem nested_allocations : Allocated nestedOwners nestedReleases := by
  intro x member
  simp only [nestedReleases, List.mem_cons, List.not_mem_nil, or_false] at member
  rcases member with rfl | rfl | rfl | rfl | rfl | rfl <;>
    unfold Allocation <;> decide

theorem nested_represented : Represented nestedOwners roomy nestedTable := by
  refine ⟨?_, nestedReleases, nested_plan, by decide, nested_allocations⟩
  simp [TableShape, PropertyShape, ArrayShape, nestedTable, roomy]

theorem nested_other_represented : Represented nestedOwners roomy twoTable := by
  refine ⟨?_, [⟨40, .itemCache⟩, ⟨91, .propertiesBuffer⟩], rfl, by decide, ?_⟩
  · simp [TableShape, PropertyShape, ArrayShape, twoTable, roomy]
  · intro x member
    simp only [List.mem_cons, List.not_mem_nil, or_false] at member
    rcases member with rfl | rfl <;> unfold Allocation <;> decide

theorem nested_residents (f c : Address) (b : Bool) (p : PropertyTable)
    (present : nestedOwners f = some (.frame c b p)) :
    (f = 0 ∧ p = nestedTable) ∨ (f = 2 ∧ p = twoTable) := by
  by_cases zero : f = 0
  · subst f
    simp [nestedOwners] at present
    exact Or.inl ⟨rfl, present.2.2.symm⟩
  · by_cases two : f = 2
    · subst f
      simp [nestedOwners] at present
      exact Or.inr ⟨rfl, present.2.2.symm⟩
    · by_cases one : f = 1
      · subst f; simp [nestedOwners] at present
      · by_cases three : f = 3
        · subst f; simp [nestedOwners] at present
        · simp only [nestedOwners, ite_eq_right zero, ite_eq_right two, ite_eq_right one, ite_eq_right three] at present
          cases entry : ([(30, Role.itemCache), (40, .itemCache), (50, .shared),
            (60, .linesBuffer), (70, .itemsBuffer), (80, .itemsBuffer),
            (90, .propertiesBuffer), (91, .propertiesBuffer)].lookup f) <;>
            simp [entry] at present

theorem nested_world : World nestedOwners roomy := by
  constructor
  · intro f c b p present
    rcases nested_residents f c b p present with ⟨_, rfl⟩ | ⟨_, rfl⟩
    · exact nested_represented
    · exact nested_other_represented
  · intro f g c d b e p q xs ys atF atG different px py
    rcases nested_residents f c b p atF with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;>
      rcases nested_residents g d e q atG with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
    · exact False.elim (different rfl)
    · simp [tablePlan, plan, footprint, optional, nestedTable, twoTable] at px py
      subst xs; subst ys
      simp [SeparatePlans]
    · simp [tablePlan, plan, footprint, optional, nestedTable, twoTable] at px py
      subst xs; subst ys
      simp [SeparatePlans]
    · exact False.elim (different rfl)

theorem nested_coherent : Coherent nestedOwners := by
  intro f c b p present
  rcases nested_residents f c b p present with ⟨rfl, _⟩ | ⟨rfl, _⟩
  · simp [nestedOwners] at present
    obtain ⟨rfl, rfl, rfl⟩ := present
    decide
  · simp [nestedOwners] at present
    obtain ⟨rfl, rfl, rfl⟩ := present
    decide

def nestedAfter : Heap :=
  referenceErase (detached nestedOwners 0 1 true) nestedReleases

theorem nested_execution : removeAll nestedOwners 0 = some nestedAfter :=
  phase_complete nestedOwners 0 1 true nestedTable nestedReleases
    (by decide) nested_plan (by decide) nested_allocations

theorem world_and_coherence_do_not_keep_selected_capture_alive :
    World nestedOwners roomy ∧ Coherent nestedOwners ∧
    removeAll nestedOwners 0 = some nestedAfter ∧
    World nestedAfter roomy ∧ Coherent nestedAfter ∧
    nestedAfter 0 = some (.frame 1 true emptyTable) ∧
    nestedAfter 30 = none ∧ nestedAfter 80 = none ∧
    nestedAfter 2 = some (.frame 3 true twoTable) ∧
    nestedAfter 40 = some (.allocation .itemCache) := by
  exact ⟨nested_world, nested_coherent, nested_execution,
    world_after_cleanup nestedOwners nestedAfter roomy 0 1 true nestedTable
      (by decide) nested_world nested_execution,
    (phase_contract nestedOwners nestedAfter 0 nested_coherent nested_execution).1,
    by decide, by decide, by decide, by decide, by decide⟩

end Destruction.Ownership
