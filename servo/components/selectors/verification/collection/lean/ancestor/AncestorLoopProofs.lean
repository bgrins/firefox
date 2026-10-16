/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.AncestorProgressProofs
public import Normalized.LoopInvariantProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open AncestorProgressProofs
set_option linter.unusedSimpArgs false
namespace AncestorLoopProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Inst" => parser.SelectorImpl I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

inductive Reach (slice : Slice Component) (origin : Nat) : Nat → Prop
  | initial : Reach slice origin origin
  | advance (cursor picked : Nat) (before : Reach slice origin cursor)
      (emitted : Yield slice cursor picked) : Reach slice origin (picked + 1)

def GoodRegion (goodComponent : Component → Prop) (slice : Slice Component)
    (origin : Nat) : Prop :=
  ∀ cursor picked, Reach slice origin cursor → Yield slice cursor picked →
    ∀ h : picked < slice.len, goodComponent slice[picked]

theorem loop_preserves (inv : Array U32 4#usize → Nat → Prop) (inst : Inst)
    (quirks : context.QuirksMode) (slice : Slice Component) (origin index : Nat)
    (bound : index ≤ slice.len) (reached : Reach slice origin index)
    (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : inv hashes len.val)
    (goodComponent : Component → Prop)
    (component_contract : ∀ component, goodComponent component →
      ∀ hashes len, len.val < 4 → inv hashes len.val →
      parser.collect_component_hashes
        (parser.AncestorIter.Insts.SelectorsParserSelectorHashIterator inst)
        component quirks hashes len ⦃ r =>
          r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
          inv r.2.1 r.2.2.val ⦄)
    (good : GoodRegion goodComponent slice origin) :
    parser.collect_selector_hashes_loop
      (parser.AncestorIter.Insts.SelectorsParserSelectorHashIterator inst)
      (⟨⟨slice, index⟩, none⟩ : Iter) quirks hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      inv r.2.1 r.2.2.val ⦄ := by
  unfold parser.collect_selector_hashes_loop
  simp only [parser.AncestorIter.Insts.SelectorsParserSelectorHashIterator,
    parser.AncestorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent]
  rw [next_exact]
  cases eq : readAt slice (jump slice index) with
  | mk option iter =>
    simp only [bind_ok]
    cases option with
    | none => simp [before]; omega
    | some component =>
      have actual := next_exact slice index
      rw [eq] at actual
      obtain ⟨picked, emitted, hin, same, state, progress, afterBound⟩ :=
        next_yield slice index component iter bound actual
      subst iter
      have goodComponent' : goodComponent component := by
        rw [same]
        exact good index picked reached emitted hin
      have comp := component_contract component goodComponent' hashes len h before
      step as ⟨cont, updated, nextLen, hbound, hcontinue, hinvariant⟩
      cases cont with
      | false => simp_all
      | true =>
        exact loop_preserves inv inst quirks slice origin (picked + 1) afterBound
          (.advance index picked reached emitted) updated nextLen (hcontinue rfl)
          hinvariant goodComponent component_contract good
termination_by slice.val.length - index
decreasing_by
  have hlen : slice.val.length = slice.len := by simp
  omega

#print axioms loop_preserves
end AncestorLoopProofs
