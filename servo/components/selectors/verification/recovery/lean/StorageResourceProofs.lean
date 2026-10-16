/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import HashInsertProofs

open Aeneas Aeneas.Std Result Bloom BloomProofs CoverageProofs HashInsertProofs

namespace StorageResourceProofs

theorem flatMap_length_bound {E H : Type} (elements : List E) (hashes : E → List H)
    (limit : Nat) (bounded : ∀ element ∈ elements, (hashes element).length ≤ limit) :
    (elements.flatMap hashes).length ≤ elements.length * limit := by
  induction elements with
  | nil => simp
  | cons element rest ih =>
    have head := bounded element (by simp)
    have tail := ih (fun value member => bounded value (by simp [member]))
    simp only [List.flatMap_cons, List.length_append, List.length_cons, Nat.add_mul]
    omega

theorem push_capacity {E H : Type} (elements : List E) (element : E)
    (hashes : E → List H) (limit capacity maximum : Nat)
    (bounded : ∀ value ∈ elements ++ [element], (hashes value).length ≤ limit)
    (room : elements.length < capacity) (fits : capacity * limit ≤ maximum) :
    (elements.flatMap hashes).length + (hashes element).length ≤ maximum := by
  have bound := flatMap_length_bound (elements ++ [element]) hashes limit bounded
  have count : elements.length + 1 ≤ capacity := by omega
  have total := Nat.mul_le_mul_right limit count
  simp only [List.flatMap_append, List.flatMap_cons, List.flatMap_nil, List.append_nil,
    List.length_append, List.length_singleton] at bound
  omega

structure AllocationModel (model : HashVecModel) (capacity : Nat) where
  push_success : ∀ before hash, (model.values before).length < capacity →
    smallvec.SmallVec.push (ArrayT64.Insts.SmallvecArray U32) before hash ⦃ _ => True ⦄

theorem push_hash_success (sink : Sink) (hash : U32)
    (room : sink.count.val < Usize.max)
    (allocation : smallvec.SmallVec.push (ArrayT64.Insts.SmallvecArray U32)
      sink.hashes hash ⦃ _ => True ⦄) :
    storage_hash sink hash ⦃ _ => True ⦄ := by
  simp only [storage_hash, bloom_storage.HashInsert.borrowed, bloom_storage.HashInsertBorrowed.push_hash, Std.bind_assoc, bind_ok]
  step as ⟨count, hcount⟩
  have filter := insert_establishes_present sink.filter hash
  unfold Bloom.insert at filter
  step with filter as ⟨filter, _⟩
  step with allocation

theorem exists_of_success {A : Type} {run : Result A} (success : run ⦃ _ => True ⦄) :
    ∃ result, run = ok result := by
  cases run with
  | ret value => exact ⟨value, rfl⟩
  | vis effect continuation => simp at success
  | div => simp at success

theorem calls_exist (model : HashVecModel) (capacity : Nat)
    (allocation : AllocationModel model capacity) (hashes : List U32) (before : Sink)
    (countRoom : before.count.val + hashes.length ≤ Usize.max)
    (hashRoom : (model.values before.hashes).length + hashes.length ≤ capacity) :
    ∃ after backs, Calls before hashes after backs := by
  induction hashes generalizing before with
  | nil => exact ⟨before, [], .nil before⟩
  | cons hash rest ih =>
    have countRoom' : before.count.val < Usize.max := by
      simp only [List.length_cons] at countRoom
      omega
    have hashRoom' : (model.values before.hashes).length < capacity := by
      simp only [List.length_cons] at hashRoom
      omega
    obtain ⟨⟨middle, back⟩, run⟩ := exists_of_success
      (push_hash_success before hash countRoom' (allocation.push_success _ _ hashRoom'))
    have single : Calls before [hash] middle [back] := .cons run (.nil middle)
    have accounting := calls_accounting model single
    have countNext : middle.count.val + rest.length ≤ Usize.max := by
      simp only [List.length_cons, List.length_nil] at accounting countRoom
      omega
    have hashNext : (model.values middle.hashes).length + rest.length ≤ capacity := by
      rw [accounting.2.1, List.length_append, List.length_singleton]
      simp only [List.length_cons] at hashRoom
      omega
    obtain ⟨after, backs, calls⟩ := ih middle countNext hashNext
    exact ⟨after, back :: backs, .cons run calls⟩

#print axioms flatMap_length_bound
#print axioms push_capacity
#print axioms push_hash_success
#print axioms calls_exist

end StorageResourceProofs
