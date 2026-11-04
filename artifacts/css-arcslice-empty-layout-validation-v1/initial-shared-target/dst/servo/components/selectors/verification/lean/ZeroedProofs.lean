/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Generated.StyloBloomVerification

open Aeneas Aeneas.Std Result Bloom

namespace ZeroedProofs

def AllZero (values : List U8) : Prop := ∀ value ∈ values, value = 0#u8

theorem loop_exact (iter : core.slice.iter.Iter U8) :
    bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.is_zeroed_loop iter
      ⦃ found => found = true ↔ AllZero (iter.slice.val.drop iter.i) ⦄ := by
  unfold bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.is_zeroed_loop
  refine loop.spec_decr_nat (fun it : core.slice.iter.Iter U8 => it.slice.val.length - it.i)
    (fun it => AllZero (it.slice.val.drop it.i) ↔ AllZero (iter.slice.val.drop iter.i))
    (fun found => found = true ↔ AllZero (iter.slice.val.drop iter.i))
    bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.is_zeroed_loop.body iter ?_ ?_
  · intro it invariant
    unfold bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.is_zeroed_loop.body
      core.slice.iter.IteratorSliceIter.next
    split
    · rename_i hnext
      have hi : it.i < it.slice.val.length := hnext
      simp only [bind_ok]
      dsimp! only
      split
      · rename_i hnonzero
        simp only [WP.spec_ok, Bool.false_eq_true, false_iff]
        intro hz
        have hhead := invariant.mpr hz it.slice.val[it.i] (by
          rw [List.drop_eq_getElem_cons hi]
          exact List.mem_cons_self)
        have hhead' : it.slice[it.i] = 0#u8 := hhead
        simp only [bne_iff_ne] at hnonzero
        exact hnonzero hhead'
      · rename_i hzero
        simp only [bne_iff_ne, not_not] at hzero
        have hzero' : it.slice.val[it.i] = 0#u8 := hzero
        simp only [WP.spec_ok]
        refine ⟨?_, by omega⟩
        rw [← invariant, List.drop_eq_getElem_cons hi]
        simp [AllZero, hzero']
    · rename_i hdone
      have hi : it.slice.val.length ≤ it.i := Nat.le_of_not_gt hdone
      simp only [bind_ok]
      dsimp! only
      simp only [WP.spec_ok, true_iff]
      apply invariant.mp
      simp [AllZero, List.drop_eq_nil_of_le hi]
  · rfl

theorem zeroed_exact (filter : bloom.CountingBloomFilter bloom.BloomStorageU8) :
    zeroed filter ⦃ found => found = true ↔
      ∀ index : Nat, index < 4096 → filter.storage.counters.val[index]! = 0#u8 ⦄ := by
  unfold zeroed bloom.CountingBloomFilter.is_zeroed
  dsimp only
  unfold bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.is_zeroed
  step as ⟨iter, hslice, hi⟩
  apply WP.spec_mono (loop_exact iter)
  intro result hresult
  rw [hresult, hslice, hi]
  simp only [List.drop_zero, AllZero]
  constructor
  · intro hz index hindex
    have hlength : index < filter.storage.counters.val.length := by simpa using hindex
    simpa only [getElem!_pos filter.storage.counters.val index hlength] using hz _ (List.getElem_mem hlength)
  · intro hz value hmem
    obtain ⟨index, hindex, rfl⟩ := List.mem_iff_getElem.mp hmem
    have hbound : index < 4096 := by simpa using hindex
    simpa only [getElem!_pos filter.storage.counters.val index hindex] using hz index hbound

theorem zeroed_true (filter : bloom.CountingBloomFilter bloom.BloomStorageU8)
    (zeros : ∀ index : Nat, index < 4096 → filter.storage.counters.val[index]! = 0#u8) :
    zeroed filter ⦃ found => found = true ⦄ := by
  apply WP.spec_mono (zeroed_exact filter)
  intro found hfound
  exact hfound.mpr zeros

end ZeroedProofs

#print axioms ZeroedProofs.loop_exact
#print axioms ZeroedProofs.zeroed_exact
#print axioms ZeroedProofs.zeroed_true
