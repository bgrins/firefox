/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Model
open Aeneas Aeneas.Std Result Baseline
noncomputable section
namespace WrapperEquivalence
abbrev Old := bloom_storage.HashInsert
abbrev New := candidate_storage.HashInsert

def forward (state : Old) : New :=
  { filter := state.filter, hashes := state.hashes, count := state.count }
def backward (state : New) : Old :=
  { filter := state.filter, hashes := state.hashes, count := state.count }

theorem exact_behavior (before : Old) (hash : U32) :
    candidate_hash (forward before) hash =
      (do
        let (after, back) ← bloom_storage.HashInsert.push_hash before hash
        ok (forward after, fun future => forward (back (backward future)))) := by
  simp [candidate_hash, candidate_storage.HashInsert.borrowed,
    candidate_storage.HashInsertBorrowed.push_hash, bloom_storage.HashInsert.push_hash,
    forward, backward, Std.bind_assoc]

#print axioms exact_behavior
end WrapperEquivalence
