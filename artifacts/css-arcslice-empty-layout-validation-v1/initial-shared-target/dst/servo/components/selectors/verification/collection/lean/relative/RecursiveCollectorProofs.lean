/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.CollectorLoopProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open CollectionIteratorProofs CollectionStepProofs CollectionInvariantProofs CollectionLoopProofs
set_option linter.unusedSimpArgs false
set_option maxHeartbeats 1000000
namespace RecursiveCollectionProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Selector" => parser.Selector I A D L N P BN BL C E
local notation "SelectorList" => parser.SelectorList I A D L N P BN BL C E
local notation "Inst" => parser.SelectorImpl I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

def selectorsOf (list : SelectorList) : Slice Selector :=
  match list._0 with
  | .first selector => Slice.from [.mk selector] (by simp; scalar_tac)
  | .second selectors => selectors.value.entries

theorem slice_eq (inst : Inst) (list : SelectorList) :
    parser.SelectorList.slice inst list = ok (selectorsOf list) := by
  cases list with
  | mk list => cases list <;> rfl

def Good (allowed : U32 → Prop) (inst : Inst) (quirks : context.QuirksMode) :
    Nat → Component → Prop
  | 0, component => nested component = false ∧
      (parser.simple_selector_hash inst component quirks
        ⦃ result => ∀ raw ∈ result, allowed (masked raw) ⦄)
  | depth + 1, component =>
      match component with
      | .Is list | .Where list =>
          (selectorsOf list).val.length = 1 → ∀ selector ∈ (selectorsOf list).val,
            goodSuffix (Good allowed inst quirks depth) selector._0.value.entries 0
      | component => Good allowed inst quirks 0 component

private theorem good_simple (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (depth : Nat) (component : Component)
    (hn : nested component = false) (hg : Good allowed inst quirks depth component) :
    Good allowed inst quirks 0 component := by
  cases depth with
  | zero => exact hg
  | succ depth => cases component <;> simp_all [nested, Good]

theorem component_preserves (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (depth : Nat) (component : Component)
    (hg : Good allowed inst quirks depth component)
    (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : prefixAllowed allowed hashes len.val) :
    parser.collect_component_hashes
      (parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator inst)
      component quirks hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      prefixAllowed allowed r.2.1 r.2.2.val ⦄ := by
  by_cases hn : nested component = false
  · have hg0 := good_simple allowed inst quirks depth component hn hg
    simp only [Good] at hg0
    exact simple_component_preserves allowed _ component quirks hashes len h before hn hg0.2
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
          apply loop_preserves allowed inst quirks selector._0.value.entries 0 hashes len h before
            (Good allowed inst quirks depth)
          · intro child goodChild hashes len h before
            exact component_preserves allowed inst quirks depth child goodChild hashes len h before
          · apply hg hs selector
            subst selector
            simp
termination_by depth

theorem selector_preserves (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (depth : Nat) (selector : Selector)
    (good : goodSuffix (Good allowed inst quirks depth) selector._0.value.entries 0)
    (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : prefixAllowed allowed hashes len.val) :
    (do
      let iter ← parser.Selector.iter selector
      parser.collect_selector_hashes
        (parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator inst)
        iter quirks hashes len) ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      prefixAllowed allowed r.2.1 r.2.2.val ⦄ := by
  rw [selector_iter]
  simp only [bind_ok]
  rw [parser.collect_selector_hashes.eq_def]
  apply loop_preserves allowed inst quirks selector._0.value.entries 0 hashes len h before
    (Good allowed inst quirks depth)
  · intro child goodChild hashes len h before
    exact component_preserves allowed inst quirks depth child goodChild hashes len h before
  · exact good

#print axioms component_preserves
#print axioms selector_preserves
end RecursiveCollectionProofs
