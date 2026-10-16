/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import StoragePushProofs
import StoragePopProofs
import StorageClearProofs

open Aeneas Aeneas.Std Result Bloom BloomProofs StyleBloomProofs HashInsertProofs

namespace StorageInvariantProofs

structure SequenceModel (E : Type) where
  hashPush : HashVecModel
  elementPush : StoragePushProofs.ElementPushModel E
  hashLength : StoragePushProofs.HashLengthModel hashPush
  pop_hash : ∀ before rest hash, hashPush.values before = rest ++ [hash] →
    smallvec.SmallVec.pop (ArrayT64.Insts.SmallvecArray U32) before
      ⦃ result => result.1 = some hash ∧ hashPush.values result.2 = rest ⦄
  pop_expected : ∀ (before : alloc.vec.Vec U32) rest hash, before.val = rest ++ [hash] →
    alloc.vec.Vec.pop Global before ⦃ result => result.1 = some hash ∧ result.2.val = rest ⦄
  pop_some : ∀ before rest element, elementPush.values before = rest ++ [element] →
    smallvec.SmallVec.pop (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E)) before
      ⦃ result => result.1 = some element ∧ elementPush.values result.2 = rest ⦄
  pop_none : ∀ before, elementPush.values before = [] →
    smallvec.SmallVec.pop (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E)) before
      ⦃ result => result.1 = none ∧ elementPush.values result.2 = [] ⦄
  clear_hashes : ∀ before,
    smallvec.SmallVec.clear (ArrayT64.Insts.SmallvecArray U32) before
      ⦃ after => hashPush.values after = [] ⦄
  clear_elements : ∀ before,
    smallvec.SmallVec.clear (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E)) before
      ⦃ after => elementPush.values after = [] ⦄
  deref_hashes : ∀ before,
    smallvec.SmallVec.Insts.CoreOpsDerefDerefSlice.deref
      (ArrayT64.Insts.SmallvecArray U32) before
      ⦃ slice => slice.val = hashPush.values before ⦄

def SequenceModel.popModel {E : Type} (model : SequenceModel E) : StoragePopProofs.PopModel :=
  { hashes := model.hashPush.values, pop_hash := model.pop_hash, pop_expected := model.pop_expected }

def SequenceModel.elementPopModel {E : Type} (model : SequenceModel E) :
    StoragePopProofs.ElementPopModel E :=
  { elements := model.elementPush.values, pop_some := model.pop_some, pop_none := model.pop_none }

def SequenceModel.clearModel {E : Type} (model : SequenceModel E) : StorageClearProofs.ClearModel E :=
  { hashes := model.hashPush.values, elements := model.elementPush.values,
    clear_hashes := model.clear_hashes, clear_elements := model.clear_elements,
    deref_hashes := model.deref_hashes }

def Valid {E : Type} (model : SequenceModel E) (hashes : E → List U32)
    (storage : bloom_storage.Storage E) : Prop :=
  HighWaterHistory storage.filter (model.hashPush.values storage.pushed_hashes)
    storage.max_pushed_hashes.val ∧
  model.hashPush.values storage.pushed_hashes =
    (model.elementPush.values storage.elements).flatMap (fun pushed => hashes pushed.element) ∧
  ∀ pushed ∈ model.elementPush.values storage.elements,
    pushed.num_hashes.val = (hashes pushed.element).length

def chain {E : Type} (model : SequenceModel E) (storage : bloom_storage.Storage E) : List E :=
  ((model.elementPush.values storage.elements).map (fun pushed => pushed.element)).reverse

theorem onSuccess_mono {A : Type} {run : Result A} {before after : A → Prop}
    (h : OnSuccess run before) (imp : ∀ value, before value → after value) : OnSuccess run after := by
  intro value hrun
  exact imp value (h value hrun)

theorem push_valid {E P : Type} (elementOps : dom.TElement E)
    (provider : bloom_storage.HashProvider P E) (hashes : E → List U32)
    (model : SequenceModel E) (providerCalls : StoragePushProofs.ProviderCalls provider hashes)
    (before : bloom_storage.Storage E) (element : E) (valid : Valid model hashes before) :
    OnSuccess (bloom_storage.Storage.push elementOps provider before element) (fun result =>
      Valid model hashes result.1 ∧ chain model result.1 = element :: chain model before ∧
      result.2 = id) := by
  refine onSuccess_mono (StoragePushProofs.push_history elementOps provider hashes model.hashPush
    model.hashLength model.elementPush providerCalls before element valid.1) ?_
  rintro result ⟨hhistory, hhashes, ⟨pushed, helement, hcount, helements⟩, hback⟩
  refine ⟨⟨hhistory, ?_, ?_⟩, ?_, hback⟩
  · rw [hhashes, helements, valid.2.1]
    simp only [List.flatMap_append, List.flatMap_cons, List.flatMap_nil, List.append_nil, helement]
  · intro item hmem
    rw [helements] at hmem
    rcases List.mem_append.mp hmem with hold | hnew
    · exact valid.2.2 item hold
    · have heq : item = pushed := by simpa using hnew
      subst item
      simpa only [helement] using hcount
  · simp only [chain, helements, List.map_append, List.map_cons, List.map_nil,
      List.reverse_append, List.reverse_cons, List.reverse_nil, List.nil_append,
      List.singleton_append, helement]

theorem clear_valid {E : Type} (elementOps : dom.TElement E) (model : SequenceModel E)
    (hashes : E → List U32) (before : bloom_storage.Storage E) (valid : Valid model hashes before) :
    bloom_storage.Storage.clear elementOps before ⦃ result =>
      Valid model hashes result.1 ∧ chain model result.1 = [] ∧ result.2 = id ⦄ := by
  apply WP.spec_mono (StorageClearProofs.clear_exact elementOps model.clearModel before valid.1)
  rintro result ⟨hfilter, helements, hhashes, hhigh, hback⟩
  change model.elementPush.values result.1.elements = [] at helements
  change model.hashPush.values result.1.pushed_hashes = [] at hhashes
  refine ⟨⟨?_, ?_, ?_⟩, ?_, hback⟩
  · rw [hfilter, hhashes, hhigh]
    exact HighWaterHistory.empty
  · rw [hhashes, helements]
    rfl
  · simp only [helements, List.not_mem_nil, false_implies, implies_true]
  · simp only [chain, helements, List.map_nil, List.reverse_nil]

theorem pop_valid {E P : Type} (elementOps : dom.TElement E)
    (provider : bloom_storage.HashProvider P E) (model : SequenceModel E)
    (optionModel : StoragePopProofs.OptionModel E) (hashes : E → List U32)
    (expectedSpec : ∀ element, provider.expected element ⦃ expected => expected.val = hashes element ⦄)
    (before : bloom_storage.Storage E) (valid : Valid model hashes before) :
    bloom_storage.Storage.pop elementOps provider before ⦃ result =>
      Valid model hashes result.2.1 ∧ chain model result.2.1 = (chain model before).tail ∧
      result.1 = (chain model before).head? ∧
      result.2.1.max_pushed_hashes = before.max_pushed_hashes ∧ result.2.2 = id ⦄ := by
  by_cases hempty : model.elementPush.values before.elements = []
  · apply WP.spec_mono (StoragePopProofs.pop_none_history elementOps provider model.popModel
      model.elementPopModel optionModel before hempty valid.1)
    rintro result ⟨hpopped, hfilter, hhashes, hhistory, helements, hhigh, hback⟩
    change model.elementPush.values result.2.1.elements = [] at helements
    refine ⟨⟨hhistory, ?_, ?_⟩, ?_, ?_, hhigh, hback⟩
    · rw [hhashes, valid.2.1, hempty, helements]
    · simp only [helements, List.not_mem_nil, false_implies, implies_true]
    · simp only [chain, helements, hempty, List.map_nil, List.reverse_nil, List.tail_nil]
    · simp only [chain, hempty, List.map_nil, List.reverse_nil, List.head?_nil]
      exact hpopped
  · let rest := (model.elementPush.values before.elements).dropLast
    let pushed := (model.elementPush.values before.elements).getLast hempty
    have helements : model.elementPush.values before.elements = rest ++ [pushed] :=
      (List.dropLast_concat_getLast hempty).symm
    have hhashes : model.hashPush.values before.pushed_hashes =
        rest.flatMap (fun (p : bloom_storage.PushedElement E) => hashes p.element) ++ hashes pushed.element := by
      rw [valid.2.1, helements]
      simp only [List.flatMap_append, List.flatMap_cons, List.flatMap_nil, List.append_nil]
    have hcount : pushed.num_hashes.val = (hashes pushed.element).length :=
      valid.2.2 pushed (by rw [helements]; simp)
    apply WP.spec_mono (StoragePopProofs.pop_some_history elementOps provider model.popModel
      model.elementPopModel optionModel before rest pushed
      (rest.flatMap (fun (p : bloom_storage.PushedElement E) => hashes p.element)) (hashes pushed.element)
      helements hhashes hcount valid.1 (expectedSpec pushed.element))
    rintro result ⟨hpopped, hhistory, hhashes, helementsAfter, hhigh, hback⟩
    change model.elementPush.values result.2.1.elements = rest at helementsAfter
    change model.hashPush.values result.2.1.pushed_hashes =
      rest.flatMap (fun (p : bloom_storage.PushedElement E) => hashes p.element) at hhashes
    refine ⟨⟨hhistory, ?_, ?_⟩, ?_, ?_, hhigh, hback⟩
    · rw [helementsAfter]
      exact hhashes
    · intro item hmem
      rw [helementsAfter] at hmem
      apply valid.2.2
      rw [helements]
      exact List.mem_append_left _ hmem
    · simp only [chain, helementsAfter, helements, List.map_append, List.map_cons, List.map_nil,
        List.reverse_append, List.reverse_cons, List.reverse_nil, List.nil_append,
        List.singleton_append, List.tail_cons]
    · simpa only [chain, helements, List.map_append, List.map_cons, List.map_nil,
        List.reverse_append, List.reverse_cons, List.reverse_nil, List.nil_append,
        List.singleton_append, List.head?_cons] using hpopped

#print axioms push_valid
#print axioms clear_valid
#print axioms pop_valid

end StorageInvariantProofs
