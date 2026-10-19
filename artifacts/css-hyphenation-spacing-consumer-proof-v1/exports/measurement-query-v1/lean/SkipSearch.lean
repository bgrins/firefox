import SkipRanges

namespace HyphenSkipSearch

open HyphenSkipRanges

def upperSearch (values : Nat → Nat) (offset low high : Nat) : Nat :=
  if low < high then
    let middle := low+(high-low)/2
    if offset < values middle then upperSearch values offset low middle
    else upperSearch values offset (middle+1) high
  else low
termination_by high-low
decreasing_by all_goals omega

def Cut (values : Nat → Nat) (offset size cut : Nat) : Prop :=
  cut ≤ size ∧ ∀ i, i < size → (offset < values i ↔ cut ≤ i)

theorem binary_search_finds_cut (values : Nat → Nat) (offset size cut low high : Nat)
    (partition : Cut values offset size cut)
    (bounds : low ≤ cut ∧ cut ≤ high ∧ high ≤ size) :
    upperSearch values offset low high = cut := by
  unfold upperSearch
  split
  next active =>
    have middleBound : low+(high-low)/2 < size := by omega
    dsimp only
    split
    next before =>
      have side := (partition.2 _ middleBound).mp before
      exact binary_search_finds_cut values offset size cut low _ partition ⟨bounds.1,side,by omega⟩
    next after =>
      have side : ¬ cut ≤ low+(high-low)/2 := by
        intro h
        exact after ((partition.2 _ middleBound).mpr h)
      exact binary_search_finds_cut values offset size cut _ high partition ⟨by omega,bounds.2⟩
  next inactive => omega
termination_by high-low
decreasing_by all_goals omega

def cutIndex (offset : Nat) : List Nat → Nat
  | [] => 0
  | x::rest => if offset < x then 0 else 1+cutIndex offset rest

theorem sorted_cut (values : List Nat) (offset : Nat)
    (sorted : values.Pairwise (· ≤ ·)) :
    Cut (fun i => values[i]?.getD 0) offset values.length (cutIndex offset values) := by
  induction values with
  | nil => simp [Cut,cutIndex]
  | cons x rest ih =>
    have sortedParts := List.pairwise_cons.mp sorted
    have later := ih sortedParts.2
    unfold cutIndex
    split
    next before =>
      refine ⟨by omega,?_⟩
      intro i hi
      constructor
      · intro _; omega
      · intro _
        cases i with
        | zero => simpa using before
        | succ j =>
          have hj : j < rest.length := by simp at hi; omega
          have member : rest[j] ∈ rest := List.getElem_mem hj
          have order := sortedParts.1 _ member
          simpa [List.getElem?_eq_getElem hj] using Nat.lt_of_lt_of_le before order
    next after =>
      refine ⟨by have := later.1; simp; omega,?_⟩
      intro i hi
      cases i with
      | zero => simp; omega
      | succ j =>
        have hj : j < rest.length := by simp at hi; omega
        simpa [Nat.add_comm] using later.2 j hj

theorem native_binary_search_sorted (values : List Nat) (offset : Nat)
    (sorted : values.Pairwise (· ≤ ·)) :
    upperSearch (fun i => values[i]?.getD 0) offset 0 values.length = cutIndex offset values :=
  binary_search_finds_cut _ _ _ _ _ _ (sorted_cut values offset sorted)
    ⟨Nat.zero_le _,(sorted_cut values offset sorted).1,Nat.le_refl _⟩

def selectedByIndex (ranges : List Range) (cut : Nat) : Option Range :=
  if cut = 0 then none else ranges[cut-1]?

def selectReverseBy (key : Range → Nat) (ranges : List Range) (offset : Nat) : Option Range :=
  ranges.find? fun r => decide (key r ≤ offset)

theorem sorted_index_selects_predecessor_by (key : Range → Nat) (ranges : List Range) (offset : Nat)
    (sorted : ranges.Pairwise fun a b => key a ≤ key b) :
    selectedByIndex ranges (cutIndex offset (ranges.map key)) =
      selectReverseBy key ranges.reverse offset := by
  induction ranges with
  | nil => rfl
  | cons r rest ih =>
    have parts := List.pairwise_cons.mp sorted
    have later := ih parts.2
    by_cases before : offset < key r
    · have noMatch : selectReverseBy key (r::rest).reverse offset = none := by
        apply List.find?_eq_none.mpr
        intro x hx
        have member : x ∈ r::rest := List.mem_reverse.mp hx
        have above : offset < key x := by
          rcases List.mem_cons.mp member with same | other
          · subst x; exact before
          · exact Nat.lt_of_lt_of_le before (parts.1 x other)
        simp; omega
      rw [noMatch]
      simp [selectedByIndex,cutIndex,before]
    · simp only [List.map_cons,cutIndex,ite_eq_right before]
      rw [List.reverse_cons]
      unfold selectReverseBy
      rw [List.find?_append]
      have headMatch : List.find? (fun x : Range => decide (key x ≤ offset)) [r] = some r := by
        simp; omega
      rw [headMatch]
      by_cases zero : cutIndex offset (rest.map key) = 0
      · have noneLater : selectReverseBy key rest.reverse offset = none := by
          rw [← later]
          simp [selectedByIndex,zero]
        change _ = (selectReverseBy key rest.reverse offset).or (some r)
        rw [noneLater]
        simp [selectedByIndex,zero]
      · have positive : 0 < cutIndex offset (rest.map key) := by omega
        have shifted : (1+cutIndex offset (rest.map key))-1 =
            (cutIndex offset (rest.map key)-1)+1 := by omega
        simp only [selectedByIndex,Nat.add_eq_zero_iff,Nat.one_ne_zero,false_and,↓reduceIte,shifted,
          List.getElem?_cons_succ]
        change _ = (selectReverseBy key rest.reverse offset).or (some r)
        rw [← later]
        simp only [selectedByIndex,ite_eq_right zero]
        have bounded := (sorted_cut (rest.map key) offset (List.pairwise_map.mpr parts.2)).1
        have ix : cutIndex offset (rest.map key)-1 < rest.length := by simp at bounded; omega
        rw [List.getElem?_eq_getElem ix]
        rfl

def selectReverse (ranges : List Range) (offset : Nat) : Option Range :=
  selectReverseBy Range.start ranges offset

theorem sorted_index_selects_predecessor (ranges : List Range) (offset : Nat)
    (sorted : ranges.Pairwise fun a b => a.start ≤ b.start) :
    selectedByIndex ranges (cutIndex offset (ranges.map Range.start)) =
      selectReverse ranges.reverse offset :=
  sorted_index_selects_predecessor_by Range.start ranges offset sorted

theorem wellformed_member_start (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) : ∀ r ∈ ranges, r.start ≤ count := by
  induction ranges generalizing count with
  | nil => simp
  | cons r rest ih =>
    intro x hx
    rcases List.mem_cons.mp hx with same | other
    · subst x; have := valid.1; unfold Range.finish at this; omega
    · have smaller := ih _ valid.2.2 x other
      have last := valid.1
      unfold Range.finish at last
      omega

theorem wellformed_reverse_sorted (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) :
    ranges.reverse.Pairwise fun a b => a.start ≤ b.start := by
  apply List.pairwise_reverse.mpr
  induction ranges generalizing count with
  | nil => exact List.Pairwise.nil
  | cons r rest ih =>
    apply List.pairwise_cons.mpr
    exact ⟨wellformed_member_start rest r.start valid.2.2,ih _ valid.2.2⟩

def evaluateSelected (offset : Nat) : Option Range → Nat
  | none => offset
  | some r => if offset < r.finish then r.start-r.delta else offset-r.nextDelta

theorem selection_evaluates_lookup (ranges : List Range) (offset : Nat) :
    evaluateSelected offset (selectReverse ranges offset) = lookupOriginal ranges offset := by
  induction ranges with
  | nil => rfl
  | cons r rest ih =>
    by_cases before : offset < r.start
    · have no : ¬ r.start ≤ offset := by omega
      simpa [selectReverse,selectReverseBy,List.find?,no,lookupOriginal,before] using ih
    · have yes : r.start ≤ offset := by omega
      simp [selectReverse,selectReverseBy,List.find?,yes,lookupOriginal,before,evaluateSelected]

theorem indexed_iterator_refines_lookup (ranges : List Range) (count offset : Nat)
    (valid : WellFormed ranges count) :
    let array := ranges.reverse
    let index := upperSearch (fun i => (array.map Range.start)[i]?.getD 0)
      offset 0 array.length
    evaluateSelected offset (selectedByIndex array index) = lookupOriginal ranges offset := by
  dsimp only
  have sorted := wellformed_reverse_sorted ranges count valid
  have searched := native_binary_search_sorted (ranges.reverse.map Range.start) offset
    (List.pairwise_map.mpr sorted)
  simp only [List.length_map] at searched
  rw [searched,sorted_index_selects_predecessor _ _ sorted,List.reverse_reverse,
    selection_evaluates_lookup]

theorem complete_original_iterator (ops : List Operation) (offset : Nat) :
    let state := build ⟨0,[]⟩ ops
    let array := state.reversedRanges.reverse
    let clamped := min offset state.count
    let index := upperSearch (fun i => (array.map Range.start)[i]?.getD 0)
      clamped 0 array.length
    evaluateSelected clamped (selectedByIndex array index) =
      HyphenSkipRanges.keptPrefix (ops.flatMap meaning) offset := by
  dsimp only
  rw [indexed_iterator_refines_lookup _ _ _ (constructor_builder_represents ops).2.1]
  exact constructor_original_coordinate ops offset

def skippedOffset (r : Range) : Nat := r.start-r.delta

theorem wellformed_member_skipped (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) : ∀ r ∈ ranges, skippedOffset r ≤ count-total ranges := by
  induction ranges generalizing count with
  | nil => simp
  | cons r rest ih =>
    have before := total_bound rest r.start valid.2.2
    have last := valid.1
    have delta := valid.2.1
    unfold Range.finish at last
    intro x hx
    rcases List.mem_cons.mp hx with same | other
    · subst x; unfold skippedOffset total; omega
    · have older := ih _ valid.2.2 x other
      simp only [total]
      omega

theorem wellformed_skipped_sorted (ranges : List Range) (count : Nat)
    (valid : WellFormed ranges count) :
    ranges.reverse.Pairwise fun a b => skippedOffset a ≤ skippedOffset b := by
  apply List.pairwise_reverse.mpr
  induction ranges generalizing count with
  | nil => exact List.Pairwise.nil
  | cons r rest ih =>
    apply List.pairwise_cons.mpr
    refine ⟨?_,ih _ valid.2.2⟩
    intro x hx
    have old := wellformed_member_skipped rest r.start valid.2.2 x hx
    simpa [skippedOffset,valid.2.1] using old

def evaluateSkipped (offset : Nat) : Option Range → Nat
  | none => offset
  | some r => r.finish+offset-skippedOffset r

theorem skipped_selection_evaluates_lookup (ranges : List Range) (offset : Nat) :
    evaluateSkipped offset (selectReverseBy skippedOffset ranges offset) = lookupSkipped ranges offset := by
  induction ranges with
  | nil => rfl
  | cons r rest ih =>
    by_cases before : offset < skippedOffset r
    · have no : ¬ skippedOffset r ≤ offset := by omega
      simp only [skippedOffset] at before no
      simpa [selectReverseBy,List.find?,no,lookupSkipped,skippedOffset,before] using ih
    · have yes : skippedOffset r ≤ offset := by omega
      simp only [skippedOffset] at before yes
      simp [selectReverseBy,List.find?,yes,lookupSkipped,skippedOffset,before,evaluateSkipped]

theorem indexed_skipped_iterator_refines_lookup (ranges : List Range) (count offset : Nat)
    (valid : WellFormed ranges count) :
    let array := ranges.reverse
    let index := upperSearch (fun i => (array.map skippedOffset)[i]?.getD 0)
      offset 0 array.length
    evaluateSkipped offset (selectedByIndex array index) = lookupSkipped ranges offset := by
  dsimp only
  have sorted := wellformed_skipped_sorted ranges count valid
  have searched := native_binary_search_sorted (ranges.reverse.map skippedOffset) offset
    (List.pairwise_map.mpr sorted)
  simp only [List.length_map] at searched
  rw [searched,sorted_index_selects_predecessor_by _ _ _ sorted,List.reverse_reverse,
    skipped_selection_evaluates_lookup]

theorem complete_skipped_iterator (ops : List Operation) (offset : Nat)
    (bound : offset ≤ ((ops.flatMap meaning).filter fun x => !x).length) :
    let state := build ⟨0,[]⟩ ops
    let array := state.reversedRanges.reverse
    let index := upperSearch (fun i => (array.map skippedOffset)[i]?.getD 0)
      offset 0 array.length
    let original := evaluateSkipped offset (selectedByIndex array index)
    original ≤ state.count ∧ HyphenSkipRanges.keptPrefix (ops.flatMap meaning) original = offset := by
  dsimp only
  rw [indexed_skipped_iterator_refines_lookup _ _ _ (constructor_builder_represents ops).2.1]
  exact constructor_skipped_coordinate ops offset bound

end HyphenSkipSearch
