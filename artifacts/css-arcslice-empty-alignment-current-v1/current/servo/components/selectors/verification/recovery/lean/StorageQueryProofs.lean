/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Generated.StyloBloomVerification

open Aeneas Aeneas.Std Result Bloom

namespace StorageQueryProofs

variable {E P : Type}
abbrev Stack := bloom_storage.RecoveryStack E P
abbrev Pushed := bloom_storage.PushedElement E
abbrev ElementVec := smallvec.SmallVec (Array (Pushed (E := E)) 16#usize) (Pushed (E := E))

structure QueryModel (E : Type) where
  values : ElementVec (E := E) → List (Pushed (E := E))
  len_spec : ∀ before,
    smallvec.SmallVec.len (ArrayT16.Insts.SmallvecArray (Pushed (E := E))) before
      ⦃ size => size.val = (values before).length ⦄
  deref_spec : ∀ before,
    smallvec.SmallVec.Insts.CoreOpsDerefDerefSlice.deref
      (ArrayT16.Insts.SmallvecArray (Pushed (E := E))) before
      ⦃ slice => slice.val = values before ⦄
  last_spec : ∀ slice : Slice (Pushed (E := E)),
    core.slice.Slice.last slice = ok slice.val.getLast?

theorem parent_exact (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (element : E) :
    style_bloom_recovery.RecoveryState_inst34_impl11.parent dom provider element =
      dom.traversal_parent element := rfl

theorem len_exact (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) :
    style_bloom_recovery.RecoveryState_inst34_impl11.len dom provider before =
      smallvec.SmallVec.len (ArrayT16.Insts.SmallvecArray (Pushed (E := E)))
        before.storage.elements := rfl

theorem len_contents (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : QueryModel E) (before : Stack) :
    style_bloom_recovery.RecoveryState_inst34_impl11.len dom provider before
      ⦃ size => size.val = (model.values before.storage.elements).length ⦄ :=
  model.len_spec before.storage.elements

theorem closure_exact (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (element : Pushed) :
    bloom_storage.RecoveryStateRecoveryStackE.current_parent.closure.Insts.CoreOpsFunctionFnOnceTupleShared1PushedElementE.call_once
      dom provider () element = ok element.element := rfl

theorem option_map_exact (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (element : Option (Pushed (E := E))) :
    core.option.Option.map
      (bloom_storage.RecoveryStateRecoveryStackE.current_parent.closure.Insts.CoreOpsFunctionFnOnceTupleShared1PushedElementE
        dom provider) element () = ok (element.map (fun pushed => pushed.element)) := by
  cases element with
  | none => rfl
  | some element =>
    simp only [core.option.Option.map_some, Option.map_some]
    change (do
      let mapped ← bloom_storage.RecoveryStateRecoveryStackE.current_parent.closure.Insts.CoreOpsFunctionFnOnceTupleShared1PushedElementE.call_once
        dom provider () element
      ok (some mapped)) = ok (some element.element)
    rw [closure_exact, bind_ok]

theorem current_parent_exact (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) (slice : Slice (Pushed (E := E))) (last : Option (Pushed (E := E)))
    (hderef : smallvec.SmallVec.Insts.CoreOpsDerefDerefSlice.deref
      (ArrayT16.Insts.SmallvecArray (Pushed (E := E))) before.storage.elements = ok slice)
    (hlast : core.slice.Slice.last slice = ok last) :
    style_bloom_recovery.RecoveryState_inst34_impl11.current_parent dom provider before =
      ok (last.map (fun pushed => pushed.element)) := by
  simp only [style_bloom_recovery.RecoveryState_inst34_impl11.current_parent,
    hderef, hlast, bind_ok]
  exact option_map_exact dom provider last

theorem current_parent_contents (dom : dom.TElement E)
    (provider : bloom_storage.HashProvider P E) (model : QueryModel E) (before : Stack) :
    style_bloom_recovery.RecoveryState_inst34_impl11.current_parent dom provider before
      ⦃ result => result = (model.values before.storage.elements).getLast?.map
        (fun pushed => pushed.element) ⦄ := by
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.current_parent
  step with model.deref_spec before.storage.elements as ⟨slice, hslice⟩
  rw [model.last_spec, bind_ok, option_map_exact]
  simp only [WP.spec_ok, hslice]

#print axioms parent_exact
#print axioms len_exact
#print axioms len_contents
#print axioms closure_exact
#print axioms option_map_exact
#print axioms current_parent_exact
#print axioms current_parent_contents

end StorageQueryProofs
