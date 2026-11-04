/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.IteratorProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open CollectionIteratorProofs
set_option linter.unusedSimpArgs false
namespace AncestorIteratorProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

def isAncestor : parser.Combinator → Bool
  | .NextSibling | .LaterSibling => false
  | _ => true

def stops : Component → Bool
  | .Combinator c => isAncestor c
  | _ => false

def skipIndex (slice : Slice Component) (index : Nat) : Nat :=
  if h : index < slice.val.length then
    if stops slice.val[index] then index + 1 else skipIndex slice (index + 1)
  else index
termination_by slice.val.length - index

theorem skip_step (slice : Slice Component) (index : Nat) :
    parser.SelectorIter.skip_until_ancestor_loop (⟨⟨slice, index⟩, none⟩ : Iter) =
    if h : index < slice.len then
      if stops slice[index] then ok (⟨⟨slice, index + 1⟩, none⟩ : Iter)
      else parser.SelectorIter.skip_until_ancestor_loop (⟨⟨slice, index + 1⟩, none⟩ : Iter)
    else ok (⟨⟨slice, index⟩, none⟩ : Iter) := by
  rw [parser.SelectorIter.skip_until_ancestor_loop]
  by_cases h : index < slice.len
  · rw [dite_eq_left h, next_in_bounds slice index h]
    cases hc : slice[index] <;>
      simp [step, stops, core.option.Option.is_some, parser.SelectorIter.next_sequence,
        core.option.Option.take, core.option.Option.is_none_or,
        parser.SelectorIter.skip_until_ancestor.closure.Insts.CoreOpsFunctionFnOnceTupleCombinatorBool,
        parser.SelectorIter.skip_until_ancestor.closure.Insts.CoreOpsFunctionFnOnceTupleCombinatorBool.call_once]
    case Combinator c =>
      cases c <;> simp [parser.Combinator.is_ancestor, parser.Combinator.is_sibling, isAncestor]
  · rw [dite_eq_right h, next_exhausted slice index h]
    simp [core.option.Option.is_some, parser.SelectorIter.next_sequence,
      core.option.Option.take, core.option.Option.is_none_or]

theorem skip_exact (slice : Slice Component) (index : Nat) :
    parser.SelectorIter.skip_until_ancestor_loop (⟨⟨slice, index⟩, none⟩ : Iter) =
    ok (⟨⟨slice, skipIndex slice index⟩, none⟩ : Iter) := by
  rw [skip_step]
  by_cases h : index < slice.len
  · have hn : index < slice.val.length := by simpa using h
    rw [dite_eq_left h, skipIndex, dite_eq_left hn]
    change (if stops slice.val[index] then _ else _) = _
    by_cases hs : stops slice.val[index] = true
    · have hs' : stops slice.val[index] = true := hs
      with_unfolding_all simp [hs, hs']
    · have hs' : ¬ stops slice.val[index] = true := hs
      with_unfolding_all simpa [hs, hs'] using skip_exact slice (index + 1)
  · have hn : ¬ index < slice.val.length := by simpa using h
    rw [dite_eq_right h, skipIndex, dite_eq_right hn]
termination_by slice.val.length - index
decreasing_by simp_all; omega

inductive SkipPath (slice : Slice Component) : Nat → Nat → Prop
  | exhausted (index) (h : ¬ index < slice.val.length) : SkipPath slice index index
  | stop (index) (h : index < slice.val.length) (found : stops slice.val[index] = true) :
      SkipPath slice index (index + 1)
  | advance (index finish) (h : index < slice.val.length)
      (skipped : stops slice.val[index] = false) (rest : SkipPath slice (index + 1) finish) :
      SkipPath slice index finish

theorem skip_path (slice : Slice Component) (index : Nat) :
    SkipPath slice index (skipIndex slice index) := by
  rw [skipIndex]
  split
  next h =>
    split
    next found => exact .stop index h found
    next skipped => exact .advance index _ h (by simpa using skipped) (skip_path slice (index + 1))
  next h => exact .exhausted index h
termination_by slice.val.length - index
decreasing_by omega

theorem skip_bounds (slice : Slice Component) (start finish : Nat)
    (path : SkipPath slice start finish) :
    start ≤ finish ∧ finish ≤ max start slice.val.length := by
  induction path with
  | exhausted index h => omega
  | stop index h found => omega
  | advance index finish h skipped rest ih => omega

theorem skip_first_stop (slice : Slice Component) (start finish : Nat)
    (path : SkipPath slice start finish) (j : Nat)
    (lower : start ≤ j) (upper : j < finish) (h : j < slice.val.length)
    (found : stops slice.val[j] = true) : finish = j + 1 := by
  induction path with
  | exhausted index h => omega
  | stop index h found => omega
  | advance index finish h skipped rest ih =>
    by_cases eq : index = j
    · subst j
      simp [skipped] at found
    · exact ih (by omega) upper

theorem skip_contract (slice : Slice Component) (index : Nat) :
    ∃ finish, parser.SelectorIter.skip_until_ancestor (⟨⟨slice, index⟩, none⟩ : Iter) =
      ok (⟨⟨slice, finish⟩, none⟩ : Iter) ∧ SkipPath slice index finish := by
  exact ⟨skipIndex slice index, skip_exact slice index, skip_path slice index⟩

theorem is_ancestor_exact (c : parser.Combinator) :
    parser.Combinator.is_ancestor c = ok (isAncestor c) := by
  cases c <;> simp [parser.Combinator.is_ancestor, parser.Combinator.is_sibling, isAncestor]

theorem next_after_combinator (slice : Slice Component) (index : Nat)
    (h : index < slice.len) (c : parser.Combinator)
    (at_combinator : slice[index] = parser.Component.Combinator c) :
    parser.AncestorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
      (⟨⟨slice, index⟩, none⟩ : Iter) =
    parser.SelectorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
      (⟨⟨slice, if isAncestor c then index + 1 else skipIndex slice (index + 1)⟩, none⟩ : Iter) := by
  unfold parser.AncestorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
  rw [next_in_bounds slice index h, at_combinator]
  cases c <;>
    simp [step, core.option.Option.is_some, parser.SelectorIter.next_sequence,
      core.option.Option.take, core.option.Option.Insts.CoreOpsTry_traitTry.branch,
      parser.Combinator.is_ancestor, parser.Combinator.is_sibling, isAncestor,
      parser.SelectorIter.skip_until_ancestor, skip_exact]
  all_goals
    change Aeneas.Std.bind _ Result.ok = _
    exact Aeneas.Std.bind_pure _

theorem next_component (slice : Slice Component) (index : Nat)
    (h : index < slice.len)
    (component : ∀ c, slice[index] ≠ parser.Component.Combinator c) :
    parser.AncestorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
      (⟨⟨slice, index⟩, none⟩ : Iter) =
    ok (some slice[index], (⟨⟨slice, index + 1⟩, none⟩ : Iter)) := by
  unfold parser.AncestorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
  rw [next_in_bounds slice index h]
  cases hc : slice[index] <;>
    simp_all [step, core.option.Option.is_some]

theorem next_end (slice : Slice Component) (index : Nat)
    (h : ¬ index < slice.len) :
    parser.AncestorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
      (⟨⟨slice, index⟩, none⟩ : Iter) =
    ok (none, (⟨⟨slice, index⟩, none⟩ : Iter)) := by
  unfold parser.AncestorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
  rw [next_exhausted slice index h]
  simp [core.option.Option.is_some, parser.SelectorIter.next_sequence,
    core.option.Option.take, core.option.Option.Insts.CoreOpsTry_traitTry.branch,
    core.option.Option.Insts.CoreOpsTry_traitFromResidualOptionNever.from_residual]

#print axioms skip_step
#print axioms skip_exact
#print axioms skip_path
#print axioms skip_bounds
#print axioms skip_first_stop
#print axioms skip_contract
#print axioms is_ancestor_exact
#print axioms next_after_combinator
#print axioms next_component
#print axioms next_end
end AncestorIteratorProofs
