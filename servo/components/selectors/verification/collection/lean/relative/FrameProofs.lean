/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.RecursiveCollectorProofs
public import Normalized.LoopInvariantProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open CollectionIteratorProofs CollectionStepProofs CollectionInvariantProofs CollectionLoopProofs
open RecursiveCollectionProofs CollectionLoopInvariantProofs
set_option linter.unusedSimpArgs false
set_option maxHeartbeats 1000000
namespace CollectionFrameProofs

def frame (initial : Array U32 4#usize) (start : Nat)
    (hashes : Array U32 4#usize) (len : Nat) : Prop :=
  start ≤ len ∧ ∀ i, i < start ∨ len ≤ i → hashes[i]! = initial[i]!

theorem store_frame (initial : Array U32 4#usize) (start : Nat)
    (hash : U32) (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : frame initial start hashes len.val) :
    storeHash (some hash) hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      frame initial start r.2.1 r.2.2.val ⦄ := by
  apply WP.spec_mono (store_some hash hashes len h)
  intro r hr
  rcases hr with ⟨hlen, harray, hflag⟩
  rw [hlen, harray, hflag]
  refine ⟨by omega, by simp, ?_⟩
  constructor
  · have := before.1; omega
  · intro i hi
    have hne : len.val ≠ i := by have := before.1; omega
    rw [Array.getElem!_Nat_set_ne hashes len i (masked hash) hne]
    apply before.2 i
    omega

variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Selector" => parser.Selector I A D L N P BN BL C E
local notation "Inst" => parser.SelectorImpl I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E
private theorem good_simple (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (depth : Nat) (component : Component)
    (hn : nested component = false) (hg : Good allowed inst quirks depth component) :
    Good allowed inst quirks 0 component := by
  cases depth with
  | zero => exact hg
  | succ depth => cases component <;> simp_all [nested, Good]

theorem component_preserves_frame (initial : Array U32 4#usize) (start : Nat) (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (depth : Nat) (component : Component)
    (hg : Good allowed inst quirks depth component)
    (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : frame initial start hashes len.val) :
    parser.collect_component_hashes
      (parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator inst)
      component quirks hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      frame initial start r.2.1 r.2.2.val ⦄ := by
  by_cases hn : nested component = false
  · have hg0 := good_simple allowed inst quirks depth component hn hg
    simp only [Good] at hg0
    rw [simple_component_step _ component hn]
    have hash_spec := hg0.2
    step as ⟨result, hresult⟩
    cases result with
    | none => simp [storeHash, before]; omega
    | some hash => exact store_frame initial start hash hashes len h before
  · cases depth with
    | zero =>
      simp only [Good] at hg
      exact False.elim (hn hg.1)
    | succ depth =>
      cases component <;> simp only [nested, Bool.false_eq_true, not_true_eq_false] at hn
      all_goals
        rename_i list
        simp only [Good] at hg
        unfold parser.collect_component_hashes
        simp only [parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator,
          parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator.for_inner]
        rw [slice_eq inst list]
        simp only [bind_ok]
        split
        · simp [before]
          omega
        · rename_i single
          have hs : (selectorsOf list).val.length = 1 := by scalar_tac
          step as ⟨selector, hselector⟩
          rw [selector_iter]
          simp only [bind_ok]
          rw [parser.collect_selector_hashes.eq_def]
          apply loop_preserves_invariant (frame initial start) inst quirks selector._0.value.entries 0 hashes len h before
            (Good allowed inst quirks depth)
          · intro child goodChild hashes len h before
            exact component_preserves_frame initial start allowed inst quirks depth child goodChild hashes len h before
          · apply hg hs selector
            subst selector
            simp
termination_by depth

theorem selector_preserves_frame (initial : Array U32 4#usize) (start : Nat) (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (depth : Nat) (selector : Selector)
    (good : goodSuffix (Good allowed inst quirks depth) selector._0.value.entries 0)
    (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : frame initial start hashes len.val) :
    (do
      let iter ← parser.Selector.iter selector
      parser.collect_selector_hashes
        (parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator inst)
        iter quirks hashes len) ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      frame initial start r.2.1 r.2.2.val ⦄ := by
  rw [selector_iter]
  simp only [bind_ok]
  rw [parser.collect_selector_hashes.eq_def]
  apply loop_preserves_invariant (frame initial start) inst quirks selector._0.value.entries 0 hashes len h before
    (Good allowed inst quirks depth)
  · intro child goodChild hashes len h before
    exact component_preserves_frame initial start allowed inst quirks depth child goodChild hashes len h before
  · exact good


def zeroTail (hashes : Array U32 4#usize) (len : Nat) : Prop :=
  ∀ i, len ≤ i → i < 4 → hashes[i]! = 0#u32

theorem relative_zero_tail (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (depth : Nat) (selector : Selector)
    (good : goodSuffix (Good allowed inst quirks depth) selector._0.value.entries 0) :
    parser.collect_relative_compound inst selector quirks ⦃ r =>
      r.2.val ≤ 4 ∧ zeroTail r.1 r.2.val ⦄ := by
  have spec := selector_preserves_frame (Array.repeat 4#usize 0#u32) 0 allowed inst
    quirks depth selector good (Array.repeat 4#usize 0#u32) 0#usize (by decide) (by simp [frame])
  unfold parser.collect_relative_compound
  simp only [selector_iter, bind_ok] at spec ⊢
  step as ⟨cont, hashes, len, hbound, hflag, hframe⟩
  refine ⟨hbound, ?_⟩
  intro i hi hlt
  rw [hframe.2 i (Or.inr hi)]
  have cases : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 := by omega
  rcases cases with h | h | h | h <;> subst i <;> simp [Array.getElem!_Nat_eq, Array.repeat_val]

#print axioms relative_zero_tail
#print axioms store_frame
#print axioms component_preserves_frame
#print axioms selector_preserves_frame
end CollectionFrameProofs
