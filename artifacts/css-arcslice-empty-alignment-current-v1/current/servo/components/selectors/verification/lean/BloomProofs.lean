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

def Represents (storage : bloom.BloomStorageU8) (counts : Nat → Nat) : Prop :=
  ∀ j : Nat, j < 4096 →
    (storage.counters.val[j]!).val = 255 ∨
    (storage.counters.val[j]!).val = counts j

@[step]
theorem adjust_slot_represents (s : bloom.BloomStorageU8) (counts : Nat → Nat)
    (i : Usize) (increment : Bool) (hi : i.val < 4096)
    (hrep : Represents s counts) (hvalid : increment = false → 0 < counts i.val) :
    bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.adjust_slot
      s i increment ⦃ s' => Represents s' (Function.update counts i.val
        (if increment then counts i.val + 1 else counts i.val - 1)) ⦄ := by
  have hslot := hrep i.val hi
  have hlen : i.val < s.counters.val.length := by simp; omega
  rw [getElem!_pos s.counters.val i.val hlen] at hslot
  unfold bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.adjust_slot
  step
  subst slot index_mut_back
  split
  · rename_i hnotfull
    have hnotfullval : (s.counters.val[i.val]).val ≠ 255 := by
      scalar_tac
    have hcount : (s.counters.val[i.val]).val = counts i.val := hslot.resolve_left hnotfullval
    split
    · step
      simp only [Represents]
      intro j hj
      by_cases heq : i.val = j
      · subst j
        have hset := Array.getElem!_Nat_set_eq s.counters i i.val slot1 ⟨rfl, by simpa using hi⟩
        simp only [Array.getElem!_Nat_eq] at hset
        rw [hset]
        simp only [Function.update_self]
        right
        omega
      · simpa [Array.set_val_eq, Function.update, heq, Ne.symm heq] using hrep j hj
    · step
      simp only [Represents]
      intro j hj
      by_cases heq : i.val = j
      · subst j
        have hset := Array.getElem!_Nat_set_eq s.counters i i.val slot1 ⟨rfl, by simpa using hi⟩
        simp only [Array.getElem!_Nat_eq] at hset
        rw [hset]
        simp only [Function.update_self]
        right
        omega
      · simpa [Array.set_val_eq, Function.update, heq, Ne.symm heq] using hrep j hj
  · rename_i hfull
    have hfullval : (s.counters.val[i.val]).val = 255 := by scalar_tac
    simp only [WP.spec_ok, Represents]
    intro j hj
    by_cases heq : i.val = j
    · subst j
      left
      have hset := Array.set_getElem_eq s.counters i (by simpa using hi)
      change s.counters.set i s.counters.val[i.val] = s.counters at hset
      rw [hset]
      simpa only [getElem!_pos s.counters.val i.val hlen] using hfullval
    · simpa [Array.set_val_eq, Function.update, heq, Ne.symm heq] using hrep j hj

def contributions (hash : U32) (slot : Nat) : Nat :=
  (if slot = hash.val &&& 4095 then 1 else 0) +
  (if slot = (hash.val >>> 12) &&& 4095 then 1 else 0)

@[step]
theorem insert_represents (filter : Filter) (counts : Nat → Nat) (hash : U32)
    (hrep : Represents filter.storage counts) :
    Bloom.insert filter hash ⦃ f => Represents f.storage
      (fun j => counts j + contributions hash j) ⦄ := by
  unfold Bloom.insert bloom.CountingBloomFilter.insert_hash
  simp only
  step as ⟨first, hfirst, hfirstbound⟩
  step as ⟨firstStorage, hfirstStorage⟩
  step as ⟨second, hsecond, hsecondbound⟩
  step as ⟨finalStorage, hfinalStorage⟩
  convert hfinalStorage using 1
  funext j
  simp only [↓reduceIte, hfirst, hsecond]
  simp [contributions, Function.update]
  split_ifs <;> simp_all

@[step]
theorem remove_represents (filter : Filter) (counts : Nat → Nat) (hash : U32)
    (hrep : Represents filter.storage counts)
    (hvalid : ∀ j, contributions hash j ≤ counts j) :
    Bloom.remove filter hash ⦃ f => Represents f.storage
      (fun j => counts j - contributions hash j) ⦄ := by
  unfold Bloom.remove bloom.CountingBloomFilter.remove_hash
  simp only
  step as ⟨first, hfirst, hfirstbound⟩
  have hfirstPositive : 0 < counts first.val := by
    have hv := hvalid first.val
    simp [contributions, ← hfirst] at hv
    omega
  step as ⟨firstStorage, hfirstStorage⟩
  step as ⟨second, hsecond, hsecondbound⟩
  have hsecondPositive : 0 < Function.update counts first.val (counts first.val - 1) second.val := by
    have hv := hvalid second.val
    simp only [contributions, ← hfirst, ← hsecond] at hv
    by_cases heq : second.val = first.val
    · simp [Function.update, heq] at *
      omega
    · simp [Function.update, heq] at *
      omega
  step as ⟨finalStorage, hfinalStorage⟩
  convert hfinalStorage using 1
  funext j
  simp only [hfirst, hsecond]
  simp [contributions, Function.update]
  split_ifs <;> simp_all
  omega

def liveCounts : List U32 → Nat → Nat
  | [], _ => 0
  | hash :: rest, j => contributions hash j + liveCounts rest j

theorem liveCounts_append (xs ys : List U32) (j : Nat) :
    liveCounts (xs ++ ys) j = liveCounts xs j + liveCounts ys j := by
  induction xs with
  | nil => simp [liveCounts]
  | cons hash rest ih => simp [liveCounts, ih, Nat.add_assoc]

theorem member_contributions (hash : U32) (live : List U32) (j : Nat)
    (hmem : hash ∈ live) : contributions hash j ≤ liveCounts live j := by
  induction live with
  | nil => simp at hmem
  | cons head rest ih =>
    simp only [List.mem_cons] at hmem
    rcases hmem with rfl | hmem
    · simp [liveCounts]
    · have h := ih hmem
      simp only [liveCounts]
      omega

theorem empty_represents : Represents empty.storage (liveCounts []) := by
  intro j hj
  right
  change ((Array.repeat 4096#usize 0#u8).val[j]!).val = 0
  rw [Array.repeat_val]
  rw [getElem!_pos _ _ (by simp only [List.length_replicate]; scalar_tac)]
  simp only [List.getElem_replicate]
  rfl

inductive ValidHistory : Filter → List U32 → Prop where
  | empty : ValidHistory empty []
  | insert {filter next live hash} :
      ValidHistory filter live → Bloom.insert filter hash = ok next →
      ValidHistory next (hash :: live)
  | remove {filter next before after hash} :
      ValidHistory filter (before ++ hash :: after) → Bloom.remove filter hash = ok next →
      ValidHistory next (before ++ after)
  | clear {filter next live} :
      ValidHistory filter live → Bloom.clear filter = ok next → ValidHistory next []

theorem history_represents {filter : Filter} {live : List U32}
    (history : ValidHistory filter live) : Represents filter.storage (liveCounts live) := by
  induction history with
  | empty => exact empty_represents
  | @insert filter next live hash _ hrun ih =>
    have h := insert_represents filter (liveCounts live) hash ih
    rw [hrun] at h
    simp only [WP.spec_ok] at h
    convert h using 1
    funext j
    simp [liveCounts, Nat.add_comm]
  | @remove filter next before after hash _ hrun ih =>
    have hvalid : ∀ j, contributions hash j ≤ liveCounts (before ++ hash :: after) j := by
      intro j
      simp [liveCounts_append, liveCounts]
      omega
    have h := remove_represents filter (liveCounts (before ++ hash :: after)) hash ih hvalid
    rw [hrun] at h
    simp only [WP.spec_ok] at h
    convert h using 1
    funext j
    simp [liveCounts_append, liveCounts]
    omega
  | clear _ hrun _ =>
    rw [clear_eq_empty] at hrun
    have h : ok empty ⦃ f => Represents f.storage (liveCounts []) ⦄ := by
      simpa only [WP.spec_ok] using empty_represents
    rw [hrun] at h
    simpa only [WP.spec_ok] using h

theorem history_no_false_negatives {filter : Filter} {live : List U32}
    (history : ValidHistory filter live) (hash : U32) (hmem : hash ∈ live) :
    Bloom.contains filter hash ⦃ found => found = true ⦄ := by
  have hrep := history_represents history
  have hnonzero : ∀ j, j < 4096 → 0 < contributions hash j →
      filter.storage.counters.val[j]! ≠ 0#u8 := by
    intro j hj hpositive hzero
    have hc := member_contributions hash live j hmem
    have hr := hrep j hj
    rw [hzero] at hr
    norm_num at hr
    omega
  apply contains_of_nonzero
  · apply hnonzero
    · have := Nat.and_le_right (n := hash.val) (m := 4095)
      omega
    · simp [contributions]
  · apply hnonzero
    · have := Nat.and_le_right (n := hash.val >>> 12) (m := 4095)
      omega
    · simp [contributions]

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
#print axioms BloomProofs.adjust_slot_represents
#print axioms BloomProofs.insert_represents
#print axioms BloomProofs.remove_represents
#print axioms BloomProofs.liveCounts_append
#print axioms BloomProofs.member_contributions
#print axioms BloomProofs.empty_represents
#print axioms BloomProofs.history_represents
#print axioms BloomProofs.history_no_false_negatives
