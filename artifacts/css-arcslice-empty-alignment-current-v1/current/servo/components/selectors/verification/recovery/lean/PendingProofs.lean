/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import HashInsertProofs

open Aeneas Aeneas.Std Result Bloom HashInsertProofs

namespace PendingProofs

variable {E P : Type}
abbrev Stack := bloom_storage.RecoveryStack E P
abbrev Pending := smallvec.SmallVec (Array E 16#usize) E

def restore (before future : Stack (E := E) (P := P)) : Stack (E := E) (P := P) :=
  { before with storage := future.storage }

theorem push_exact (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) (element : E) (after : Pending)
    (h : smallvec.SmallVec.push (ArrayT16.Insts.SmallvecArray E) before.pending element = ok after) :
    style_bloom_recovery.RecoveryState_inst34_impl11.pending_push dom provider before element =
      ok ({ before with pending := after }, restore before) := by
  simp only [style_bloom_recovery.RecoveryState_inst34_impl11.pending_push, h, bind_ok]
  rfl

theorem pop_exact (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) (element : Option E) (after : Pending)
    (h : smallvec.SmallVec.pop (ArrayT16.Insts.SmallvecArray E) before.pending = ok (element, after)) :
    style_bloom_recovery.RecoveryState_inst34_impl11.pending_pop dom provider before =
      ok (element, { before with pending := after }, restore before) := by
  simp only [style_bloom_recovery.RecoveryState_inst34_impl11.pending_pop, h, bind_ok]
  rfl

theorem push_inv (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) (element : E) :
    OnSuccess (style_bloom_recovery.RecoveryState_inst34_impl11.pending_push dom provider before element)
      (fun result =>
        smallvec.SmallVec.push (ArrayT16.Insts.SmallvecArray E) before.pending element = ok result.1.pending ∧
        result.1.storage = before.storage ∧ result.2 = restore before) := by
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.pending_push
  refine onSuccess_bind_with _ _
    (fun pending => smallvec.SmallVec.push (ArrayT16.Insts.SmallvecArray E) before.pending element = ok pending)
    _ (by intro _ h; exact h) ?_
  intro pending h
  exact onSuccess_ok ⟨h, rfl, rfl⟩

theorem pop_inv (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) :
    OnSuccess (style_bloom_recovery.RecoveryState_inst34_impl11.pending_pop dom provider before)
      (fun result =>
        smallvec.SmallVec.pop (ArrayT16.Insts.SmallvecArray E) before.pending = ok (result.1, result.2.1.pending) ∧
        result.2.1.storage = before.storage ∧ result.2.2 = restore before) := by
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.pending_pop
  refine onSuccess_bind_with _ _
    (fun result => smallvec.SmallVec.pop (ArrayT16.Insts.SmallvecArray E) before.pending = ok result)
    _ (by intro _ h; exact h) ?_
  intro result h
  rcases result with ⟨element, pending⟩
  exact onSuccess_ok ⟨h, rfl, rfl⟩

theorem restore_fields (before future : Stack (E := E) (P := P)) :
    (restore before future).storage = future.storage ∧
    (restore before future).pending = before.pending ∧
    (restore before future).provider = before.provider := ⟨rfl, rfl, rfl⟩

theorem restore_compose (first second future : Stack (E := E) (P := P)) :
    restore first (restore second future) = restore first future := rfl

#print axioms push_exact
#print axioms pop_exact
#print axioms push_inv
#print axioms pop_inv
#print axioms restore_fields
#print axioms restore_compose

end PendingProofs
