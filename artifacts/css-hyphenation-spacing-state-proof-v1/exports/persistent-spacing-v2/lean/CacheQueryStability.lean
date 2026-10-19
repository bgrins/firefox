import SpacingTabComposition

namespace CacheQueryStability
open HyphenSpacingPhases HyphenSpacingTabComposition HyphenTabSpacingAdmission

def linearSelect (first : Nat) : List (Tab Value) → List (Tab Value)
  | [] => []
  | tab::rest => if first ≤ tab.offset then tab::rest else linearSelect first rest

theorem drop_cut (first : Nat) (tabs : List (Tab Value)) :
    tabs.drop (lowerCut first (tabs.map Tab.offset)) = linearSelect first tabs := by
  induction tabs with
  | nil => simp [lowerCut,linearSelect]
  | cons tab rest ih =>
    by_cases before : first ≤ tab.offset
    · simp [lowerCut,linearSelect,before]
    · simpa [lowerCut,linearSelect,before,Nat.one_add] using ih

theorem selected_linear (first : Nat) (cache : HyphenTabValues.Cache Value)
    (sorted : (cache.entries.map Tab.offset).Pairwise (· ≤ ·))
    (strict : Strict (fun i => (cache.entries[i]?).map Tab.offset |>.getD 0) cache.entries.length) :
    selectedEntries cache first = linearSelect first cache.entries := by
  unfold selectedEntries
  by_cases zero : first = 0
  · subst first
    cases cache.entries <;> simp [linearSelect]
  · rw [ite_eq_right zero]
    have partition := sorted_lower_cut (cache.entries.map Tab.offset) first sorted
    have actual : LowerCut (fun i => (cache.entries[i]?).map Tab.offset |>.getD 0)
        first cache.entries.length (lowerCut first (cache.entries.map Tab.offset)) := by
      simpa using partition
    rw [binary_search_cut _ _ _ _ _ _ actual strict ⟨Nat.zero_le _,actual.1,Nat.le_refl _⟩]
    exact drop_cut _ _

theorem entries_after_empty (first finish : Nat) (tabs : List (Tab Value))
    (afterQuery : ∀ tab ∈ tabs, finish ≤ tab.offset) :
    tabEntries first finish tabs = [] := by
  cases tabs with
  | nil => rfl
  | cons tab rest =>
    have bound := afterQuery tab (by simp)
    simp [tabEntries,show ¬tab.offset < finish by omega]

theorem entries_append_after (first finish : Nat) (early late : List (Tab Value))
    (afterQuery : ∀ tab ∈ late, finish ≤ tab.offset) :
    tabEntries first finish (early++late) = tabEntries first finish early := by
  induction early with
  | nil => simpa [tabEntries] using entries_after_empty first finish late afterQuery
  | cons tab rest ih =>
    by_cases before : tab.offset < finish <;> simp [tabEntries,before,ih]

theorem select_append_after (first : Nat) (early late : List (Tab Value))
    (afterQuery : ∀ tab ∈ late, first ≤ tab.offset) :
    linearSelect first (early++late) = linearSelect first early ++ late := by
  induction early with
  | nil =>
    cases late with
    | nil => rfl
    | cons tab rest => simp [linearSelect,afterQuery tab (by simp)]
  | cons tab rest ih =>
    by_cases before : first ≤ tab.offset <;> simp [linearSelect,before,ih]

theorem applied_prefix_stable (first finish : Nat) (early late : List (Tab Value))
    (ordered : first ≤ finish) (afterQuery : ∀ tab ∈ late, finish ≤ tab.offset) :
    tabEntries first finish (linearSelect first (early++late)) =
      tabEntries first finish (linearSelect first early) := by
  rw [select_append_after _ _ _ (by intro tab member; have bound := afterQuery tab member; omega)]
  exact entries_append_after _ _ _ _ afterQuery

theorem native_applied_prefix_stable (first finish oldLimit newLimit : Nat)
    (early late : List (Tab Value)) (ordered : first ≤ finish)
    (afterQuery : ∀ tab ∈ late, finish ≤ tab.offset)
    (oldSorted : (early.map Tab.offset).Pairwise (· ≤ ·))
    (newSorted : ((early++late).map Tab.offset).Pairwise (· ≤ ·))
    (oldStrict : Strict (fun i => (early[i]?).map Tab.offset |>.getD 0) early.length)
    (newStrict : Strict (fun i => ((early++late)[i]?).map Tab.offset |>.getD 0) (early++late).length) :
    tabEntries first finish (selectedEntries ⟨early++late,newLimit⟩ first) =
      tabEntries first finish (selectedEntries ⟨early,oldLimit⟩ first) := by
  rw [selected_linear _ _ newSorted newStrict,selected_linear _ _ oldSorted oldStrict]
  exact applied_prefix_stable _ _ _ _ ordered afterQuery

end CacheQueryStability
