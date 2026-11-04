/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import BloomProofs
import Mathlib.Tactic.IntervalCases

open Aeneas Aeneas.Std Result
open Bloom BloomProofs

namespace PackingProofs

abbrev Hashes := ancestor_hashes.AncestorHashes

def fourthValue (a b c : BitVec 32) : BitVec 32 :=
  ((a &&& 0xff000000#32) >>> 24) |||
  ((b &&& 0xff000000#32) >>> 16) |||
  ((c &&& 0xff000000#32) >>> 8)

@[step]
theorem fourth_hash_spec (h : Hashes) :
    ancestor_hashes.AncestorHashes.fourth_hash h ⦃ v =>
      v.bv = fourthValue h.packed_hashes.val[0]!.bv
        h.packed_hashes.val[1]!.bv h.packed_hashes.val[2]!.bv ⦄ := by
  unfold ancestor_hashes.AncestorHashes.fourth_hash
  step*
  simp_all [fourthValue, getElem!_pos]

def packedWords (a b c d : U32) : List U32 :=
  [⟨a.bv ||| ((d.bv &&& 0xff#32) <<< 24)⟩,
   ⟨b.bv ||| ((d.bv &&& 0xff00#32) <<< 16)⟩,
   ⟨c.bv ||| ((d.bv &&& 0xff0000#32) <<< 8)⟩]

@[step]
theorem pack_spec (a b c d : U32) (len : Usize) :
    Bloom.pack (Array.make 4#usize [a, b, c, d]) len ⦃ p =>
      p.packed_hashes.val = if len = 4#usize then packedWords a b c d else [a, b, c] ⦄ := by
  unfold Bloom.pack ancestor_hashes.AncestorHashes.from_hashes
  by_cases hlen : len = 4#usize
  all_goals simp only [hlen, ↓reduceIte]
  all_goals step*
  all_goals simp_all [packedWords, UScalar.eq_equiv_bv_eq]

def masked (a : U32) : U32 := ⟨a.bv &&& 0xffffff#32⟩

theorem pack_roundtrip (a b c d : U32) (len : Usize) :
    (do
      let p ← Bloom.pack (Array.make 4#usize [masked a, masked b, masked c, masked d]) len
      let fourth ← ancestor_hashes.AncestorHashes.fourth_hash p
      ok (p, fourth)) ⦃ result =>
        result.1.packed_hashes.val.map masked = [masked a, masked b, masked c] ∧
        result.2 = if len = 4#usize then masked d else 0#u32 ⦄ := by
  step as ⟨p, hp⟩
  step as ⟨fourth, hf⟩
  rw [hp] at hf ⊢
  by_cases hlen : len = 4#usize
  · simp only [hlen, ↓reduceIte, packedWords, List.map_cons, List.map_nil] at hf ⊢
    constructor
    · simp only [List.cons.injEq, and_true, UScalar.eq_equiv_bv_eq]
      constructor
      · dsimp [masked]
        ext i hi
        interval_cases i <;> simp
      constructor <;> dsimp [masked]
      all_goals
        ext i hi
        interval_cases i <;> simp
    · rw [UScalar.eq_equiv_bv_eq]
      apply Eq.trans hf
      simp only [fourthValue, List.getElem!_cons_zero, List.getElem!_cons_succ, masked]
      ext i hi
      interval_cases i <;> simp
  · simp only [hlen, ↓reduceIte] at hf ⊢
    constructor
    · simp [masked, BitVec.and_assoc]
    · rw [UScalar.eq_equiv_bv_eq]
      apply Eq.trans hf
      simp only [fourthValue, List.getElem!_cons_zero, List.getElem!_cons_succ, masked]
      ext i hi
      interval_cases i <;> simp

theorem may_match_of_present (packed : Array U32 3#usize) (filter : Filter)
    (hwords : ∀ word ∈ packed.val, word ≠ 0#u32 →
      Bloom.contains filter (word &&& 0xffffff#u32) ⦃ b => b = true ⦄)
    (hfourth : ∀ word : U32,
      word.bv = fourthValue packed.val[0]!.bv packed.val[1]!.bv packed.val[2]!.bv →
      word ≠ 0#u32 → Bloom.contains filter word ⦃ b => b = true ⦄) :
    Bloom.may_match packed filter ⦃ b => b = true ⦄ := by
  unfold Bloom.may_match ancestor_hashes.AncestorHashes.may_match
  step as ⟨iter, hslice, hi⟩
  unfold ancestor_hashes.AncestorHashes.may_match_loop
  apply loop.spec_decr_nat (fun it => it.slice.val.length - it.i)
    (fun it => it.slice.val = packed.val) (fun b => b = true)
  · intro it hit
    unfold ancestor_hashes.AncestorHashes.may_match_loop.body
    unfold core.slice.iter.IteratorSliceIter.next
    split
    · simp only [bind_ok]
      dsimp! only
      split
      · simp
      · rename_i hnz
        have hmem : it.slice[it.i] ∈ packed.val := by
          rw [← hit]
          exact List.getElem_mem _
        have hp := hwords it.slice[it.i] hmem hnz
        unfold Bloom.contains at hp
        simp only [bloom.BLOOM_HASH_MASK]
        step
        have he : i = it.slice[it.i] &&& 0xffffff#u32 := by scalar_tac
        subst i
        step with hp
        have hbound : it.i < it.slice.val.length := ‹it.i < it.slice.len.val›
        rw [hit] at hbound
        simp_all
        omega
    · simp only [bind_ok]
      dsimp! only
      step as ⟨fourth, hf⟩
      split
      · simp
      · rename_i hnz
        have hp := hfourth fourth hf hnz
        unfold Bloom.contains at hp
        step with hp
        assumption
  · exact hslice

theorem history_no_false_rejection (packed : Array U32 3#usize)
    {filter : Filter} {live : List U32} (history : ValidHistory filter live)
    (hwords : ∀ word ∈ packed.val, word ≠ 0#u32 → word &&& 0xffffff#u32 ∈ live)
    (hfourth : ∀ word : U32,
      word.bv = fourthValue packed.val[0]!.bv packed.val[1]!.bv packed.val[2]!.bv →
      word ≠ 0#u32 → word ∈ live) :
    Bloom.may_match packed filter ⦃ b => b = true ⦄ := by
  apply may_match_of_present
  · intro word hmem hnz
    exact history_no_false_negatives history _ (hwords word hmem hnz)
  · intro word heq hnz
    exact history_no_false_negatives history _ (hfourth word heq hnz)

end PackingProofs
#print axioms PackingProofs.may_match_of_present
#print axioms PackingProofs.history_no_false_rejection
#print axioms PackingProofs.fourth_hash_spec
#print axioms PackingProofs.pack_spec
#print axioms PackingProofs.pack_roundtrip
