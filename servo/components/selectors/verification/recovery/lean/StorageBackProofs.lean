/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import HashInsertProofs

open Aeneas Aeneas.Std Result Bloom HashInsertProofs

namespace StorageBackProofs

variable {E P : Type}

theorem skip {A B : Type} (run : Result A) (next : A → Result B) (post : B → Prop)
    (h : ∀ value, OnSuccess (next value) post) : OnSuccess (Aeneas.Std.bind run next) post :=
  onSuccess_bind_with run next (fun _ => True) post (by intro _ _; trivial) (fun value _ => h value)

theorem push_internal_back (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : bloom_storage.Storage E) (element : E) :
    OnSuccess (bloom_storage.Storage.push_internal dom provider before element)
      (fun result => result.2 = id) := by
  unfold bloom_storage.Storage.push_internal
  apply skip
  rintro ⟨sink, back⟩
  apply skip; intro length
  apply skip; intro high
  apply skip; intro pushed
  apply skip; intro elements
  exact onSuccess_ok rfl

theorem push_back (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : bloom_storage.Storage E) (element : E) :
    OnSuccess (bloom_storage.Storage.push dom provider before element)
      (fun result => result.2 = id) := by
  unfold bloom_storage.Storage.push
  apply skip; intro empty
  apply skip; intro checked
  exact push_internal_back dom provider before element

theorem clear_back (dom : dom.TElement E) (before : bloom_storage.Storage E) :
    OnSuccess (bloom_storage.Storage.clear dom before) (fun result => result.2 = id) := by
  unfold bloom_storage.Storage.clear
  apply skip; intro elements
  apply skip; intro slice
  apply skip; intro filter
  apply skip; intro hashes
  apply skip; intro zeroed
  apply skip; intro checked
  exact onSuccess_ok rfl

theorem pop_back (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : bloom_storage.Storage E) :
    OnSuccess (bloom_storage.Storage.pop dom provider before)
      (fun result => result.2.2 = id) := by
  unfold bloom_storage.Storage.pop
  apply skip
  rintro ⟨popped, elements⟩
  apply skip; intro branch
  cases branch with
  | Continue pushed =>
    apply skip; intro element
    apply skip; intro expected
    apply skip; rintro ⟨filter, hashes⟩
    exact onSuccess_ok rfl
  | Break residual =>
    apply skip; intro result
    exact onSuccess_ok rfl

abbrev Stack := bloom_storage.RecoveryStack E P

theorem stack_push_back (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) (element : E) :
    OnSuccess (style_bloom_recovery.RecoveryState_inst34_impl11.push dom provider before element)
      (fun result => ∀ future, (result.2 future).storage = future.storage) := by
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.push
  refine onSuccess_bind_with _ _ _ _ (push_back dom provider before.storage element) ?_
  rintro ⟨storage, back⟩ hback
  apply onSuccess_ok
  intro future
  change back = id at hback
  change back future.storage = future.storage
  rw [hback]
  rfl

theorem stack_clear_back (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) :
    OnSuccess (style_bloom_recovery.RecoveryState_inst34_impl11.clear dom provider before)
      (fun result => ∀ future, (result.2 future).storage = future.storage) := by
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.clear
  refine onSuccess_bind_with _ _ _ _ (clear_back dom before.storage) ?_
  rintro ⟨storage, back⟩ hback
  apply onSuccess_ok
  intro future
  change back = id at hback
  change back future.storage = future.storage
  rw [hback]
  rfl

theorem stack_pop_back (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) :
    OnSuccess (style_bloom_recovery.RecoveryState_inst34_impl11.pop dom provider before)
      (fun result => ∀ future, (result.2.2 future).storage = future.storage) := by
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.pop
  refine onSuccess_bind_with _ _ _ _ (pop_back dom provider before.storage) ?_
  rintro ⟨element, storage, back⟩ hback
  apply onSuccess_ok
  intro future
  change back = id at hback
  change back future.storage = future.storage
  rw [hback]
  rfl

theorem pending_push_back (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) (element : E) :
    OnSuccess (style_bloom_recovery.RecoveryState_inst34_impl11.pending_push dom provider before element)
      (fun result => ∀ future, (result.2 future).storage = future.storage) := by
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.pending_push
  apply skip; intro pending
  exact onSuccess_ok (fun _ => rfl)

theorem pending_pop_back (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (before : Stack) :
    OnSuccess (style_bloom_recovery.RecoveryState_inst34_impl11.pending_pop dom provider before)
      (fun result => ∀ future, (result.2.2 future).storage = future.storage) := by
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.pending_pop
  apply skip; rintro ⟨element, pending⟩
  exact onSuccess_ok (fun _ => rfl)

#print axioms push_internal_back
#print axioms push_back
#print axioms clear_back
#print axioms pop_back
#print axioms stack_push_back
#print axioms stack_clear_back
#print axioms stack_pop_back
#print axioms pending_push_back
#print axioms pending_pop_back

end StorageBackProofs
