/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import ProviderProofs
open Aeneas Aeneas.Std Result Bloom ProviderProofs
noncomputable section
namespace ProviderTraceProofs

abbrev Calls := HashInsertProofs.Calls

theorem bind_success {A B : Type} {run : Result A} {next : A → Result B} {value : B}
    (success : Std.bind run next = ok value) :
    ∃ middle, run = ok middle ∧ next middle = ok value := by
  cases run with
  | ret middle => exact ⟨middle, rfl, by simpa only [bind_ok] using success⟩
  | vis effect continuation =>
    have h := congrArg Result.match success
    simp only [bind_vis, Result.match.vis, Result.match.ok] at h
    cases h
  | div =>
    have h := congrArg Result.match success
    simp only [bind_div, Result.match.div, Result.match.ok] at h
    cases h

theorem original_fold_calls {before after : Old} {hashes : List U32}
    (success : originalFold before hashes = ok after) :
    ∃ backs, Calls before hashes after backs := by
  induction hashes generalizing before with
  | nil =>
    have h := congrArg Result.match success
    simp only [originalFold, Result.match.ok] at h
    cases h
    exact ⟨[], .nil _⟩
  | cons hash rest ih =>
    change Std.bind (storage_hash before hash)
      (fun result => originalFold result.1 rest) = ok after at success
    obtain ⟨⟨middle, back⟩, call, continuation⟩ := bind_success success
    obtain ⟨backs, calls⟩ := ih continuation
    exact ⟨back :: backs, .cons call calls⟩


theorem provider_calls {E : Type} (element : dom.TElement E) (node : E)
    (before : Old) (hashes : List U32) (after : New) (back : New → New)
    (enumeration : each_relevant_element_hash_inst261 element
      (core.ops.function.FnMut_inst35_impl23 element) node (viewOfOld before) =
      callbackFold element (viewOfOld before) hashes)
    (success : bloom_hashes.DomHashes.Insts.Stylo_bloom_verificationBloom_storageHashProvider.insert
      element node (newOfOld before) = ok (after, back)) :
    ∃ backs, Calls before hashes (oldOfNew after) backs ∧
      back = fun future => { future with count := before.count } := by
  rw [provider_original element node before hashes enumeration] at success
  change Std.bind (originalFold before hashes)
    (fun final => ok (newOfOld final, fun future : New => { future with count := before.count })) =
      ok (after, back) at success
  obtain ⟨final, folded, result⟩ := bind_success success
  have h := congrArg Result.match result
  simp only [Result.match.ok] at h
  have pair : (newOfOld final, fun future : New => { future with count := before.count }) =
      (after, back) := by cases h; rfl
  have forward := congrArg Prod.fst pair
  change newOfOld final = after at forward
  have backward := congrArg Prod.snd pair
  obtain ⟨backs, calls⟩ := original_fold_calls folded
  refine ⟨backs, ?_, backward.symm⟩
  rw [← forward]
  exact calls

def expectedFold {E : Type} (element : dom.TElement E) (before : alloc.vec.Vec U32) :
    List U32 → Result (alloc.vec.Vec U32)
  | [] => ok before
  | hash :: rest => do
    let (_, after, back) ← core.ops.function.FnMut_inst37_impl25.call_mut element before hash
    expectedFold element (back after) rest

def vecFold (before : alloc.vec.Vec U32) : List U32 → Result (alloc.vec.Vec U32)
  | [] => ok before
  | hash :: rest => do
    let after ← alloc.vec.Vec.push before hash
    vecFold after rest

theorem expected_callback {E : Type} (element : dom.TElement E)
    (before : alloc.vec.Vec U32) (hash : U32) :
    core.ops.function.FnMut_inst37_impl25.call_mut element before hash =
      (do let after ← alloc.vec.Vec.push before hash; ok ((), after, id)) := by
  rfl

theorem expected_fold {E : Type} (element : dom.TElement E)
    (before : alloc.vec.Vec U32) (hashes : List U32) :
    expectedFold element before hashes = vecFold before hashes := by
  induction hashes generalizing before with
  | nil => rfl
  | cons hash rest ih =>
    simp only [expectedFold, expected_callback, vecFold, Std.bind_assoc, bind_ok]
    congr 1
    funext after
    simpa using ih after

theorem vec_fold_values (before : alloc.vec.Vec U32) (hashes : List U32)
    (capacity : before.val.length + hashes.length ≤ Usize.max) :
    vecFold before hashes ⦃ after => after.val = before.val ++ hashes ⦄ := by
  induction hashes generalizing before with
  | nil => simp [vecFold]
  | cons hash rest ih =>
    have room : before.val.length < Usize.max := by
      simp only [List.length_cons] at capacity
      omega
    simp only [vecFold]
    apply WP.spec_bind (alloc.vec.Vec.push_spec before hash room)
    intro middle values
    have remaining : middle.val.length + rest.length ≤ Usize.max := by
      rw [values, List.length_append, List.length_singleton]
      simp only [List.length_cons] at capacity
      omega
    apply WP.spec_mono (ih middle remaining)
    intro after final
    simpa only [values, List.append_assoc, List.singleton_append] using final

theorem provider_expected {E : Type} (element : dom.TElement E) (node : E)
    (hashes : List U32) (capacity : hashes.length ≤ Usize.max)
    (enumeration : each_relevant_element_hash_inst262 element
      (core.ops.function.FnMut_inst37_impl25 element) node (alloc.vec.Vec.new U32) =
      expectedFold element (alloc.vec.Vec.new U32) hashes) :
    bloom_hashes.DomHashes.Insts.Stylo_bloom_verificationBloom_storageHashProvider.expected
      element node ⦃ after => after.val = hashes ⦄ := by
  simp only [bloom_hashes.DomHashes.Insts.Stylo_bloom_verificationBloom_storageHashProvider.expected,
    enumeration, expected_fold]
  simpa using vec_fold_values (alloc.vec.Vec.new U32) hashes (by simpa using capacity)

#print axioms original_fold_calls
#print axioms provider_calls
#print axioms expected_callback
#print axioms expected_fold
#print axioms vec_fold_values
#print axioms provider_expected
end ProviderTraceProofs
