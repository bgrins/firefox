/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.AncestorScanProofs
public import Normalized.AncestorComponentProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open AncestorContracts AncestorSubjectProofs AncestorScanProofs AncestorComponentProofs
open AncestorLoopProofs CollectionStepProofs RecursiveCollectionProofs
set_option linter.unusedSimpArgs false
set_option maxHeartbeats 1000000
namespace AncestorFullProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Selector" => parser.Selector I A D L N P BN BL C E
local notation "SelectorList" => parser.SelectorList I A D L N P BN BL C E
local notation "Inst" => parser.SelectorImpl I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

theorem phase_reach (slice : Slice Component) (origin start cursor : Nat)
    (ready : PhaseReach slice origin .ancestor start) (reached : Reach slice start cursor) :
    PhaseReach slice origin .ancestor cursor := by
  induction reached with
  | initial => exact ready
  | advance cursor picked before emitted ih => exact .ancestorStep cursor picked ih emitted

theorem good_region (subjectGood ancestorGood : Component → Prop)
    (slice : Slice Component) (origin start : Nat)
    (good : FullRegion subjectGood ancestorGood slice origin)
    (ready : PhaseReach slice origin .ancestor start) :
    GoodRegion ancestorGood slice start := by
  intro cursor picked reached emitted hin
  exact good.2 cursor picked (phase_reach slice origin start cursor ready reached) emitted hin

theorem full_preserves (allowed : U32 → Prop) (initial : Array U32 4#usize)
    (start : Nat) (inst : Inst) (quirks : context.QuirksMode) (depth : Nat)
    (slice : Slice Component) (index : Nat) (bound : index ≤ slice.len)
    (good : FullGood allowed inst quirks depth slice index)
    (hashes : Array U32 4#usize) (len : Usize) (h : len.val < 4)
    (before : invariant allowed initial start hashes len.val) :
    parser.collect_ancestor_hashes inst (⟨⟨slice, index⟩, none⟩ : Iter) quirks hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      invariant allowed initial start r.2.1 r.2.2.val ⦄ := by
  have children : ∀ list : SelectorList,
      ((policies allowed inst quirks depth).1 (.Is list) ∨
       (policies allowed inst quirks depth).1 (.Where list)) →
      (selectorsOf list).val.length = 1 →
      ∀ selector ∈ (selectorsOf list).val, ∀ hashes len,
      len.val < 4 → invariant allowed initial start hashes len.val →
      parser.collect_ancestor_hashes inst
        (⟨⟨selector._0.value.entries, 0⟩, none⟩ : Iter) quirks hashes len ⦃ r =>
        r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
        invariant allowed initial start r.2.1 r.2.2.val ⦄ := by
    intro list childGood single selector member hashes len h before
    cases depth with
    | zero => simp [policies, nested] at childGood
    | succ depth =>
      have nestedGood : FullGood allowed inst quirks depth selector._0.value.entries 0 := by
        rcases childGood with childGood | childGood
        all_goals exact childGood single selector member
      exact full_preserves allowed initial start inst quirks depth selector._0.value.entries 0
        (by omega) nestedGood hashes len h before
  unfold parser.collect_ancestor_hashes
  rw [parser.scan_ancestor_hash_subject.eq_def]
  have scan := scan_loop (invariant allowed initial start) inst quirks slice index index bound
    (.initial) hashes len h before (policies allowed inst quirks depth).1 good.1 children
  step as ⟨result, iter, updated, nextLen, hbound, hcontinue, hinvariant, hready⟩
  cases result with
  | none =>
    obtain ⟨finish, state, upper, ready⟩ := hready rfl
    subst iter
    exact ancestor_region_preserves allowed initial start inst quirks depth slice finish upper
      (good_region _ _ slice index finish good ready) updated nextLen
      (hcontinue (by simp)) hinvariant
  | some cont =>
    cases cont <;> simp_all
termination_by depth

theorem ancestors_required_and_zero (allowed : U32 → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (depth : Nat) (selector : Selector)
    (good : FullGood allowed inst quirks depth selector._0.value.entries 0) :
    parser.collect_ancestors inst selector quirks ⦃ r =>
      r.2.val ≤ 4 ∧ CollectionInvariantProofs.prefixAllowed allowed r.1 r.2.val ∧
      CollectionFrameProofs.zeroTail r.1 r.2.val ⦄ := by
  have spec := full_preserves allowed (Array.repeat 4#usize 0#u32) 0 inst quirks depth
    selector._0.value.entries 0 (by omega) good (Array.repeat 4#usize 0#u32) 0#usize
    (by decide) (by simp [invariant, CollectionInvariantProofs.prefixAllowed, CollectionFrameProofs.frame])
  unfold parser.collect_ancestors
  rw [CollectionIteratorProofs.selector_iter]
  simp only [bind_ok]
  step as ⟨cont, hashes, len, hbound, hflag, hinvariant⟩
  refine ⟨hbound, hinvariant.1, ?_⟩
  intro i hi hlt
  rw [hinvariant.2.2 i (Or.inr hi)]
  have cases : i = 0 ∨ i = 1 ∨ i = 2 ∨ i = 3 := by omega
  rcases cases with h | h | h | h <;> subst i <;> simp [Array.getElem!_Nat_eq, Array.repeat_val]

#print axioms phase_reach
#print axioms good_region
#print axioms full_preserves
#print axioms ancestors_required_and_zero
end AncestorFullProofs
