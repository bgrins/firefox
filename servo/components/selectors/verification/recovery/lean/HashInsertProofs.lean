/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import StorageHistoryProofs
import NormalizationProofs

open Aeneas Aeneas.Std Result Bloom BloomProofs CoverageProofs StorageHistoryProofs

namespace HashInsertProofs

abbrev HashVec := smallvec.SmallVec (Array U32 64#usize) U32
abbrev Sink := bloom_storage.HashInsert

def OnSuccess {A : Type} (run : Result A) (post : A → Prop) : Prop :=
  ∀ result, run = ok result → post result

theorem onSuccess_ok {A : Type} {value : A} {post : A → Prop} (h : post value) :
    OnSuccess (ok value) post := by
  intro result heq
  have he := congrArg Result.match heq
  simp only [Result.match.ok] at he
  cases he
  exact h

theorem onSuccess_bind_with {A B : Type} (run : Result A) (next : A → Result B)
    (pre : A → Prop) (post : B → Prop) (hr : OnSuccess run pre)
    (h : ∀ value, pre value → OnSuccess (next value) post) :
    OnSuccess (Aeneas.Std.bind run next) post := by
  cases run with
  | ret value => simpa only [bind_ok] using h value (hr value rfl)
  | vis effect continuation =>
    intro result heq
    have he := congrArg Result.match heq
    simp only [bind_vis, Result.match.vis, Result.match.ok] at he
    cases he
  | div =>
    intro result heq
    have he := congrArg Result.match heq
    simp only [bind_div, Result.match.div, Result.match.ok] at he
    cases he

theorem push_hash_exact (s : Sink) (hash : U32) (count : Usize)
    (filter : Filter) (hashes : HashVec)
    (hc : s.count + 1#usize = ok count)
    (hf : Bloom.insert s.filter hash = ok filter)
    (hh : smallvec.SmallVec.push (ArrayT64.Insts.SmallvecArray U32) s.hashes hash = ok hashes) :
    storage_hash s hash =
      ok ({ filter, hashes, count }, fun future => { future with count := s.count }) := by
  simp only [Bloom.insert] at hf
  simp [storage_hash, bloom_storage.HashInsert.borrowed, bloom_storage.HashInsertBorrowed.push_hash, hc, hf, hh]

theorem push_hash_inv (s : Sink) (hash : U32) :
    OnSuccess (storage_hash s hash) (fun result =>
      s.count + 1#usize = ok result.1.count ∧
      Bloom.insert s.filter hash = ok result.1.filter ∧
      smallvec.SmallVec.push (ArrayT64.Insts.SmallvecArray U32) s.hashes hash =
        ok result.1.hashes ∧
      result.2 = fun future => { future with count := s.count }) := by
  simp only [storage_hash, bloom_storage.HashInsert.borrowed, bloom_storage.HashInsertBorrowed.push_hash, Std.bind_assoc, bind_ok]
  refine onSuccess_bind_with _ _ (fun count => s.count + 1#usize = ok count) _
    (by intro _ h; exact h) ?_
  intro count hc
  refine onSuccess_bind_with _ _ (fun filter => Bloom.insert s.filter hash = ok filter) _
    (by intro _ h; exact h) ?_
  intro filter hf
  refine onSuccess_bind_with _ _
    (fun hashes => smallvec.SmallVec.push (ArrayT64.Insts.SmallvecArray U32) s.hashes hash = ok hashes) _
    (by intro _ h; exact h) ?_
  intro hashes hh
  exact onSuccess_ok ⟨hc, hf, hh, rfl⟩


structure HashVecModel where
  values : HashVec → List U32
  push_correct : ∀ before hash after,
    smallvec.SmallVec.push (ArrayT64.Insts.SmallvecArray U32) before hash = ok after →
    values after = values before ++ [hash]

inductive Calls : Sink → List U32 → Sink → List (Sink → Sink) → Prop where
  | nil (sink : Sink) : Calls sink [] sink []
  | cons {before middle final hash rest back backs} :
      storage_hash before hash = ok (middle, back) →
      Calls middle rest final backs →
      Calls before (hash :: rest) final (back :: backs)

def closeBacks (backs : List (Sink → Sink)) (future : Sink) : Sink :=
  backs.foldr (fun back result => back result) future

def closeProvider (initial : Sink) (backs : List (Sink → Sink)) (future : Sink) : Sink :=
  { closeBacks backs future with count := initial.count }

theorem calls_accounting (model : HashVecModel) {before after : Sink}
    {hashes : List U32} {backs : List (Sink → Sink)}
    (calls : Calls before hashes after backs) :
    Insertions before.filter hashes after.filter ∧
    model.values after.hashes = model.values before.hashes ++ hashes ∧
    after.count.val = before.count.val + hashes.length := by
  induction calls with
  | nil sink => exact ⟨.nil _, by simp, by simp⟩
  | @cons before middle final hash rest back backs hrun _ ih =>
    have info := push_hash_inv before hash (middle, back) hrun
    have hv := model.push_correct before.hashes hash middle.hashes info.2.2.1
    have hc := UScalar.add_equiv before.count 1#usize
    rw [info.1] at hc
    simp only [Result.match.ok] at hc
    refine ⟨.cons info.2.1 ih.1, ?_, ?_⟩
    · rw [ih.2.1, hv]
      simp only [List.append_assoc, List.singleton_append]
    · have hcount : middle.count.val = before.count.val + 1 := by simpa using hc.2.1
      simp only [List.length_cons]
      omega

theorem calls_borrowed_fields {before after : Sink} {hashes : List U32}
    {backs : List (Sink → Sink)} (calls : Calls before hashes after backs) (future : Sink) :
    (closeBacks backs future).filter = future.filter ∧
    (closeBacks backs future).hashes = future.hashes := by
  induction calls with
  | nil sink => exact ⟨rfl, rfl⟩
  | @cons before middle final hash rest back backs hrun _ ih =>
    have info := push_hash_inv before hash (middle, back) hrun
    have hb : back = fun future => { future with count := before.count } := info.2.2.2
    simp only [closeBacks, List.foldr_cons, hb]
    exact ih

theorem calls_close {before after : Sink} {hashes : List U32}
    {backs : List (Sink → Sink)} (calls : Calls before hashes after backs) (future : Sink) :
    closeProvider before backs future = { future with count := before.count } := by
  have fields := calls_borrowed_fields calls future
  cases h : closeBacks backs future with
  | mk filter hashes count =>
    simp only [h] at fields
    simp only [closeProvider, h, fields.1, fields.2]

theorem calls_history (model : HashVecModel) {before after : Sink}
    {hashes : List U32} {backs : List (Sink → Sink)} {high : Nat}
    (history : StyleBloomProofs.HighWaterHistory before.filter (model.values before.hashes) high)
    (calls : Calls before hashes after backs) :
    StyleBloomProofs.HighWaterHistory after.filter (model.values after.hashes)
      (max high ((model.values before.hashes).length + hashes.length)) := by
  have info := calls_accounting model calls
  rw [info.2.1]
  exact insertion_history history info.1

#print axioms push_hash_exact
#print axioms push_hash_inv
#print axioms calls_accounting
#print axioms calls_borrowed_fields
#print axioms calls_close
#print axioms calls_history

end HashInsertProofs
