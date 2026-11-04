/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.AncestorSubjectProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open AncestorIteratorProofs AncestorContracts AncestorSubjectProofs
set_option linter.unusedSimpArgs false
set_option maxHeartbeats 1000000
namespace AncestorScanProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "SelectorList" => parser.SelectorList I A D L N P BN BL C E
local notation "Inst" => parser.SelectorImpl I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

def Ready (slice : Slice Component) (origin : Nat) (iter : Iter) : Prop :=
  ∃ finish, iter = (⟨⟨slice, finish⟩, none⟩ : Iter) ∧
    finish ≤ slice.len ∧ PhaseReach slice origin .ancestor finish

theorem scan_loop (inv : Array U32 4#usize → Nat → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (slice : Slice Component) (origin index : Nat)
    (bound : index ≤ slice.len) (reached : PhaseReach slice origin .subject index)
    (hashes : Array U32 4#usize) (len : Usize) (h : len.val < 4)
    (before : inv hashes len.val) (subjectGood : Component → Prop)
    (good : ∀ cursor, PhaseReach slice origin .subject cursor →
      ∀ h : cursor < slice.len, subjectGood slice[cursor])
    (child_contract : ∀ list : SelectorList,
      (subjectGood (.Is list) ∨ subjectGood (.Where list)) →
      (RecursiveCollectionProofs.selectorsOf list).val.length = 1 →
      ∀ selector ∈ (RecursiveCollectionProofs.selectorsOf list).val, ∀ hashes len,
      len.val < 4 → inv hashes len.val →
      parser.collect_ancestor_hashes inst
        (⟨⟨selector._0.value.entries, 0⟩, none⟩ : Iter) quirks hashes len ⦃ r =>
        r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧ inv r.2.1 r.2.2.val ⦄) :
    parser.scan_ancestor_hash_subject_loop inst
      (⟨⟨slice, index⟩, none⟩ : Iter) quirks hashes len ⦃ r =>
      r.2.2.2.val ≤ 4 ∧ (r.1 ≠ some false → r.2.2.2.val < 4) ∧
      inv r.2.2.1 r.2.2.2.val ∧
      (r.1 = none → Ready slice origin r.2.1) ⦄ := by
  unfold parser.scan_ancestor_hash_subject_loop
  rw [parser.collect_subject_ancestor_hashes.eq_def]
  have subject := subject_loop inv inst quirks slice origin index bound reached hashes len h before
    subjectGood good child_contract
  step as ⟨cont, iter, updated, nextLen, hbound, hcontinue, hinvariant, hfinished⟩
  cases cont with
  | false => simp_all
  | true =>
    obtain ⟨finish, marker, state, lower, upper, endpoint⟩ := hfinished rfl
    subst iter
    have room := hcontinue rfl
    have sequence : parser.SelectorIter.next_sequence
        (⟨⟨slice, finish⟩, marker⟩ : Iter) =
        ok (marker, (⟨⟨slice, finish⟩, none⟩ : Iter)) := by
      simp [parser.SelectorIter.next_sequence, core.option.Option.take]
    simp only [ite_true]
    rw [sequence]
    simp only [bind_ok]
    cases marker with
    | none => simp [hinvariant, hbound, room]
    | some c =>
      obtain ⟨position, hp, beforePos, endPos, subjectPos, atBoundary⟩ := endpoint
      have nextPhase := PhaseReach.boundary position hp c subjectPos atBoundary
      subst finish
      cases c with
      | Child | Descendant =>
        change WP.spec (ok _) _
        rw [WP.spec_ok]
        exact ⟨hbound, by simp [room], hinvariant,
          fun _ => ⟨position + 1, rfl, upper, nextPhase⟩⟩
      | NextSibling | LaterSibling =>
        change WP.spec (Aeneas.Std.bind (parser.SelectorIter.skip_until_ancestor
          (⟨⟨slice, position + 1⟩, none⟩ : Iter)) _) _
        rw [parser.SelectorIter.skip_until_ancestor, skip_exact]
        simp only [bind_ok]
        rw [WP.spec_ok]
        have bounds := skip_bounds slice (position + 1) (skipIndex slice (position + 1))
          (skip_path slice (position + 1))
        have hlen : slice.val.length = slice.len := by simp
        exact ⟨hbound, by simp [room], hinvariant,
          fun _ => ⟨skipIndex slice (position + 1), rfl, by omega, nextPhase⟩⟩
      | PseudoElement | SlotAssignment | Part =>
        exact scan_loop inv inst quirks slice origin (position + 1) upper nextPhase
          updated nextLen room hinvariant subjectGood good child_contract
termination_by slice.val.length - index
decreasing_by
  all_goals
    have hlen : slice.val.length = slice.len := by simp
    omega

#print axioms scan_loop
end AncestorScanProofs
