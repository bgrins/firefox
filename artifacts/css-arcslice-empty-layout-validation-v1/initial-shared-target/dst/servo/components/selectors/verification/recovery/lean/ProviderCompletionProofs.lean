/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import ProviderTraceProofs
import StorageResourceProofs
open Aeneas Aeneas.Std Result Bloom HashInsertProofs ProviderProofs StorageResourceProofs
noncomputable section
namespace ProviderCompletionProofs

theorem calls_fold {before after : Sink} {hashes : List U32} {backs : List (Sink → Sink)}
    (calls : Calls before hashes after backs) : originalFold before hashes = ok after := by
  induction calls with
  | nil sink => rfl
  | cons run _ ih =>
    simp only [originalFold, run, bind_ok]
    exact ih

theorem fold_success (model : HashVecModel) (capacity : Nat)
    (allocation : AllocationModel model capacity) (hashes : List U32) (before : Sink)
    (countRoom : before.count.val + hashes.length ≤ Usize.max)
    (hashRoom : (model.values before.hashes).length + hashes.length ≤ capacity) :
    originalFold before hashes ⦃ _ => True ⦄ := by
  obtain ⟨after, backs, calls⟩ := calls_exist model capacity allocation hashes before countRoom hashRoom
  rw [calls_fold calls]
  simp

theorem provider_success {E : Type} (element : dom.TElement E) (node : E)
    (model : HashVecModel) (capacity : Nat) (allocation : AllocationModel model capacity)
    (before : Sink) (hashes : List U32)
    (countRoom : before.count.val + hashes.length ≤ Usize.max)
    (hashRoom : (model.values before.hashes).length + hashes.length ≤ capacity)
    (enumeration : each_relevant_element_hash_inst261 element
      (core.ops.function.FnMut_inst35_impl23 element) node (viewOfOld before) =
      callbackFold element (viewOfOld before) hashes) :
    bloom_hashes.DomHashes.Insts.Stylo_bloom_verificationBloom_storageHashProvider.insert
      element node (newOfOld before) ⦃ _ => True ⦄ := by
  rw [provider_original element node before hashes enumeration]
  obtain ⟨after, backs, calls⟩ := calls_exist model capacity allocation hashes before countRoom hashRoom
  rw [calls_fold calls]
  simp

#print axioms calls_fold
#print axioms fold_success
#print axioms provider_success
end ProviderCompletionProofs
