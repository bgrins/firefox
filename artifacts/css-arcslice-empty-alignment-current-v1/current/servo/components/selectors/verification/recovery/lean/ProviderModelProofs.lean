/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import ProviderCompletionProofs
import StorageContractProofs
open Aeneas Aeneas.Std Result Bloom HashInsertProofs ProviderProofs ProviderTraceProofs
  StorageResourceProofs StorageInvariantProofs StorageContractProofs
noncomputable section
namespace ProviderModelProofs

abbrev actual {E : Type} (element : dom.TElement E) :=
  bloom_hashes.DomHashes.Insts.Stylo_bloom_verificationBloom_storageHashProvider element

structure Enumeration {E : Type} (element : dom.TElement E) (hashes : E → List U32) : Prop where
  insert : ∀ node before, each_relevant_element_hash_inst261 element
    (core.ops.function.FnMut_inst35_impl23 element) node (viewOfOld before) =
    callbackFold element (viewOfOld before) (hashes node)
  expected : ∀ node, each_relevant_element_hash_inst262 element
    (core.ops.function.FnMut_inst37_impl25 element) node (alloc.vec.Vec.new U32) =
    expectedFold element (alloc.vec.Vec.new U32) (hashes node)

theorem actual_calls {E : Type} (element : dom.TElement E) (hashes : E → List U32)
    (enumeration : Enumeration element hashes) :
    StoragePushProofs.ProviderCalls (actual element) hashes := by
  intro node before result success
  obtain ⟨backs, calls, back⟩ := provider_calls element node before (hashes node)
    result.1 result.2 (enumeration.insert node before) success
  refine ⟨backs, calls, ?_⟩
  rw [back]
  funext future
  exact (calls_close calls future).symm

theorem hash_capacity {E : Type} (model : SequenceModel E) (hashes : E → List U32)
    (before : bloom_storage.Storage E) (node : E) (capacity limit hashCapacity : Nat)
    (bounded : ∀ value, (hashes value).length ≤ limit)
    (fits : capacity * limit ≤ hashCapacity)
    (valid : Valid model hashes before) (room : (chain model before).length < capacity) :
    (model.hashPush.values before.pushed_hashes).length + (hashes node).length ≤ hashCapacity := by
  have total := push_capacity ((model.elementPush.values before.elements).map (·.element))
    node hashes limit capacity hashCapacity (fun value _ => bounded value)
    (by simpa only [chain, List.length_reverse] using room) fits
  rw [valid.2.1]
  simpa only [List.flatMap_map] using total

theorem actual_model {E : Type} (element : dom.TElement E)
    (model : LibraryModel E capacity) (hashes : E → List U32)
    (enumeration : Enumeration element hashes) (limit hashCapacity : Nat)
    (bounded : ∀ node, (hashes node).length ≤ limit)
    (elementFits : limit ≤ Usize.max) (fits : capacity * limit ≤ hashCapacity)
    (allocation : AllocationModel model.sequence.hashPush hashCapacity) :
    ProviderModel element (actual element) model hashes := by
  refine { calls := actual_calls element hashes enumeration, expected := ?_, success := ?_ }
  · intro node
    exact provider_expected element node (hashes node) (Nat.le_trans (bounded node) elementFits)
      (enumeration.expected node)
  · intro before node valid room
    have hashRoom := hash_capacity model.sequence hashes before node capacity limit hashCapacity
      bounded fits valid room
    exact ProviderCompletionProofs.provider_success element node model.sequence.hashPush hashCapacity
      allocation { filter := before.filter, hashes := before.pushed_hashes, count := 0#usize }
      (hashes node) (by simpa using Nat.le_trans (bounded node) elementFits) hashRoom
      (enumeration.insert node _)

#print axioms actual_calls
#print axioms hash_capacity
#print axioms actual_model
end ProviderModelProofs
