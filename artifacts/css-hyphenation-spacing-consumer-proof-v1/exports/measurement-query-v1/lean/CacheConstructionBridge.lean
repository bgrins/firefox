import PersistentTabs
import CacheQueryStability

namespace CacheConstructionBridge
open HyphenSpacingPhases HyphenTabValues PersistentTabs HyphenTabSpacingAdmission

theorem reference_offsets (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (input : Values Value) :
    (numericReference numeric providers start first finish input).entries.map Tab.offset =
      input.entries.map Tab.offset ++ collectedOffsets providers start first finish := by
  let state : State Value := ⟨input.offset,some ⟨input.entries,0⟩,0,[]⟩
  have same := loop_values numeric providers start first finish state
  have result := loop_offsets numeric providers start first finish state
  change (values (loop numeric providers start first finish state)).entries.map Tab.offset = _ at result
  rw [same] at result
  simpa [values,offsets,state] using result

theorem collected_bounds (providers : Providers Value) (start first finish : Nat)
    (ordered : start ≤ first) :
    ∀ offset ∈ collectedOffsets providers start first finish,
      first-start ≤ offset ∧ offset < finish-start := by
  intro offset member
  simp only [collectedOffsets,List.mem_filterMap] at member
  obtain ⟨index,inRange,selected⟩ := member
  have bounds := List.mem_range'.mp inRange
  split at selected
  next tab => simp at selected; omega
  next ordinary => simp at selected

theorem collected_order (providers : Providers Value) (start first finish : Nat)
    (ordered : start ≤ first) :
    (collectedOffsets providers start first finish).Pairwise (· < ·) := by
  by_cases active : first < finish
  · have next := collected_order providers start (first+1) finish (by omega)
    have bounds := collected_bounds providers start (first+1) finish (by omega)
    have length : finish-first = (finish-(first+1))+1 := by omega
    unfold collectedOffsets
    rw [length,List.range'_succ]
    by_cases tab : providers.isTab first = true
    · simp only [List.filterMap_cons,tab,↓reduceIte]
      apply List.pairwise_cons.mpr
      refine ⟨?_,next⟩
      intro later member
      have bound := bounds later member
      omega
    · simpa [tab,collectedOffsets] using next
  · simp [collectedOffsets,Nat.sub_eq_zero_of_le (by omega : finish ≤ first)]
termination_by finish-first

def reference (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (offset : Value) : Values Value :=
  numericReference numeric providers start start finish ⟨offset,[]⟩

theorem reference_sorted (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (offset : Value) :
    ((reference numeric providers start finish offset).entries.map Tab.offset).Pairwise (· < ·) := by
  unfold reference
  rw [reference_offsets]
  simpa using collected_order providers start start finish (Nat.le_refl _)

theorem reference_bounds (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (offset : Value) :
    ∀ tab ∈ (reference numeric providers start finish offset).entries, tab.offset < finish-start := by
  intro tab member
  have mapped : tab.offset ∈ (reference numeric providers start finish offset).entries.map Tab.offset := List.mem_map.mpr ⟨tab,member,rfl⟩
  simp only [reference,reference_offsets,List.map_nil,List.nil_append] at mapped
  exact (collected_bounds providers start start finish (Nat.le_refl _) _ mapped).2

theorem reference_strict (numeric : Numeric Value) (providers : Providers Value)
    (start finish : Nat) (offset : Value) :
    Strict (fun i => ((reference numeric providers start finish offset).entries[i]?).map Tab.offset |>.getD 0)
      (reference numeric providers start finish offset).entries.length := by
  have ready : HyphenTabCacheConstruction.Ready
      ⟨(reference numeric providers start finish offset).entries.map Tab.offset,finish-start⟩ := by
    refine ⟨reference_sorted _ _ _ _ _,?_⟩
    intro index member
    obtain ⟨tab,tabMember,rfl⟩ := List.mem_map.mp member
    exact reference_bounds _ _ _ _ _ tab tabMember
  simpa using HyphenTabCacheConstruction.ready_strict _ ready

theorem reference_extension (numeric : Numeric Value) (providers : Providers Value)
    (start first finish : Nat) (input : Values Value) (ordered : start ≤ first) :
    ∃ late, (numericReference numeric providers start first finish input).entries = input.entries++late ∧
      ∀ tab ∈ late, first-start ≤ tab.offset ∧ tab.offset < finish-start := by
  by_cases active : first < finish
  · have length : finish-first = (finish-(first+1))+1 := by omega
    have tail := reference_extension numeric providers start (first+1) finish
      (numericStep numeric providers start first input) (by omega)
    obtain ⟨late,tailEq,bounds⟩ := tail
    unfold numericReference
    rw [length,List.range'_succ,List.foldl_cons]
    change ∃ added, (numericReference numeric providers start (first+1) finish
      (numericStep numeric providers start first input)).entries = input.entries++added ∧ _
    rw [tailEq]
    by_cases tab : providers.isTab first = true
    · let spacing := providers.spacingWithoutTabs first
      let before := numeric.arithmetic.add input.offset spacing.before
      let entry : Tab Value := ⟨first-start,numeric.roundedDifference (numeric.nextTab before) before⟩
      refine ⟨entry::late,?_,?_⟩
      · simp [numericStep,tab,entry,before,spacing,List.append_assoc]
      · intro item member
        rcases List.mem_cons.mp member with same | later
        · subst item
          dsimp [entry]
          omega
        · have bound := bounds item later
          omega
    · refine ⟨late,?_,?_⟩
      · simp [numericStep,tab]
      · intro item member
        have bound := bounds item member
        omega
  · refine ⟨[],?_,by simp⟩
    simp [numericReference,Nat.sub_eq_zero_of_le (by omega : finish ≤ first)]
termination_by finish-first

theorem constructed_query_stable (numeric : Numeric Value) (providers : Providers Value)
    (start middle finish queryFirst queryEnd : Nat) (offset : Value)
    (startBound : start ≤ middle) (endBound : middle ≤ finish)
    (queryOrdered : queryFirst ≤ queryEnd) (queryCovered : queryEnd ≤ middle-start) :
    tabEntries queryFirst queryEnd (HyphenSpacingTabComposition.selectedEntries
      ⟨(reference numeric providers start finish offset).entries,finish-start⟩ queryFirst) =
    tabEntries queryFirst queryEnd (HyphenSpacingTabComposition.selectedEntries
      ⟨(reference numeric providers start middle offset).entries,middle-start⟩ queryFirst) := by
  obtain ⟨late,extension,bounds⟩ := reference_extension numeric providers start middle finish
    (reference numeric providers start middle offset) startBound
  have combination := reference_chunks numeric providers start start middle finish ⟨offset,[]⟩ startBound endBound
  change numericReference numeric providers start middle finish
    (reference numeric providers start middle offset) = reference numeric providers start finish offset at combination
  rw [combination] at extension
  have oldSorted := reference_sorted numeric providers start middle offset
  have newSorted := reference_sorted numeric providers start finish offset
  have oldStrict := reference_strict numeric providers start middle offset
  have newStrict := reference_strict numeric providers start finish offset
  rw [extension] at newSorted newStrict ⊢
  apply CacheQueryStability.native_applied_prefix_stable _ _ _ _ _ _ queryOrdered
  · intro tab member
    have bound := bounds tab member
    omega
  · exact oldSorted.imp (by intro a b order; omega)
  · exact newSorted.imp (by intro a b order; omega)
  · exact oldStrict
  · exact newStrict

def cacheWrites (first finish : Nat) (entries : List (Tab Value)) :=
  tabEntries first finish (HyphenSpacingTabComposition.selectedEntries ⟨entries,0⟩ first)

theorem history_query_stable (numeric : Numeric Value) (providers : Providers Value)
    (start queryFirst queryEnd : Nat) (offset : Value) (left right : List Nat)
    (leftBounded : ∀ finish ∈ left, start ≤ finish)
    (rightBounded : ∀ finish ∈ right, start ≤ finish)
    (queryOrdered : queryFirst ≤ queryEnd)
    (leftCovers : queryEnd ≤ covered start left-start)
    (rightCovers : queryEnd ≤ covered start right-start) :
    cacheWrites queryFirst queryEnd (values (queries numeric providers start (initial offset) left)).entries =
    cacheWrites queryFirst queryEnd (values (queries numeric providers start (initial offset) right)).entries := by
  rw [constructor_values _ _ _ _ _ leftBounded,constructor_values _ _ _ _ _ rightBounded]
  have leftStart := covered_lower start left
  have rightStart := covered_lower start right
  have leftEq := constructed_query_stable numeric providers start (min (covered start left) (covered start right))
    (covered start left) queryFirst queryEnd offset (by omega) (by omega) queryOrdered (by omega)
  have rightEq := constructed_query_stable numeric providers start (min (covered start left) (covered start right))
    (covered start right) queryFirst queryEnd offset (by omega) (by omega) queryOrdered (by omega)
  exact leftEq.trans rightEq.symm

end CacheConstructionBridge
