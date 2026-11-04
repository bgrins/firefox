/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import HashInsertProofs
open Aeneas Aeneas.Std Result Bloom
noncomputable section
namespace ProviderProofs

abbrev Old := bloom_storage.HashInsert
abbrev New := bloom_storage.HashInsert
abbrev View := bloom_storage.HashInsertBorrowed

def oldOfView (state : View) : Old :=
  { filter := state.filter, hashes := state.hashes, count := state.count }

def viewOfOld (state : Old) : View :=
  { filter := state.filter, hashes := state.hashes, count := state.count }

def newOfOld (state : Old) : New :=
  { filter := state.filter, hashes := state.hashes, count := state.count }

def oldOfNew (state : New) : Old :=
  { filter := state.filter, hashes := state.hashes, count := state.count }

theorem callback_original {E : Type} (element : dom.TElement E)
    (before : View) (hash : U32) :
    core.ops.function.FnMut_inst35_impl23.call_mut element before hash =
      (do
        let (after, _) ← storage_hash (oldOfView before) hash
        ok ((), viewOfOld after, id)) := by
  simp [core.ops.function.FnMut_inst35_impl23.call_mut,
    bloom_storage.HashInsertBorrowed.push_hash, bloom_storage.HashInsert.borrowed, bloom_storage.HashInsertBorrowed.push_hash,
    storage_hash, oldOfView, viewOfOld, Std.bind_assoc]
  rfl


def originalFold (before : Old) : List U32 → Result Old
  | [] => ok before
  | hash :: rest => do
    let (after, _) ← storage_hash before hash
    originalFold after rest

def callbackFold {E : Type} (element : dom.TElement E) (before : View) : List U32 → Result View
  | [] => ok before
  | hash :: rest => do
    let (_, after, back) ← core.ops.function.FnMut_inst35_impl23.call_mut element before hash
    callbackFold element (back after) rest

theorem callback_fold_original {E : Type} (element : dom.TElement E)
    (before : Old) (hashes : List U32) :
    callbackFold element (viewOfOld before) hashes =
      (do let after ← originalFold before hashes; ok (viewOfOld after)) := by
  induction hashes generalizing before with
  | nil => simp [callbackFold, originalFold]
  | cons hash rest ih =>
    simp only [callbackFold, callback_original, originalFold, Std.bind_assoc]
    simp only [oldOfView, viewOfOld]
    congr 1
    funext result
    rcases result with ⟨after, back⟩
    simpa [viewOfOld] using ih after

theorem provider_original {E : Type} (element : dom.TElement E) (node : E)
    (before : Old) (hashes : List U32)
    (enumeration : each_relevant_element_hash_inst261 element
      (core.ops.function.FnMut_inst35_impl23 element) node (viewOfOld before) =
      callbackFold element (viewOfOld before) hashes) :
    bloom_hashes.DomHashes.Insts.Stylo_bloom_verificationBloom_storageHashProvider.insert
      element node (newOfOld before) =
      (do let after ← originalFold before hashes
          ok (newOfOld after, fun future : New => { future with count := before.count })) := by
  simp only [bloom_hashes.DomHashes.Insts.Stylo_bloom_verificationBloom_storageHashProvider.insert,
    bloom_storage.HashInsert.borrowed, newOfOld, bind_ok]
  change (do
    let after ← each_relevant_element_hash_inst261 element
      (core.ops.function.FnMut_inst35_impl23 element) node (viewOfOld before)
    ok (newOfOld (oldOfView after), fun future : New => { future with count := before.count })) = _
  rw [enumeration, callback_fold_original]
  change Std.bind (Std.bind (originalFold before hashes) (fun after => ok (viewOfOld after)))
    (fun after => ok (newOfOld (oldOfView after), fun future : New => { future with count := before.count })) =
    Std.bind (originalFold before hashes)
      (fun after => ok (newOfOld after, fun future : New => { future with count := before.count }))
  rw [Std.bind_assoc]
  simp only [bind_ok, newOfOld, oldOfView, viewOfOld]

#print axioms callback_fold_original
#print axioms provider_original

#print axioms callback_original
end ProviderProofs
