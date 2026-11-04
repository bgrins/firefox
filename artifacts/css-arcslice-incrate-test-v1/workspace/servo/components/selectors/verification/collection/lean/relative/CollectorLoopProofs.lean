/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.IteratorProofs
public import Normalized.CollectorInvariantProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open CollectionIteratorProofs CollectionStepProofs CollectionInvariantProofs
set_option linter.unusedSimpArgs false
namespace CollectionLoopProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Inst" => parser.SelectorImpl I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

def goodSuffix (goodComponent : Component → Prop)
    (slice : Slice Component) (index : Nat) : Prop :=
  ∀ i, index ≤ i → ∀ h : i < slice.val.length,
    (∀ j, index ≤ j → ∀ hj : j < i, ∀ c,
      slice.val[j]'(by omega) ≠ parser.Component.Combinator c) →
    goodComponent slice.val[i]

theorem loop_preserves (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (slice : Slice Component) (index : Nat)
    (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : prefixAllowed allowed hashes len.val)
    (goodComponent : Component → Prop)
    (component_contract : ∀ component, goodComponent component →
      ∀ hashes len, len.val < 4 → prefixAllowed allowed hashes len.val →
      parser.collect_component_hashes
        (parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator inst)
        component quirks hashes len ⦃ r =>
          r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
          prefixAllowed allowed r.2.1 r.2.2.val ⦄)
    (good : goodSuffix goodComponent slice index) :
    parser.collect_selector_hashes_loop
      (parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator inst)
      (⟨⟨slice, index⟩, none⟩ : Iter) quirks hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      prefixAllowed allowed r.2.1 r.2.2.val ⦄ := by
  unfold parser.collect_selector_hashes_loop
  simp only [parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator,
    parser.SelectorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent]
  by_cases hin : index < slice.len
  · rw [next_in_bounds slice index hin]
    simp only [bind_ok]
    by_cases hc : ∃ c, slice[index] = parser.Component.Combinator c
    · rcases hc with ⟨c, hc⟩
      rw [hc]
      simp [CollectionIteratorProofs.step, before]
      omega
    · have hstep : step slice[index] ⟨slice, index + 1⟩ =
          (some slice[index], (⟨⟨slice, index + 1⟩, none⟩ : Iter)) := by
        cases heq : slice[index] <;> simp_all [CollectionIteratorProofs.step]
      rw [hstep]
      have hh := good index (by omega) (by simpa using hin) (by intro j hj hji; omega)
      have comp := component_contract slice[index] (by with_unfolding_all exact hh)
        hashes len h before
      step as ⟨cont, updated, nextLen, hbound, hcontinue, hallowed⟩
      cases cont with
      | false => simp_all
      | true =>
        have hnat : index < slice.val.length := by simpa using hin
        apply loop_preserves allowed inst quirks slice (index + 1) updated nextLen
          (hcontinue rfl) hallowed goodComponent component_contract
        intro i hi hbound between
        apply good i (by omega) hbound
        intro j hj hji c
        by_cases heq : j = index
        · subst j
          intro hcj
          apply hc
          exact ⟨c, by with_unfolding_all exact hcj⟩
        · exact between j (by omega) hji c
  · rw [next_exhausted slice index hin]
    simp [before]
    omega
termination_by slice.val.length - index
decreasing_by omega

#print axioms loop_preserves
end CollectionLoopProofs
