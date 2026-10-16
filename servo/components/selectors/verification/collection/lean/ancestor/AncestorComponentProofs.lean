/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.AncestorContracts
public import Normalized.FrameProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open CollectionIteratorProofs CollectionStepProofs CollectionInvariantProofs
open RecursiveCollectionProofs CollectionFrameProofs AncestorContracts AncestorLoopProofs
set_option linter.unusedSimpArgs false
set_option maxHeartbeats 1000000
namespace AncestorComponentProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Inst" => parser.SelectorImpl I A D L N P BN BL C E

def invariant (allowed : U32 → Prop) (initial : Array U32 4#usize) (start : Nat)
    (hashes : Array U32 4#usize) (len : Nat) : Prop :=
  prefixAllowed allowed hashes len ∧ frame initial start hashes len

private theorem good_simple (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (depth : Nat) (component : Component)
    (hn : nested component = false)
    (hg : (policies allowed inst quirks depth).2 component) :
    nested component = false ∧ (parser.simple_selector_hash inst component quirks
      ⦃ result => ∀ raw ∈ result, allowed (masked raw) ⦄) := by
  cases depth with
  | zero => exact hg
  | succ depth => cases component <;> simp_all [nested, policies]

theorem store_invariant (allowed : U32 → Prop) (initial : Array U32 4#usize)
    (start : Nat) (hash : U32) (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : invariant allowed initial start hashes len.val)
    (required : allowed (masked hash)) :
    storeHash (some hash) hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      invariant allowed initial start r.2.1 r.2.2.val ⦄ := by
  apply WP.spec_mono (store_some hash hashes len h)
  intro r hr
  rcases hr with ⟨hlen, harray, hflag⟩
  rw [hlen, harray, hflag]
  refine ⟨by omega, by simp, ?_, ?_⟩
  · intro i hi
    by_cases heq : len.val = i
    · rw [Array.getElem!_Nat_set_eq hashes len i (masked hash) ⟨heq, by scalar_tac⟩]
      exact required
    · rw [Array.getElem!_Nat_set_ne hashes len i (masked hash) heq]
      exact before.1 i (by omega)
  · constructor
    · have := before.2.1; omega
    · intro i hi
      have hne : len.val ≠ i := by have := before.2.1; omega
      rw [Array.getElem!_Nat_set_ne hashes len i (masked hash) hne]
      apply before.2.2 i
      omega

theorem component_preserves (allowed : U32 → Prop) (initial : Array U32 4#usize)
    (start : Nat) (inst : Inst) (quirks : context.QuirksMode) (depth : Nat)
    (component : Component) (hg : (policies allowed inst quirks depth).2 component)
    (hashes : Array U32 4#usize) (len : Usize) (h : len.val < 4)
    (before : invariant allowed initial start hashes len.val) :
    parser.collect_component_hashes
      (parser.AncestorIter.Insts.SelectorsParserSelectorHashIterator inst)
      component quirks hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      invariant allowed initial start r.2.1 r.2.2.val ⦄ := by
  by_cases hn : nested component = false
  · have hg0 := good_simple allowed inst quirks depth component hn hg
    rw [simple_component_step _ component hn]
    have hash_spec := hg0.2
    step as ⟨result, hresult⟩
    cases result with
    | none => simp [storeHash, before]; omega
    | some hash =>
      exact store_invariant allowed initial start hash hashes len h before (hresult hash (by simp))
  · cases depth with
    | zero => exact False.elim (hn hg.1)
    | succ depth =>
      cases component <;> simp only [nested, Bool.false_eq_true, not_true_eq_false] at hn
      all_goals
        rename_i list
        simp only [policies] at hg
        unfold parser.collect_component_hashes
        simp only [parser.AncestorIter.Insts.SelectorsParserSelectorHashIterator,
          parser.AncestorIter.Insts.SelectorsParserSelectorHashIterator.for_inner]
        rw [slice_eq inst list]
        simp only [bind_ok]
        split
        · simp [before]; omega
        · rename_i single
          have hs : (selectorsOf list).val.length = 1 := by scalar_tac
          step as ⟨selector, hselector⟩
          rw [selector_iter]
          simp only [bind_ok]
          rw [parser.collect_selector_hashes.eq_def]
          apply AncestorLoopProofs.loop_preserves (invariant allowed initial start) inst quirks
            selector._0.value.entries 0 0 (by omega) (.initial) hashes len h before
            (policies allowed inst quirks depth).2
          · intro child goodChild hashes len h before
            exact component_preserves allowed initial start inst quirks depth child goodChild hashes len h before
          · apply hg hs selector
            subst selector
            simp
termination_by depth

theorem ancestor_region_preserves (allowed : U32 → Prop) (initial : Array U32 4#usize)
    (start : Nat) (inst : Inst) (quirks : context.QuirksMode) (depth : Nat)
    (slice : Slice Component) (index : Nat) (bound : index ≤ slice.len)
    (good : GoodRegion (policies allowed inst quirks depth).2 slice index)
    (hashes : Array U32 4#usize) (len : Usize) (h : len.val < 4)
    (before : invariant allowed initial start hashes len.val) :
    parser.collect_selector_hashes
      (parser.AncestorIter.Insts.SelectorsParserSelectorHashIterator inst)
      ⟨⟨slice, index⟩, none⟩ quirks hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      invariant allowed initial start r.2.1 r.2.2.val ⦄ := by
  rw [parser.collect_selector_hashes.eq_def]
  apply AncestorLoopProofs.loop_preserves (invariant allowed initial start) inst quirks
    slice index index bound (.initial) hashes len h before
    (policies allowed inst quirks depth).2
  · intro component hg hashes len h before
    exact component_preserves allowed initial start inst quirks depth component hg hashes len h before
  · exact good

#print axioms store_invariant
#print axioms component_preserves
#print axioms ancestor_region_preserves
end AncestorComponentProofs
