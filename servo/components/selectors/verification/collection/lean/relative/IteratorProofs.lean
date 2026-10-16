/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.Funs
@[expose] public section
open Aeneas Aeneas.Std Result
open Collection
set_option linter.unusedVariables false
set_option linter.unusedSimpArgs false
namespace CollectionIteratorProofs
variable {I A D L N P BN BL C E : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Selector" => parser.Selector I A D L N P BN BL C E
local notation "Iter" => parser.SelectorIter I A D L N P BN BL C E

def step (component : Component) (iter : core.slice.iter.Iter Component) :
    Option Component × Iter :=
  match component with
  | .Combinator c => (none, ⟨iter, some c⟩)
  | component => (some component, ⟨iter, none⟩)

theorem next_in_bounds (slice : Slice Component) (index : Nat)
    (h : index < slice.len) :
    parser.SelectorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
      (⟨⟨slice, index⟩, none⟩ : Iter) =
    ok (step slice[index] ⟨slice, index + 1⟩) := by
  have h' : index < slice.val.length := by simpa using h
  simp only [parser.SelectorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next,
    core.option.Option.is_none, Option.isNone, massert, ite_true,
    core.slice.iter.IteratorSliceIter.next, dite_eq_left h, bind_ok,
    core.option.Option.Insts.CoreOpsTry_traitTry.branch]
  cases slice[index] <;> with_unfolding_all simp [step]

theorem next_exhausted (slice : Slice Component) (index : Nat)
    (h : ¬index < slice.len) :
    parser.SelectorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next
      (⟨⟨slice, index⟩, none⟩ : Iter) =
    ok (none, (⟨⟨slice, index⟩, none⟩ : Iter)) := by
  have h' : ¬index < slice.val.length := by simpa using h
  simp [parser.SelectorIter.Insts.CoreIterTraitsIteratorIteratorSharedAComponent.next,
    core.option.Option.is_none, massert, core.slice.iter.IteratorSliceIter.next,
    h, h', core.option.Option.Insts.CoreOpsTry_traitTry.branch,
    core.option.Option.Insts.CoreOpsTry_traitFromResidualOptionNever.from_residual]

theorem selector_iter (selector : Selector) :
    parser.Selector.iter selector = ok (⟨⟨selector._0.value.entries, 0⟩, none⟩ : Iter) := by
  simp [parser.Selector.iter, parser.Selector.iter_raw_match_order,
    servo_arc.Arc.Insts.CoreOpsDerefDeref.deref, servo_arc.HeaderSlice.slice,
    core.slice.Slice.iter]

#print axioms next_in_bounds
#print axioms next_exhausted
#print axioms selector_iter
end CollectionIteratorProofs
