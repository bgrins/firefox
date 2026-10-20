import BoundaryMutants

namespace OwnershipReview
open Destruction Destruction.Ownership

theorem capacity_is_an_external_choice :
    ArrayShape roomy (some 70) 4 ∧
    ¬ ArrayShape (fun _ => 0) (some 70) 4 := by simp [ArrayShape, roomy]

theorem same_heap_fails_under_zero_capacity :
    World nestedOwners roomy ∧ ¬ World nestedOwners (fun _ => 0) := by
  refine ⟨nested_world, ?_⟩
  intro world
  have shape := (world.represented 0 1 true nestedTable (by decide)).1
  simp [TableShape, ArrayShape, nestedTable] at shape

theorem full_world_allows_dangling_raw_reference :
    World nestedOwners roomy ∧ Coherent nestedOwners ∧
    nestedOwners 999 = none ∧
    (.shared 50 (some 60) [⟨some 70, [0, 2, 0, 999]⟩, ⟨some 80, []⟩]) ∈
      nestedTable.entries := by
  exact ⟨nested_world, nested_coherent, by decide, by decide⟩

def lone : Heap := fun address =>
  if address = 0 then some (.frame 1 true emptyTable) else none

theorem world_does_not_establish_primary_coherence :
    World lone roomy ∧ ¬ Coherent lone := by
  constructor
  · constructor
    · intro f c b p live
      by_cases zero : f = 0
      · subst f
        simp [lone] at live
        obtain ⟨rfl, rfl, rfl⟩ := live
        exact represented_empty lone roomy
      · simp [lone, zero] at live
    · intro f g c d b e p q xs ys atF atG different px py
      have fzero : f = 0 := by
        by_cases z : f = 0
        · exact z
        · simp [lone, z] at atF
      have gzero : g = 0 := by
        by_cases z : g = 0
        · exact z
        · simp [lone, z] at atG
      exact False.elim (different (fzero.trans gzero.symm))
  · intro coherent
    have bad := coherent 0 1 true emptyTable (by decide)
    have noPrimary : primary lone 1 = none := by decide
    simp [noPrimary] at bad

theorem foreign_descriptor_is_outside_the_world :
    ¬ Represented nestedOwners roomy ⟨some 90, [.foreign 30]⟩ := by
  intro represented
  have shape := represented.1
  simp [TableShape, PropertyShape] at shape

theorem different_roles_already_exclude_alias
    (h : Heap) (x y : Release) (liveX : Allocation h x)
    (liveY : Allocation h y) (different : x.role ≠ y.role) :
    x.address ≠ y.address := by
  intro same
  unfold Allocation at liveX liveY
  rw [same, liveY] at liveX
  have roles : y.role = x.role := by simpa using liveX
  exact different roles.symm

theorem freed_then_reused_address_has_no_generation_tag :
    nestedAfter 30 = none ∧
    (write nestedAfter 30 (some (.allocation .itemCache))) 30 = nestedOwners 30 := by
  decide

#print axioms capacity_is_an_external_choice
#print axioms same_heap_fails_under_zero_capacity
#print axioms full_world_allows_dangling_raw_reference
#print axioms world_does_not_establish_primary_coherence
#print axioms foreign_descriptor_is_outside_the_world
#print axioms different_roles_already_exclude_alias
#print axioms freed_then_reused_address_has_no_generation_tag
end OwnershipReview
