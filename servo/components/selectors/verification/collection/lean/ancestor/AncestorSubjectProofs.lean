/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.AncestorContracts
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open CollectionIteratorProofs RecursiveCollectionProofs AncestorContracts
set_option linter.unusedSimpArgs false
set_option maxHeartbeats 1000000
namespace AncestorSubjectProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Selector" => parser.Selector I A D L N P BN BL C E
local notation "SelectorList" => parser.SelectorList I A D L N P BN BL C E
local notation "Inst" => parser.SelectorImpl I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

def Finished (slice : Slice Component) (origin start : Nat) (iter : Iter) : Prop :=
  ∃ finish marker, iter = (⟨⟨slice, finish⟩, marker⟩ : Iter) ∧
    start ≤ finish ∧ finish ≤ slice.len ∧
    match marker with
    | none => finish = slice.len
    | some c => ∃ position : Nat, ∃ h : position < slice.len,
        start ≤ position ∧ finish = position + 1 ∧ PhaseReach slice origin .subject position ∧
        slice[position] = parser.Component.Combinator c

theorem finished_weaken (slice : Slice Component) (origin start middle : Nat)
    (iter : Iter) (h : start ≤ middle) (finished : Finished slice origin middle iter) :
    Finished slice origin start iter := by
  obtain ⟨finish, marker, same, lower, upper, endpoint⟩ := finished
  refine ⟨finish, marker, same, by omega, upper, ?_⟩
  cases marker with
  | none => exact endpoint
  | some c =>
    obtain ⟨position, hat, before, same, reached, component⟩ := endpoint
    exact ⟨position, hat, by omega, same, reached, component⟩

theorem subject_loop (inv : Array U32 4#usize → Nat → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (slice : Slice Component) (origin index : Nat)
    (bound : index ≤ slice.len) (reached : PhaseReach slice origin .subject index)
    (hashes : Array U32 4#usize) (len : Usize) (h : len.val < 4)
    (before : inv hashes len.val) (subjectGood : Component → Prop)
    (good : ∀ cursor, PhaseReach slice origin .subject cursor →
      ∀ h : cursor < slice.len, subjectGood slice[cursor])
    (child_contract : ∀ list : SelectorList,
      (subjectGood (.Is list) ∨ subjectGood (.Where list)) →
      (selectorsOf list).val.length = 1 →
      ∀ selector ∈ (selectorsOf list).val, ∀ hashes len,
      len.val < 4 → inv hashes len.val →
      parser.collect_ancestor_hashes inst
        (⟨⟨selector._0.value.entries, 0⟩, none⟩ : Iter) quirks hashes len ⦃ r =>
        r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧ inv r.2.1 r.2.2.val ⦄) :
    parser.collect_subject_ancestor_hashes_loop inst
      (⟨⟨slice, index⟩, none⟩ : Iter) quirks hashes len ⦃ r =>
      r.2.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.2.val < 4) ∧
      inv r.2.2.1 r.2.2.2.val ∧
      (r.1 = true → Finished slice origin index r.2.1) ⦄ := by
  unfold parser.collect_subject_ancestor_hashes_loop
  by_cases hin : index < slice.len
  · rw [next_in_bounds slice index hin]
    simp only [bind_ok]
    by_cases boundary : ∃ c, slice[index] = parser.Component.Combinator c
    · obtain ⟨c, hc⟩ := boundary
      rw [hc]
      simp only [step]
      change WP.spec (ok _) _
      rw [WP.spec_ok]
      change len.val ≤ 4 ∧ (true = true → len.val < 4) ∧ inv hashes len.val ∧
        (true = true → Finished slice origin index (⟨⟨slice, index + 1⟩, some c⟩ : Iter))
      refine ⟨by omega, by simpa using h, before, ?_⟩
      intro _
      exact ⟨index + 1, some c, rfl, by omega, by omega,
        index, hin, by omega, rfl, reached, hc⟩
    · have ordinary : ∀ c, slice[index] ≠ parser.Component.Combinator c := by simpa using boundary
      have plain : step slice[index] ⟨slice, index + 1⟩ =
          (some slice[index], (⟨⟨slice, index + 1⟩, none⟩ : Iter)) := by
        cases hc : slice[index] <;> with_unfolding_all simp_all [step]
      rw [plain]
      have current := good index reached hin
      have nextReached := PhaseReach.subjectStep index hin reached ordinary
      have rest : ∀ hashes len, len.val < 4 → inv hashes len.val →
          parser.collect_subject_ancestor_hashes_loop inst
            (⟨⟨slice, index + 1⟩, none⟩ : Iter) quirks hashes len ⦃ r =>
            r.2.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.2.val < 4) ∧
            inv r.2.2.1 r.2.2.2.val ∧
            (r.1 = true → Finished slice origin index r.2.1) ⦄ := by
        intro hashes len h before
        apply WP.spec_mono (subject_loop inv inst quirks slice origin (index + 1)
          (by omega) nextReached hashes len h before subjectGood good child_contract)
        intro r hr
        exact ⟨hr.1, hr.2.1, hr.2.2.1,
          fun cont => finished_weaken slice origin index (index + 1) _ (by omega) (hr.2.2.2 cont)⟩
      cases hc : slice[index] <;> with_unfolding_all simp only [hc] at current ⊢
      all_goals try exact rest hashes len h before
      all_goals
        rename_i list
        change WP.spec (Aeneas.Std.bind (parser.SelectorList.slice inst list) _) _
        rw [slice_eq inst list]
        with_unfolding_all simp only [bind_ok]
        split
        · rename_i single
          have hs : (selectorsOf list).val.length = 1 := by scalar_tac
          step as ⟨selector, hselector⟩
          rw [selector_iter]
          simp only [bind_ok]
          have child := child_contract list (by first | exact Or.inl current | exact Or.inr current)
            hs selector (by subst selector; simp) hashes len h before
          step as ⟨cont, updated, nextLen, hbound, hcontinue, hinvariant⟩
          cases cont with
          | false => simp_all
          | true => exact rest updated nextLen (hcontinue rfl) hinvariant
        · exact rest hashes len h before
  · rw [next_exhausted slice index hin]
    simp only [bind_ok]
    change WP.spec (ok _) _
    rw [WP.spec_ok]
    change len.val ≤ 4 ∧ (true = true → len.val < 4) ∧ inv hashes len.val ∧
      (true = true → Finished slice origin index (⟨⟨slice, index⟩, none⟩ : Iter))
    refine ⟨by omega, by simpa using h, before, ?_⟩
    intro _
    exact ⟨index, none, rfl, by omega, bound, by omega⟩
termination_by slice.val.length - index
decreasing_by
  have hlen : slice.val.length = slice.len := by simp
  omega

#print axioms finished_weaken
#print axioms subject_loop
end AncestorSubjectProofs
