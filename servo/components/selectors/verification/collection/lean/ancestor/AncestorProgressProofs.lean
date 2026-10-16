/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.AncestorIteratorProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open CollectionIteratorProofs AncestorIteratorProofs
set_option linter.unusedSimpArgs false
namespace AncestorProgressProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

def readAt (slice : Slice Component) (index : Nat) : Option Component × Iter :=
  if h : index < slice.len then step slice[index] ⟨slice, index + 1⟩
  else (none, ⟨⟨slice, index⟩, none⟩)

def jump (slice : Slice Component) (index : Nat) : Nat :=
  if h : index < slice.len then
    match slice[index] with
    | .Combinator c => if isAncestor c then index + 1 else skipIndex slice (index + 1)
    | _ => index
  else index

theorem selector_read (slice : Slice Component) (index : Nat) :
    parser.SelectorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
      (⟨⟨slice, index⟩, none⟩ : Iter) = ok (readAt slice index) := by
  by_cases h : index < slice.len
  · rw [next_in_bounds slice index h, readAt, dite_eq_left h]
  · rw [next_exhausted slice index h, readAt, dite_eq_right h]

theorem next_exact (slice : Slice Component) (index : Nat) :
    parser.AncestorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
      (⟨⟨slice, index⟩, none⟩ : Iter) = ok (readAt slice (jump slice index)) := by
  by_cases h : index < slice.len
  · by_cases boundary : ∃ c, slice[index] = parser.Component.Combinator c
    · obtain ⟨c, hc⟩ := boundary
      rw [next_after_combinator slice index h c hc, selector_read]
      with_unfolding_all simp only [jump, dite_eq_left h, hc]
    · have hj : jump slice index = index := by
        unfold jump
        rw [dite_eq_left h]
        cases hc : slice[index] <;> with_unfolding_all simp_all
      have plain : ∀ (component : Component), (∀ c, component ≠ parser.Component.Combinator c) →
          step component ⟨slice, index + 1⟩ =
          (some component, (⟨⟨slice, index + 1⟩, none⟩ : Iter)) := by
        intro component ordinary
        cases component <;> simp_all [step]
      rw [next_component slice index h (by simpa using boundary), hj,
        readAt, dite_eq_left h, plain _ (by simpa using boundary)]
  · rw [next_end slice index h]
    with_unfolding_all simp only [jump, readAt, dite_eq_right h]

theorem jump_bounds (slice : Slice Component) (index : Nat)
    (bound : index ≤ slice.len) : index ≤ jump slice index ∧ jump slice index ≤ slice.len := by
  by_cases h : index < slice.len
  · by_cases boundary : ∃ c, slice[index] = parser.Component.Combinator c
    · obtain ⟨c, hc⟩ := boundary
      have hj : jump slice index = if isAncestor c then index + 1 else skipIndex slice (index + 1) := by
        with_unfolding_all simp only [jump, dite_eq_left h, hc]
      rw [hj]
      split
      · omega
      · have bounds := skip_bounds slice (index + 1) (skipIndex slice (index + 1))
          (skip_path slice (index + 1))
        have length : slice.val.length = slice.len := by simp
        omega
    · have hj : jump slice index = index := by
        unfold jump
        rw [dite_eq_left h]
        cases hc : slice[index] <;> with_unfolding_all simp_all
      rw [hj]
      exact ⟨Nat.le_refl _, bound⟩
  · rw [jump, dite_eq_right h]
    exact ⟨Nat.le_refl _, bound⟩

theorem read_some (slice : Slice Component) (index : Nat) (component : Component)
    (iter : Iter) (found : readAt slice index = (some component, iter)) :
    ∃ h : index < slice.len, component = slice[index] ∧
      (∀ c, component ≠ parser.Component.Combinator c) ∧
      iter = (⟨⟨slice, index + 1⟩, none⟩ : Iter) := by
  unfold readAt at found
  split at found
  next h =>
    refine ⟨h, ?_⟩
    cases hc : slice[index] <;> with_unfolding_all simp only [hc, step, Prod.mk.injEq, Option.some.injEq] at found
    all_goals first
      | simp at found
      | obtain ⟨rfl, rfl⟩ := found; simp
  next h => simp at found

def Yield (slice : Slice Component) (start picked : Nat) : Prop :=
  picked = jump slice start ∧ ∃ h : picked < slice.len,
    ∀ c, slice[picked] ≠ parser.Component.Combinator c

theorem next_yield (slice : Slice Component) (index : Nat) (component : Component)
    (iter : Iter) (bound : index ≤ slice.len)
    (found : parser.AncestorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
      (⟨⟨slice, index⟩, none⟩ : Iter) = ok (some component, iter)) :
    ∃ picked, Yield slice index picked ∧ ∃ h : picked < slice.len,
      component = slice[picked] ∧
      iter = (⟨⟨slice, picked + 1⟩, none⟩ : Iter) ∧
      index < picked + 1 ∧ picked + 1 ≤ slice.len := by
  rw [next_exact] at found
  have eq : readAt slice (jump slice index) = (some component, iter) := by simpa using found
  obtain ⟨h, same, ordinary, state⟩ := read_some slice (jump slice index) component iter eq
  have bounds := jump_bounds slice index bound
  refine ⟨jump slice index, ⟨rfl, h, ?_⟩, h, same, state, ?_, ?_⟩
  · simpa [← same] using ordinary
  · omega
  · omega

#print axioms selector_read
#print axioms next_exact
#print axioms jump_bounds
#print axioms read_some
#print axioms next_yield
end AncestorProgressProofs
