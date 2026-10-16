/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import StyleBloomProofs
import ZeroedProofs

open Aeneas Aeneas.Std Result Bloom BloomProofs StyleBloomProofs

namespace StorageClearProofs

abbrev HashVec := smallvec.SmallVec (Array U32 64#usize) U32
abbrev ElementVec (E : Type) :=
  smallvec.SmallVec (Array (bloom_storage.PushedElement E) 16#usize)
    (bloom_storage.PushedElement E)

structure ClearModel (E : Type) where
  hashes : HashVec → List U32
  elements : ElementVec E → List (bloom_storage.PushedElement E)
  clear_hashes : ∀ before,
    smallvec.SmallVec.clear (ArrayT64.Insts.SmallvecArray U32) before
      ⦃ after => hashes after = [] ⦄
  clear_elements : ∀ before,
    smallvec.SmallVec.clear (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E)) before
      ⦃ after => elements after = [] ⦄
  deref_hashes : ∀ before,
    smallvec.SmallVec.Insts.CoreOpsDerefDerefSlice.deref
      (ArrayT64.Insts.SmallvecArray U32) before
      ⦃ slice => slice.val = hashes before ⦄

theorem empty_zeroed : Bloom.zeroed empty ⦃ found => found = true ⦄ := by
  apply ZeroedProofs.zeroed_true
  intro index hindex
  change (Array.repeat 4096#usize 0#u8).val[index]! = 0#u8
  rw [Array.repeat_val]
  rw [getElem!_pos _ _ (by simp only [List.length_replicate]; scalar_tac)]
  simp only [List.getElem_replicate]

theorem clear_exact {E : Type} (elementOps : dom.TElement E)
    (model : ClearModel E) (before : bloom_storage.Storage E)
    (history : HighWaterHistory before.filter (model.hashes before.pushed_hashes)
      before.max_pushed_hashes.val) :
    bloom_storage.Storage.clear elementOps before ⦃ result =>
      result.1.filter = empty ∧
      model.elements result.1.elements = [] ∧
      model.hashes result.1.pushed_hashes = [] ∧
      result.1.max_pushed_hashes = 0#usize ∧ result.2 = id ⦄ := by
  unfold bloom_storage.Storage.clear
  step with model.clear_elements before.elements as ⟨elements, helements⟩
  step with model.deref_hashes before.pushed_hashes as ⟨slice, hslice⟩
  have hhistory : HighWaterHistory before.filter slice.val before.max_pushed_hashes.val := by
    simpa only [hslice] using history
  step with clear_filter_eq_empty before.filter slice before.max_pushed_hashes hhistory as ⟨filter, hfilter⟩
  subst filter
  step with model.clear_hashes before.pushed_hashes as ⟨hashes, hhashes⟩
  have hz := empty_zeroed
  unfold Bloom.zeroed at hz
  step with hz as ⟨found, hfound⟩
  subst found
  step
  exact ⟨helements, hhashes, rfl⟩

theorem clear_history {E : Type} (elementOps : dom.TElement E)
    (model : ClearModel E) (before : bloom_storage.Storage E)
    (history : HighWaterHistory before.filter (model.hashes before.pushed_hashes)
      before.max_pushed_hashes.val) :
    bloom_storage.Storage.clear elementOps before ⦃ result =>
      HighWaterHistory result.1.filter (model.hashes result.1.pushed_hashes)
        result.1.max_pushed_hashes.val ∧
      model.elements result.1.elements = [] ∧ result.2 = id ⦄ := by
  apply WP.spec_mono (clear_exact elementOps model before history)
  rintro result ⟨hfilter, helements, hhashes, hhigh, hback⟩
  refine ⟨?_, helements, hback⟩
  rw [hfilter, hhashes, hhigh]
  exact HighWaterHistory.empty

#print axioms empty_zeroed
#print axioms clear_exact
#print axioms clear_history

end StorageClearProofs
