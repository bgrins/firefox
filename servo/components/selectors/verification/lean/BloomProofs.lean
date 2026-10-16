/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Generated.StyloBloomVerification

open Aeneas Aeneas.Std Result
open Bloom

namespace BloomProofs

abbrev Filter := bloom.CountingBloomFilter bloom.BloomStorageU8

def empty : Filter := ⟨⟨Array.repeat 4096#usize 0#u8⟩⟩

theorem new_eq_empty : Bloom.new = ok empty := by
  simp [Bloom.new, bloom.CountingBloomFilter.new,
    bloom.CountingBloomFilter.Insts.CoreDefaultDefault.default,
    bloom.BloomStorageU8.Insts.CoreDefaultDefault.default, empty]

theorem clear_eq_empty (filter : Filter) : Bloom.clear filter = ok empty := by
  simp [Bloom.clear, bloom.CountingBloomFilter.clear,
    bloom.BloomStorageU8.Insts.CoreDefaultDefault.default, empty]

theorem saturated_slot_unchanged (s : bloom.BloomStorageU8) (i : Usize)
    (increment : Bool) (hi : i.val < s.counters.length)
    (hs : s.counters.val[i.val] = 255#u8) :
    bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.adjust_slot
      s i increment ⦃ s' => s' = s ⦄ := by
  unfold bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.adjust_slot
  step
  simp_all
  have he := Array.set_getElem_eq s.counters i hi
  change s.counters.set i s.counters.val[i.val] = s.counters at he
  rw [hs] at he
  rw [he]

@[step]
theorem key_mask_spec : bloom.KEY_MASK ⦃ i => i = 4095#u32 ⦄ := by
  unfold bloom.KEY_MASK
  simp only [bloom.KEY_SIZE]
  step
  step
  scalar_tac

@[step]
theorem hash1_spec (hash : U32) :
    bloom.hash1 hash ⦃ i => i.val = hash.val &&& 4095 ∧ i.val < 4096 ⦄ := by
  unfold bloom.hash1
  step
  simp_all
  have : hash.val &&& 4095 ≤ 4095 := Nat.and_le_right
  omega

@[step]
theorem hash2_spec (hash : U32) :
    bloom.hash2 hash ⦃ i => i.val = (hash.val >>> 12) &&& 4095 ∧ i.val < 4096 ⦄ := by
  unfold bloom.hash2
  simp only [bloom.KEY_SIZE]
  step
  step
  simp_all
  have : (hash.val >>> 12) &&& 4095 ≤ 4095 := Nat.and_le_right
  omega

@[step]
theorem first_index_spec (hash : U32) :
    bloom.BloomStorage.first_slot_index.default bloom.BloomStorageU8 hash
      ⦃ i => i.val = hash.val &&& 4095 ∧ i.val < 4096 ⦄ := by
  unfold bloom.BloomStorage.first_slot_index.default
  step
  simp_all

@[step]
theorem second_index_spec (hash : U32) :
    bloom.BloomStorage.second_slot_index.default bloom.BloomStorageU8 hash
      ⦃ i => i.val = (hash.val >>> 12) &&& 4095 ∧ i.val < 4096 ⦄ := by
  unfold bloom.BloomStorage.second_slot_index.default
  step
  simp_all

@[step]
theorem slot_is_empty_spec (s : bloom.BloomStorageU8) (i : Usize)
    (hi : i.val < s.counters.length) :
    bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.slot_is_empty
      s i ⦃ b => b = decide (s.counters.val[i.val] = 0#u8) ⦄ := by
  unfold bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.slot_is_empty
  step
  simp_all

theorem contains_of_nonzero (filter : Filter) (hash : U32)
    (hfirst : filter.storage.counters.val[hash.val &&& 4095]! ≠ 0#u8)
    (hsecond : filter.storage.counters.val[(hash.val >>> 12) &&& 4095]! ≠ 0#u8) :
    Bloom.contains filter hash ⦃ b => b = true ⦄ := by
  have hi1 : hash.val &&& 4095 < filter.storage.counters.val.length := by
    have : hash.val &&& 4095 ≤ 4095 := Nat.and_le_right
    simp
    omega
  have hi2 : (hash.val >>> 12) &&& 4095 < filter.storage.counters.val.length := by
    have : (hash.val >>> 12) &&& 4095 ≤ 4095 := Nat.and_le_right
    simp
    omega
  rw [getElem!_pos filter.storage.counters.val (hash.val &&& 4095) hi1] at hfirst
  rw [getElem!_pos filter.storage.counters.val ((hash.val >>> 12) &&& 4095) hi2] at hsecond
  unfold Bloom.contains bloom.CountingBloomFilter.might_contain_hash
  simp only
  step
  step
  simp_all
  step
  step
  simp_all

end BloomProofs

#print axioms BloomProofs.new_eq_empty
#print axioms BloomProofs.clear_eq_empty
#print axioms BloomProofs.saturated_slot_unchanged
#print axioms BloomProofs.key_mask_spec
#print axioms BloomProofs.hash1_spec
#print axioms BloomProofs.hash2_spec
#print axioms BloomProofs.first_index_spec
#print axioms BloomProofs.second_index_spec
#print axioms BloomProofs.slot_is_empty_spec
#print axioms BloomProofs.contains_of_nonzero
