/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import RecoveryProofs
import StorageInvariantProofs
import StorageQueryProofs

open Aeneas Aeneas.Std Result Bloom HashInsertProofs StorageInvariantProofs RecoveryProofs

noncomputable section

namespace StorageContractProofs

variable {E P : Type}
abbrev Stack := bloom_storage.RecoveryStack E P
abbrev PendingVec (E : Type) := smallvec.SmallVec (Array E 16#usize) E

def forwardOps (actual : style_bloom_recovery.RecoveryState_inst34 E P E) :
    style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E :=
  { coremarkerCopyInst := actual.coremarkerCopyInst, corecmpEqInst := actual.corecmpEqInst,
    parent := actual.parent, len := actual.len, current_parent := actual.current_parent,
    clear := fun before => do let result ← actual.clear before; ok result.1,
    pop := fun before => do let result ← actual.pop before; ok (result.1, result.2.1),
    push := fun before element => do let result ← actual.push before element; ok result.1,
    pending_push := fun before element => do let result ← actual.pending_push before element; ok result.1,
    pending_pop := fun before => do let result ← actual.pending_pop before; ok (result.1, result.2.1) }

structure LibraryModel (E : Type) (capacity : Nat) where
  sequence : SequenceModel E
  query : StorageQueryProofs.QueryModel E
  query_values : query.values = sequence.elementPush.values
  pending : PendingVec E → List E
  pending_pop : ∀ before, smallvec.SmallVec.pop (ArrayT16.Insts.SmallvecArray E) before
    ⦃ result => result.1 = (pending before).getLast? ∧ pending result.2 = (pending before).dropLast ⦄
  pending_push : ∀ before element, (pending before).length < capacity →
    smallvec.SmallVec.push (ArrayT16.Insts.SmallvecArray E) before element
      ⦃ after => pending after = pending before ++ [element] ⦄
  hash_len : ∀ before, smallvec.SmallVec.len (ArrayT64.Insts.SmallvecArray U32) before ⦃ _ => True ⦄
  element_empty : ∀ before, smallvec.SmallVec.is_empty
    (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E)) before
      ⦃ empty => empty = true ↔ sequence.elementPush.values before = [] ⦄
  element_push : ∀ before pushed, (sequence.elementPush.values before).length < capacity →
    smallvec.SmallVec.push (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E))
      before pushed ⦃ _ => True ⦄

def view (model : LibraryModel E capacity) (hashes : E → List U32) : StackView (Stack (E := E) (P := P)) E :=
  { chain := fun state => chain model.sequence state.storage,
    pending := fun state => (model.pending state.pending).reverse,
    valid := fun state => Valid model.sequence hashes state.storage }

def actual (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E) :=
  style_bloom_recovery.RecoveryState_inst34_impl11 dom provider

structure ProviderModel (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (hashes : E → List U32) where
  calls : StoragePushProofs.ProviderCalls provider hashes
  expected : ∀ element, provider.expected element ⦃ result => result.val = hashes element ⦄
  success : ∀ before element, Valid model.sequence hashes before →
    (chain model.sequence before).length < capacity →
    provider.insert element { filter := before.filter, hashes := before.pushed_hashes, count := 0#usize }
      ⦃ _ => True ⦄

theorem len_spec (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (hashes : E → List U32) (before : Stack) :
    (forwardOps (actual dom provider)).len before
      ⦃ size => size.val = ((view model hashes).chain before).length ⦄ := by
  apply WP.spec_mono (StorageQueryProofs.len_contents dom provider model.query before)
  intro size hsize
  simpa only [view, chain, List.length_reverse, List.length_map, model.query_values] using hsize

theorem current_parent_spec (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (hashes : E → List U32) (before : Stack) :
    (forwardOps (actual dom provider)).current_parent before
      ⦃ parent => parent = ((view model hashes).chain before).head? ⦄ := by
  apply WP.spec_mono (StorageQueryProofs.current_parent_contents dom provider model.query before)
  intro parent hparent
  simpa only [view, chain, List.head?_reverse, List.getLast?_map, model.query_values] using hparent

theorem clear_spec (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (hashes : E → List U32) (before : Stack)
    (valid : (view model hashes).valid before) :
    (forwardOps (actual dom provider)).clear before ⦃ after =>
      (view model hashes).valid after ∧ (view model hashes).chain after = [] ∧
      (view model hashes).pending after = (view model hashes).pending before ⦄ := by
  unfold forwardOps actual style_bloom_recovery.RecoveryState_inst34_impl11
  dsimp only
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.clear
  step with clear_valid dom model.sequence hashes before.storage valid as ⟨result, hvalid, hchain, _⟩
  rcases result with ⟨storage, back⟩
  dsimp! only
  simp only [bind_ok, WP.spec_ok]
  exact ⟨hvalid, hchain, rfl⟩

theorem pop_spec (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (optionModel : StoragePopProofs.OptionModel E)
    (hashes : E → List U32) (providerModel : ProviderModel dom provider model hashes)
    (before : Stack) (valid : (view model hashes).valid before) :
    (forwardOps (actual dom provider)).pop before ⦃ result =>
      (view model hashes).valid result.2 ∧
      (view model hashes).chain result.2 = ((view model hashes).chain before).tail ∧
      (view model hashes).pending result.2 = (view model hashes).pending before ∧
      result.1 = ((view model hashes).chain before).head? ⦄ := by
  unfold forwardOps actual style_bloom_recovery.RecoveryState_inst34_impl11
  dsimp only
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.pop
  step with pop_valid dom provider model.sequence optionModel hashes providerModel.expected
    before.storage valid as ⟨result, hvalid, hchain, hpopped, _, _⟩
  rcases result with ⟨popped, storage, back⟩
  dsimp! only
  simp only [bind_ok, WP.spec_ok]
  exact ⟨hvalid, hchain, rfl, hpopped⟩

theorem push_spec (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (hashes : E → List U32)
    (providerModel : ProviderModel dom provider model hashes)
    (before : Stack) (element : E) (valid : (view model hashes).valid before)
    (room : ((view model hashes).chain before).length < capacity)
    (parent : (forwardOps (actual dom provider)).parent element =
      ok ((view model hashes).chain before).head?) :
    (forwardOps (actual dom provider)).push before element ⦃ after =>
      (view model hashes).valid after ∧ (view model hashes).chain after = element :: (view model hashes).chain before ∧
      (view model hashes).pending after = (view model hashes).pending before ⦄ := by
  have elementRoom : (model.sequence.elementPush.values before.storage.elements).length < capacity := by
    simpa only [view, chain, List.length_reverse, List.length_map] using room
  have internal := StoragePushProofs.push_internal_success dom provider before.storage element
    (providerModel.success before.storage element valid room) model.hash_len
    (fun pushed => model.element_push before.storage.elements pushed elementRoom)
  have root : model.sequence.elementPush.values before.storage.elements = [] →
      dom.traversal_parent element = ok none := by
    intro empty
    simpa only [forwardOps, actual, style_bloom_recovery.RecoveryState_inst34_impl11,
      style_bloom_recovery.RecoveryState_inst34_impl11.parent, view, chain,
      empty, List.map_nil, List.reverse_nil, List.head?_nil] using parent
  have success := StoragePushProofs.push_success dom provider before.storage element
    model.sequence.elementPush.values (model.element_empty before.storage.elements) root internal
  have correct := StoragePushProofs.spec_of_success success
    (push_valid dom provider hashes model.sequence providerModel.calls before.storage element valid)
  unfold forwardOps actual style_bloom_recovery.RecoveryState_inst34_impl11
  dsimp only
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.push
  step with correct as ⟨result, hvalid, hchain, _⟩
  rcases result with ⟨storage, back⟩
  dsimp! only
  simp only [bind_ok, WP.spec_ok]
  exact ⟨hvalid, hchain, rfl⟩

theorem pending_push_spec (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (hashes : E → List U32)
    (before : Stack) (element : E) (valid : (view model hashes).valid before)
    (room : ((view model hashes).pending before).length < capacity) :
    (forwardOps (actual dom provider)).pending_push before element ⦃ after =>
      (view model hashes).valid after ∧ (view model hashes).chain after = (view model hashes).chain before ∧
      (view model hashes).pending after = element :: (view model hashes).pending before ⦄ := by
  have room' : (model.pending before.pending).length < capacity := by
    simpa only [view, List.length_reverse] using room
  unfold forwardOps actual style_bloom_recovery.RecoveryState_inst34_impl11
  dsimp only
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.pending_push
  step with model.pending_push before.pending element room' as ⟨pending, hpending⟩
  refine ⟨valid, rfl, ?_⟩
  simp only [view, hpending, List.reverse_append, List.reverse_cons, List.reverse_nil,
    List.nil_append, List.singleton_append]

theorem pending_pop_spec (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (hashes : E → List U32)
    (before : Stack) (valid : (view model hashes).valid before) :
    (forwardOps (actual dom provider)).pending_pop before ⦃ result =>
      (view model hashes).valid result.2 ∧ (view model hashes).chain result.2 = (view model hashes).chain before ∧
      (view model hashes).pending result.2 = ((view model hashes).pending before).tail ∧
      result.1 = ((view model hashes).pending before).head? ⦄ := by
  unfold forwardOps actual style_bloom_recovery.RecoveryState_inst34_impl11
  dsimp only
  unfold style_bloom_recovery.RecoveryState_inst34_impl11.pending_pop
  step with model.pending_pop before.pending as ⟨result, hpopped, hpending⟩
  rcases result with ⟨popped, pending⟩
  dsimp! only
  simp only [bind_ok, WP.spec_ok]
  refine ⟨valid, rfl, ?_, ?_⟩
  · simp only [view, hpending, List.tail_reverse]
  · simpa only [view, List.head?_reverse] using hpopped

theorem contract (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (optionModel : StoragePopProofs.OptionModel E)
    (hashes : E → List U32) (providerModel : ProviderModel dom provider model hashes) :
    StackContract (forwardOps (actual dom provider)) (view model hashes) capacity :=
  { len_spec := fun before _ => len_spec dom provider model hashes before,
    current_parent_spec := fun before _ => current_parent_spec dom provider model hashes before,
    pop_spec := pop_spec dom provider model optionModel hashes providerModel,
    push_spec := push_spec dom provider model hashes providerModel,
    pending_pop_spec := pending_pop_spec dom provider model hashes,
    pending_push_spec := pending_push_spec dom provider model hashes,
    clear_spec := clear_spec dom provider model hashes }

#print axioms len_spec
#print axioms current_parent_spec
#print axioms clear_spec
#print axioms pop_spec
#print axioms push_spec
#print axioms pending_push_spec
#print axioms pending_pop_spec
#print axioms contract

end StorageContractProofs
