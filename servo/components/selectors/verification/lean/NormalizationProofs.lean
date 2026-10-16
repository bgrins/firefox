/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import PackingProofs

open Aeneas Aeneas.Std Result
open Bloom BloomProofs PackingProofs

namespace NormalizationProofs

theorem eq_ok_of_spec {α : Type} (m : Result α) (x : α)
    (h : m ⦃ v => v = x ⦄) : m = ok x := by
  cases m with
  | ret v => simpa using h
  | vis e k => simp at h
  | div => simp at h

theorem hash1_eq (h : U32) : bloom.hash1 h = ok ⟨h.bv &&& 4095#32⟩ := by
  apply eq_ok_of_spec
  unfold bloom.hash1
  step*
  simp_all [UScalar.eq_equiv_bv_eq]

theorem hash2_eq (h : U32) : bloom.hash2 h = ok ⟨(h.bv >>> 12) &&& 4095#32⟩ := by
  apply eq_ok_of_spec
  unfold bloom.hash2
  simp only [bloom.KEY_SIZE]
  step*
  simp_all [UScalar.eq_equiv_bv_eq]

theorem hash1_masked (h : U32) : bloom.hash1 (masked h) = bloom.hash1 h := by
  rw [hash1_eq, hash1_eq]
  congr 1
  rw [UScalar.eq_equiv_bv_eq]
  dsimp [masked]
  ext i hi
  interval_cases i <;> simp

theorem hash2_masked (h : U32) : bloom.hash2 (masked h) = bloom.hash2 h := by
  rw [hash2_eq, hash2_eq]
  congr 1
  rw [UScalar.eq_equiv_bv_eq]
  dsimp [masked]
  ext i hi
  interval_cases i <;> simp

theorem insert_masked (filter : Filter) (hash : U32) :
    Bloom.insert filter (masked hash) = Bloom.insert filter hash := by
  simp only [Bloom.insert, bloom.CountingBloomFilter.insert_hash,
    bloom.BloomStorage.first_slot_index.default, bloom.BloomStorage.second_slot_index.default,
    hash1_masked, hash2_masked]

theorem remove_masked (filter : Filter) (hash : U32) :
    Bloom.remove filter (masked hash) = Bloom.remove filter hash := by
  simp only [Bloom.remove, bloom.CountingBloomFilter.remove_hash,
    bloom.BloomStorage.first_slot_index.default, bloom.BloomStorage.second_slot_index.default,
    hash1_masked, hash2_masked]

theorem contains_masked (filter : Filter) (hash : U32) :
    Bloom.contains filter (masked hash) = Bloom.contains filter hash := by
  simp only [Bloom.contains, bloom.CountingBloomFilter.might_contain_hash,
    bloom.BloomStorage.first_slot_index.default, bloom.BloomStorage.second_slot_index.default,
    hash1_masked, hash2_masked]

theorem history_masked {filter : Filter} {live : List U32}
    (history : ValidHistory filter live) : ValidHistory filter (live.map masked) := by
  induction history with
  | empty => exact ValidHistory.empty
  | insert _ hrun ih =>
    exact ValidHistory.insert ih (by rwa [insert_masked])
  | @remove filter next before after hash history hrun ih =>
    have hi : ValidHistory filter (before.map masked ++ masked hash :: after.map masked) := by
      simpa only [List.map_append, List.map_cons] using ih
    simpa only [List.map_append] using
      (ValidHistory.remove hi (by rwa [remove_masked] : Bloom.remove filter (masked hash) = ok next))
  | clear _ hrun ih => exact ValidHistory.clear ih hrun

theorem raw_history_no_false_rejection (packed : Array U32 3#usize)
    {filter : Filter} {live : List U32} (history : ValidHistory filter live)
    (hwords : ∀ word ∈ packed.val, word ≠ 0#u32 → word &&& 0xffffff#u32 ∈ live.map masked)
    (hfourth : ∀ word : U32,
      word.bv = fourthValue packed.val[0]!.bv packed.val[1]!.bv packed.val[2]!.bv →
      word ≠ 0#u32 → word ∈ live.map masked) :
    Bloom.may_match packed filter ⦃ b => b = true ⦄ :=
  history_no_false_rejection packed (history_masked history) hwords hfourth

theorem pack_match_four_raw_hashes (a b c d : U32)
    {filter : Filter} {live : List U32} (history : ValidHistory filter live)
    (hsource : ∀ hash ∈ [a, b, c, d], hash ∈ live) :
    (do
      let p ← Bloom.pack (Array.make 4#usize [masked a, masked b, masked c, masked d]) 4#usize
      Bloom.may_match p.packed_hashes filter) ⦃ found => found = true ⦄ := by
  step as ⟨p, hp⟩
  simp only [↓reduceIte] at hp
  apply raw_history_no_false_rejection p.packed_hashes history
  · intro word hmem hnz
    rw [hp] at hmem
    simp only [packedWords, List.mem_cons, List.not_mem_nil, or_false] at hmem
    rcases hmem with rfl | rfl | rfl
    · apply List.mem_map.mpr
      refine ⟨a, hsource a (by simp), ?_⟩
      rw [UScalar.eq_equiv_bv_eq]
      dsimp [masked]
      ext i hi
      interval_cases i <;> simp
    · apply List.mem_map.mpr
      refine ⟨b, hsource b (by simp), ?_⟩
      rw [UScalar.eq_equiv_bv_eq]
      dsimp [masked]
      ext i hi
      interval_cases i <;> simp
    · apply List.mem_map.mpr
      refine ⟨c, hsource c (by simp), ?_⟩
      rw [UScalar.eq_equiv_bv_eq]
      dsimp [masked]
      ext i hi
      interval_cases i <;> simp
  · intro word hf hnz
    have he : word = masked d := by
      rw [UScalar.eq_equiv_bv_eq]
      apply Eq.trans hf
      rw [hp]
      simp only [packedWords, fourthValue, List.getElem!_cons_zero, List.getElem!_cons_succ, masked]
      ext i hi
      interval_cases i <;> simp
    rw [he]
    exact List.mem_map.mpr ⟨d, hsource d (by simp), rfl⟩

theorem pack_match_short_raw_hashes (a b c d : U32) (len : Usize) (hlen : len ≠ 4#usize)
    {filter : Filter} {live : List U32} (history : ValidHistory filter live)
    (hsource : ∀ hash ∈ [a, b, c], hash ≠ 0#u32 → hash ∈ live) :
    (do
      let p ← Bloom.pack (Array.make 4#usize [masked a, masked b, masked c, masked d]) len
      Bloom.may_match p.packed_hashes filter) ⦃ found => found = true ⦄ := by
  step as ⟨p, hp⟩
  simp only [hlen, ↓reduceIte] at hp
  apply raw_history_no_false_rejection p.packed_hashes history
  · intro word hmem hnz
    rw [hp] at hmem
    have hmem' : word ∈ [a, b, c].map masked := by simpa using hmem
    obtain ⟨raw, hraw, he⟩ := List.mem_map.mp hmem'
    subst word
    apply List.mem_map.mpr
    refine ⟨raw, hsource raw hraw ?_, ?_⟩
    · intro hz
      apply hnz
      rw [hz]
      rfl
    · rw [UScalar.eq_equiv_bv_eq]
      dsimp [masked]
      simp [BitVec.and_assoc]
  · intro word hf hnz
    have hz : word = 0#u32 := by
      rw [UScalar.eq_equiv_bv_eq]
      apply Eq.trans hf
      rw [hp]
      simp only [fourthValue, List.getElem!_cons_zero, List.getElem!_cons_succ, masked]
      ext i hi
      interval_cases i <;> simp
    exact False.elim (hnz hz)

theorem pack_match_raw_history (a b c d : U32) (len : Usize)
    {filter : Filter} {live : List U32} (history : ValidHistory filter live)
    (hsource : ∀ hash ∈ [a, b, c, d].take len.val, hash ∈ live)
    (hpadding : ∀ hash ∈ [a, b, c, d].drop len.val, hash = 0#u32) :
    (do
      let p ← Bloom.pack (Array.make 4#usize [masked a, masked b, masked c, masked d]) len
      Bloom.may_match p.packed_hashes filter) ⦃ found => found = true ⦄ := by
  by_cases hlen : len = 4#usize
  · subst len
    apply pack_match_four_raw_hashes a b c d history
    simpa using hsource
  · apply pack_match_short_raw_hashes a b c d len hlen history
    intro hash hmem hnz
    have hfull : hash ∈ [a, b, c, d] := by
      simp only [List.mem_cons, List.not_mem_nil, or_false] at hmem ⊢
      tauto
    rw [← List.take_append_drop len.val [a, b, c, d], List.mem_append] at hfull
    rcases hfull with hprefix | hsuffix
    · exact hsource hash hprefix
    · exact False.elim (hnz (hpadding hash hsuffix))

end NormalizationProofs

#print axioms NormalizationProofs.eq_ok_of_spec
#print axioms NormalizationProofs.hash1_eq
#print axioms NormalizationProofs.hash2_eq
#print axioms NormalizationProofs.hash1_masked
#print axioms NormalizationProofs.hash2_masked
#print axioms NormalizationProofs.insert_masked
#print axioms NormalizationProofs.remove_masked
#print axioms NormalizationProofs.contains_masked
#print axioms NormalizationProofs.history_masked
#print axioms NormalizationProofs.raw_history_no_false_rejection
#print axioms NormalizationProofs.pack_match_four_raw_hashes
#print axioms NormalizationProofs.pack_match_short_raw_hashes
#print axioms NormalizationProofs.pack_match_raw_history
