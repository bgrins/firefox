import PropertyPhase

namespace Destruction

def sampleTable : PropertyTable :=
  ⟨some 90, [.itemCache 30, .fragment 40,
    .shared 50 (some 60) [⟨some 70, [0, 2]⟩, ⟨none, [0]⟩, ⟨some 80, []⟩]]⟩

def sample : Heap := fun a =>
  if a = 0 then some (.frame 1 true sampleTable)
  else if a = 1 then some (.content (some 0))
  else if a = 2 then some (.frame 3 true emptyTable)
  else if a = 3 then some (.content (some 2))
  else ([(30, Role.itemCache), (40, .fragment), (50, .shared),
          (60, .linesBuffer), (70, .itemsBuffer), (80, .itemsBuffer),
          (90, .propertiesBuffer), (100, .itemCache)].lookup a).map Cell.allocation

def releases : List Release :=
  [⟨30, .itemCache⟩, ⟨40, .fragment⟩, ⟨70, .itemsBuffer⟩,
   ⟨80, .itemsBuffer⟩, ⟨60, .linesBuffer⟩, ⟨50, .shared⟩,
   ⟨90, .propertiesBuffer⟩]

def lookupAfter (h : Heap) (owner address : Address) : Option (Option Cell) :=
  (removeAll h owner).map (fun next => next address)

theorem sample_plan : tablePlan sampleTable = some releases := by
  decide

theorem sample_coherent : Coherent sample := by
  intro frame content bit props present
  by_cases zero : frame = 0
  · subst frame
    simp [sample] at present
    obtain ⟨rfl, rfl, rfl⟩ := present
    decide
  · by_cases one : frame = 1
    · subst frame; simp [sample] at present
    · by_cases two : frame = 2
      · subst frame
        simp [sample] at present
        obtain ⟨rfl, rfl, rfl⟩ := present
        decide
      · by_cases three : frame = 3
        · subst frame; simp [sample] at present
        · simp only [sample, ite_eq_right zero, ite_eq_right one, ite_eq_right two, ite_eq_right three] at present
          cases entry : ([(30, Role.itemCache), (40, .fragment), (50, .shared),
            (60, .linesBuffer), (70, .itemsBuffer), (80, .itemsBuffer),
            (90, .propertiesBuffer), (100, .itemCache)].lookup frame) <;>
            simp [entry] at present

def sampleAfter : Heap :=
  referenceErase (detached sample 0 1 true) releases

theorem sample_completeness : removeAll sample 0 = some sampleAfter := by
  apply phase_complete sample 0 1 true sampleTable releases
    (by decide) sample_plan (by decide)
  intro a member
  simp only [releases, List.mem_cons, List.not_mem_nil, or_false] at member
  rcases member with rfl | rfl | rfl | rfl | rfl | rfl | rfl <;>
    unfold Allocation <;> decide

theorem sample_after_coherent : Coherent sampleAfter :=
  (phase_contract sample sampleAfter 0 sample_coherent sample_completeness).1

theorem coherent_live_owner_with_freed_cache :
    Coherent sampleAfter ∧ sampleAfter 0 = some (.frame 1 true emptyTable) ∧
      primary sampleAfter 1 = some 0 ∧ sampleAfter 30 = none := by
  exact ⟨sample_after_coherent, by decide, by decide, by decide⟩

theorem captured_cache_freed : lookupAfter sample 0 30 = some none := by decide

theorem empty_allocated_array_freed : lookupAfter sample 0 80 = some none := by decide

theorem raw_frame_survives : lookupAfter sample 0 2 = some (sample 2) := by decide

theorem owner_survives_with_empty_table : lookupAfter sample 0 0 =
    some (some (.frame 1 true emptyTable)) := by decide

theorem primary_pointer_survives : lookupAfter sample 0 1 = some (sample 1) := by decide

theorem unrelated_allocation_survives : lookupAfter sample 0 100 = some (sample 100) := by decide

theorem table_buffer_freed : lookupAfter sample 0 90 = some none := by decide

def nonPrimarySample : Heap :=
  write (write (write sample 0 (some (.frame 1 false sampleTable)))
    1 (some (.content (some 2)))) 2 (some (.frame 1 true emptyTable))

theorem distinct_primary_remains :
    (removeAll nonPrimarySample 0).map (fun h => (bitRead h 0, primary h 1)) =
      some (some false, some 2) := by decide

def aliasTable : PropertyTable := ⟨none, [.itemCache 30, .itemCache 30]⟩

theorem double_owned_address_rejected :
    (removeAll (write sample 0 (some (.frame 1 true aliasTable))) 0).isNone = true := by decide

def sharedOwnedBufferTable : PropertyTable :=
  ⟨none, [.shared 50 (some 60) [⟨some 70, [0]⟩],
          .shared 40 (some 80) [⟨some 70, [2]⟩]]⟩

def sharedOwnedBufferHeap : Heap :=
  write (write (write sample 40 (some (.allocation .shared)))
    80 (some (.allocation .linesBuffer))) 0 (some (.frame 1 true sharedOwnedBufferTable))

theorem shared_buffers_initially_typed :
    Allocated sharedOwnedBufferHeap
      [⟨70, .itemsBuffer⟩, ⟨60, .linesBuffer⟩, ⟨50, .shared⟩,
       ⟨70, .itemsBuffer⟩, ⟨80, .linesBuffer⟩, ⟨40, .shared⟩] := by
  intro a member
  simp only [List.mem_cons, List.not_mem_nil, or_false] at member
  rcases member with rfl | rfl | rfl | rfl | rfl | rfl <;> unfold Allocation <;> decide

theorem distinct_roots_sharing_owned_buffer_rejected :
    (removeAll sharedOwnedBufferHeap 0).isNone = true := by decide

theorem wrong_allocation_role_rejected :
    (removeAll (write sample 30 (some (.allocation .fragment))) 0).isNone = true := by decide

theorem correct_allocation_role_admitted :
    (freeOne sample ⟨30, .itemCache⟩).isSome = true := by decide

def repeatedRawTable : PropertyTable :=
  ⟨some 90, [.shared 50 (some 60) [⟨some 70, [0, 0, 2, 2, 0]⟩,
                                 ⟨some 80, [2, 0, 2]⟩]]⟩

theorem repeated_raw_references_admitted :
    (removeAll (write sample 0 (some (.frame 1 true repeatedRawTable))) 0).map
      (fun h => (h 2, h 70, h 80)) = some (sample 2, none, none) := by decide

def danglingRawTable : PropertyTable :=
  ⟨none, [.shared 50 (some 60) [⟨some 70, [999, 999]⟩]]⟩

theorem dangling_raw_references_not_followed :
    (removeAll (write sample 0 (some (.frame 1 true danglingRawTable))) 0).map
      (fun h => (h 999, h 50)) = some (none, none) := by decide

theorem frame_as_owned_allocation_rejected :
    (removeAll (write sample 0 (some (.frame 1 true ⟨none, [.itemCache 2]⟩))) 0).isNone = true := by
  decide

theorem foreign_descriptor_rejected :
    (removeAll (write sample 0 (some (.frame 1 true ⟨none, [.foreign 30]⟩))) 0).isNone = true := by
  decide

def badIgnoreRole (h : Heap) (release : Release) : Option Heap :=
  match h release.address with
  | some (.allocation _) => some (write h release.address none)
  | _ => none

theorem erased_role_check_changes_admission :
    let wrong := write sample 30 (some (.allocation .fragment))
    (badIgnoreRole wrong ⟨30, .itemCache⟩).isSome = true ∧
      (freeOne wrong ⟨30, .itemCache⟩).isNone = true := by decide

def badOmitRoot (h : Heap) : Option Heap :=
  freeMany (detached h 0 1 true) releases.tail

theorem omitted_root_is_still_live :
    (badOmitRoot sample).map (fun h => h 30) = some (some (.allocation .itemCache)) := by decide

def badFollowRaw (h : Heap) : Heap :=
  referenceErase h (releases ++ [⟨0, .itemCache⟩, ⟨2, .itemCache⟩])

theorem following_raw_pointer_destroys_frame :
    badFollowRaw sample 2 = none ∧ sample 2 ≠ none := by decide

def badKeepTable (h : Heap) : Option Heap :=
  freeMany h releases

theorem missing_detach_leaves_dangling_table :
    (badKeepTable sample).map (fun h => h 0) = some (some (.frame 1 true sampleTable)) := by decide

theorem missing_detach_breaks_second_pass :
    ((badKeepTable sample).bind (fun h => removeAll h 0)).isNone = true := by decide

def repopulate (h : Heap) : Heap :=
  write h 0 (some (.frame 1 true ⟨none, [.itemCache 100]⟩))

theorem intervening_addition_makes_final_pass_nonempty :
    ((removeAll sample 0).map repopulate).map (fun h => h 100) =
      some (some (.allocation .itemCache)) ∧
    (((removeAll sample 0).map repopulate).bind (fun h => removeAll h 0)).map
      (fun h => h 100) = some none := by decide

end Destruction
