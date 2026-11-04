/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import HashInsertProofs

open Aeneas Aeneas.Std Result Bloom BloomProofs StyleBloomProofs HashInsertProofs

set_option maxHeartbeats 1500000

namespace StoragePushProofs

abbrev ElementVec (E : Type) :=
  smallvec.SmallVec (Array (bloom_storage.PushedElement E) 16#usize) (bloom_storage.PushedElement E)

structure HashLengthModel (model : HashVecModel) where
  len_correct : ∀ hashes length,
    smallvec.SmallVec.len (ArrayT64.Insts.SmallvecArray U32) hashes = ok length →
    length.val = (model.values hashes).length

structure ElementPushModel (E : Type) where
  values : ElementVec E → List (bloom_storage.PushedElement E)
  push_correct : ∀ before element after,
    smallvec.SmallVec.push (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E))
      before element = ok after → values after = values before ++ [element]

def ProviderCalls {E P : Type} (provider : bloom_storage.HashProvider P E)
    (hashes : E → List U32) : Prop :=
  ∀ element initial, OnSuccess (provider.insert element initial) (fun result =>
    ∃ backs, Calls initial (hashes element) result.1 backs ∧
      result.2 = closeProvider initial backs)

theorem onSuccess_of_spec {A : Type} {run : Result A} {post : A → Prop}
    (h : run ⦃ post ⦄) : OnSuccess run post := by
  intro result heq
  rw [heq] at h
  simpa only [WP.spec_ok] using h

theorem push_internal_history {E P : Type} (elementOps : dom.TElement E)
    (provider : bloom_storage.HashProvider P E) (hashes : E → List U32)
    (model : HashVecModel) (lengthModel : HashLengthModel model)
    (elementModel : ElementPushModel E) (providerCalls : ProviderCalls provider hashes)
    (before : bloom_storage.Storage E) (element : E)
    (history : HighWaterHistory before.filter (model.values before.pushed_hashes)
      before.max_pushed_hashes.val) :
    OnSuccess (bloom_storage.Storage.push_internal elementOps provider before element)
      (fun result =>
        HighWaterHistory result.1.filter (model.values result.1.pushed_hashes)
          result.1.max_pushed_hashes.val ∧
        model.values result.1.pushed_hashes = model.values before.pushed_hashes ++ hashes element ∧
        (∃ pushed, pushed.element = element ∧ pushed.num_hashes.val = (hashes element).length ∧
          elementModel.values result.1.elements = elementModel.values before.elements ++ [pushed]) ∧
        result.2 = id) := by
  unfold bloom_storage.Storage.push_internal
  refine onSuccess_bind_with _ _ _ _ (providerCalls element _) ?_
  rintro ⟨after, back⟩ ⟨backs, calls, hback⟩
  have info := calls_accounting model calls
  dsimp only at calls hback info ⊢
  have hclose : back after = { after with count := 0#usize } := by
    exact Eq.trans (congrFun hback after) (calls_close calls after)
  change OnSuccess (do
    let length ← smallvec.SmallVec.len (ArrayT64.Insts.SmallvecArray U32) (back after).hashes
    let high ← style_bloom_filter.update_high_water before.max_pushed_hashes length
    let pushed ← bloom_storage.PushedElement.new elementOps element after.count
    let elements ← smallvec.SmallVec.push
      (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E)) before.elements pushed
    ok (({ filter := (back after).filter, elements := elements,
           pushed_hashes := (back after).hashes, max_pushed_hashes := high } : bloom_storage.Storage E), id)) _
  rw [hclose]
  refine onSuccess_bind_with _ _ (fun length => length.val = (model.values after.hashes).length) _
    (by intro length h; exact lengthModel.len_correct _ _ h) ?_
  intro length hlength
  refine onSuccess_bind_with _ _ (fun high => high.val = max before.max_pushed_hashes.val length.val) _
    (onSuccess_of_spec (update_high_water_spec _ _)) ?_
  intro high hhigh
  simp only [bloom_storage.PushedElement.new, dom.SendElement.new, bind_ok]
  refine onSuccess_bind_with _ _
    (fun elements => elementModel.values elements = elementModel.values before.elements ++
      [{ element, num_hashes := after.count }]) _
    (by intro elements h; exact elementModel.push_correct _ _ _ h) ?_
  intro elements helements
  apply onSuccess_ok
  refine ⟨?_, info.2.1, ?_, rfl⟩
  · have hh := calls_history model history calls
    have hl : length.val = (model.values before.pushed_hashes).length + (hashes element).length := by
      rw [hlength, info.2.1, List.length_append]
    simpa only [hhigh, hl] using hh
  · refine ⟨{ element, num_hashes := after.count }, rfl, ?_, helements⟩
    simpa using info.2.2

theorem push_history {E P : Type} (elementOps : dom.TElement E)
    (provider : bloom_storage.HashProvider P E) (hashes : E → List U32)
    (model : HashVecModel) (lengthModel : HashLengthModel model)
    (elementModel : ElementPushModel E) (providerCalls : ProviderCalls provider hashes)
    (before : bloom_storage.Storage E) (element : E)
    (history : HighWaterHistory before.filter (model.values before.pushed_hashes)
      before.max_pushed_hashes.val) :
    OnSuccess (bloom_storage.Storage.push elementOps provider before element)
      (fun result =>
        HighWaterHistory result.1.filter (model.values result.1.pushed_hashes)
          result.1.max_pushed_hashes.val ∧
        model.values result.1.pushed_hashes = model.values before.pushed_hashes ++ hashes element ∧
        (∃ pushed, pushed.element = element ∧ pushed.num_hashes.val = (hashes element).length ∧
          elementModel.values result.1.elements = elementModel.values before.elements ++ [pushed]) ∧
        result.2 = id) := by
  unfold bloom_storage.Storage.push
  refine onSuccess_bind_with _ _ (fun _ => True) _ (by intro _ _; trivial) ?_
  intro isEmpty _
  refine onSuccess_bind_with _ _ (fun _ => True) _ (by intro _ _; trivial) ?_
  intro _ _
  exact push_internal_history elementOps provider hashes model lengthModel elementModel
    providerCalls before element history

theorem push_internal_success {E P : Type} (elementOps : dom.TElement E)
    (provider : bloom_storage.HashProvider P E) (before : bloom_storage.Storage E) (element : E)
    (providerSuccess : provider.insert element
      { filter := before.filter, hashes := before.pushed_hashes, count := 0#usize }
      ⦃ _ => True ⦄)
    (lengthSuccess : ∀ hashes, smallvec.SmallVec.len (ArrayT64.Insts.SmallvecArray U32) hashes
      ⦃ _ => True ⦄)
    (elementPushSuccess : ∀ pushed,
      smallvec.SmallVec.push (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E))
        before.elements pushed ⦃ _ => True ⦄) :
    bloom_storage.Storage.push_internal elementOps provider before element ⦃ _ => True ⦄ := by
  unfold bloom_storage.Storage.push_internal
  step with providerSuccess as ⟨result, _⟩
  step with lengthSuccess _ as ⟨length⟩
  step with update_high_water_spec _ _ as ⟨high, _⟩
  simp only [bloom_storage.PushedElement.new, dom.SendElement.new, bind_ok]
  step with elementPushSuccess _

theorem spec_of_success {A : Type} {run : Result A} {post : A → Prop}
    (success : run ⦃ _ => True ⦄) (correct : OnSuccess run post) : run ⦃ post ⦄ := by
  cases run with
  | ret value => simpa only [WP.spec_ok] using correct value rfl
  | vis effect continuation => simp at success
  | div => simp at success

theorem push_success {E P : Type} (elementOps : dom.TElement E)
    (provider : bloom_storage.HashProvider P E) (before : bloom_storage.Storage E) (element : E)
    (elements : ElementVec E → List (bloom_storage.PushedElement E))
    (emptySpec : smallvec.SmallVec.is_empty
      (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E)) before.elements
      ⦃ empty => empty = true ↔ elements before.elements = [] ⦄)
    (rootCondition : elements before.elements = [] → elementOps.traversal_parent element = ok none)
    (internalSuccess : bloom_storage.Storage.push_internal elementOps provider before element
      ⦃ _ => True ⦄) :
    bloom_storage.Storage.push elementOps provider before element ⦃ _ => True ⦄ := by
  unfold bloom_storage.Storage.push
  step with emptySpec as ⟨empty, hempty⟩
  cases empty with
  | false => simpa only [Bool.false_eq_true, ↓reduceIte, bind_ok] using internalSuccess
  | true =>
    have hroot := rootCondition (hempty.mp rfl)
    simp only [↓reduceIte, hroot, bind_ok]
    simpa [massert] using internalSuccess

#print axioms push_internal_history
#print axioms push_history
#print axioms push_internal_success
#print axioms push_success


end StoragePushProofs
