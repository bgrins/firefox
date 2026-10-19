import SpacingRunAdmission

namespace HyphenTabSpacingAdmission

def binarySearch (values : Nat → Nat) (target low high : Nat) : Nat :=
  if active : low < high then
    let middle := low+(high-low)/2
    if target = values middle then middle
    else if target < values middle then binarySearch values target low middle
    else binarySearch values target (middle+1) high
  else low
termination_by high-low

def LowerCut (values : Nat → Nat) (target size cut : Nat) : Prop :=
  cut ≤ size ∧ ∀ i, i < size → (target ≤ values i ↔ cut ≤ i)

def Strict (values : Nat → Nat) (size : Nat) : Prop :=
  ∀ i j, i < j → j < size → values i < values j

theorem binary_search_cut (values : Nat → Nat) (target size cut low high : Nat)
    (partition : LowerCut values target size cut) (strict : Strict values size)
    (bounds : low ≤ cut ∧ cut ≤ high ∧ high ≤ size) :
    binarySearch values target low high = cut := by
  rw [binarySearch]
  split
  next active =>
    dsimp only
    have middleBound : low+(high-low)/2 < size := by omega
    split
    next matched =>
      have cutBelow := (partition.2 _ middleBound).mp (by omega)
      by_cases same : low+(high-low)/2 = cut
      · exact same
      · have cutBound : cut < size := by omega
        have cutValue := (partition.2 cut cutBound).mpr (Nat.le_refl _)
        have separated := strict cut (low+(high-low)/2) (by omega) middleBound
        omega
    next unmatched =>
      split
      next before =>
        have cutBelow := (partition.2 _ middleBound).mp (by omega)
        exact binary_search_cut values target size cut low _ partition strict
          ⟨bounds.1,cutBelow,by omega⟩
      next after =>
        have cutAfter : ¬ cut ≤ low+(high-low)/2 := by
          intro crossed
          have value := (partition.2 _ middleBound).mpr crossed
          omega
        exact binary_search_cut values target size cut _ high partition strict
          ⟨by omega,bounds.2⟩
  next finished => omega
termination_by high-low
decreasing_by all_goals omega

def lowerCut (target : Nat) : List Nat → Nat
  | [] => 0
  | value::rest => if target ≤ value then 0 else 1+lowerCut target rest

theorem sorted_lower_cut (values : List Nat) (target : Nat)
    (sorted : values.Pairwise (· ≤ ·)) :
    LowerCut (fun i => values[i]?.getD 0) target values.length (lowerCut target values) := by
  induction values with
  | nil => simp [LowerCut,lowerCut]
  | cons value rest ih =>
    have parts := List.pairwise_cons.mp sorted
    have later := ih parts.2
    unfold lowerCut
    split
    next before =>
      refine ⟨by simp,?_⟩
      intro i bound
      cases i with
      | zero => simpa using before
      | succ j =>
        have inner : j < rest.length := by simp at bound; omega
        have order := parts.1 rest[j] (List.getElem_mem inner)
        simp only [List.getElem?_cons_succ,List.getElem?_eq_getElem inner,Option.getD_some]
        omega
    next after =>
      refine ⟨by have := later.1; simp; omega,?_⟩
      intro i bound
      cases i with
      | zero => simp; omega
      | succ j =>
        have inner : j < rest.length := by simp at bound; omega
        simpa [Nat.add_comm] using later.2 j inner

def applyOffsets (offset length : Nat) : List Nat → List Nat
  | [] => []
  | value::rest => if value ≥ offset+length then []
      else (value-offset)::applyOffsets offset length rest

theorem tab_writes_bounded (offset length : Nat) (values : List Nat)
    (lower : ∀ value ∈ values, offset ≤ value) :
    ∀ index ∈ applyOffsets offset length values, index < length := by
  induction values with
  | nil => simp [applyOffsets]
  | cons value rest ih =>
    unfold applyOffsets
    split
    next stopped => simp
    next continuing =>
      intro index member
      rcases List.mem_cons.mp member with same | later
      · subst index; have low := lower value (by simp); omega
      · exact ih (by intro x hx; exact lower x (by simp [hx])) index later

theorem drop_cut_lower (values : List Nat) (target : Nat)
    (sorted : values.Pairwise (· ≤ ·)) :
    ∀ value ∈ values.drop (lowerCut target values), target ≤ value := by
  have partition := sorted_lower_cut values target sorted
  intro value member
  obtain ⟨index,bound,same⟩ := List.mem_iff_getElem.mp member
  have absoluteBound : lowerCut target values+index < values.length := by
    simp only [List.length_drop] at bound
    omega
  have lower := (partition.2 (lowerCut target values+index) absoluteBound).mpr (by omega)
  rw [List.getElem_drop] at same
  simp only [List.getElem?_eq_getElem absoluteBound,Option.getD_some] at lower
  omega

theorem native_tab_write_bounds (values : List Nat) (offset length : Nat)
    (sorted : values.Pairwise (· ≤ ·))
    (strict : Strict (fun i => values[i]?.getD 0) values.length) :
    let first := if offset = 0 then 0 else binarySearch (fun i => values[i]?.getD 0) offset 0 values.length
    ∀ index ∈ applyOffsets offset length (values.drop first), index < length := by
  dsimp only
  by_cases zero : offset = 0
  · simp only [zero,↓reduceIte,List.drop_zero]
    exact tab_writes_bounded 0 length values (by intro value member; omega)
  · rw [ite_eq_right zero]
    have partition := sorted_lower_cut values offset sorted
    rw [binary_search_cut _ offset values.length (lowerCut offset values) 0 values.length
      partition strict ⟨Nat.zero_le _,partition.1,Nat.le_refl _⟩]
    exact tab_writes_bounded offset length _ (drop_cut_lower values offset sorted)

end HyphenTabSpacingAdmission
