/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import BloomProofs

open Aeneas Aeneas.Std Result Bloom BloomProofs

namespace StyleBloomProofs

def Exact (storage : bloom.BloomStorageU8) (counts : Nat → Nat) : Prop :=
  ∀ j : Nat, j < 4096 → (storage.counters.val[j]!).val = counts j

@[step]
theorem adjust_slot_exact (s : bloom.BloomStorageU8) (counts : Nat → Nat)
    (i : Usize) (increment : Bool) (hi : i.val < 4096)
    (hexact : Exact s counts) (hbound : counts i.val < 255)
    (hvalid : increment = false → 0 < counts i.val) :
    bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.adjust_slot
      s i increment ⦃ s' => Exact s' (Function.update counts i.val
        (if increment then counts i.val + 1 else counts i.val - 1)) ⦄ := by
  have hcount := hexact i.val hi
  have hlen : i.val < s.counters.val.length := by simp; omega
  rw [getElem!_pos s.counters.val i.val hlen] at hcount
  unfold bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.adjust_slot
  step
  subst slot index_mut_back
  split
  · split
    all_goals
      step
      simp only [Exact]
      intro j hj
      by_cases heq : i.val = j
      · subst j
        have hset := Array.getElem!_Nat_set_eq s.counters i i.val slot1 ⟨rfl, by simpa using hi⟩
        simp only [Array.getElem!_Nat_eq] at hset
        rw [hset]
        simp only [Function.update_self]
        omega
      · simpa [Array.set_val_eq, Function.update, heq, Ne.symm heq] using hexact j hj
  · rename_i hs
    have : (s.counters.val[i.val]).val = 255 := by scalar_tac
    omega

@[step]
theorem insert_exact (filter : Filter) (counts : Nat → Nat) (hash : U32)
    (hexact : Exact filter.storage counts)
    (hbound : ∀ j, counts j + contributions hash j < 255) :
    Bloom.insert filter hash ⦃ f => Exact f.storage
      (fun j => counts j + contributions hash j) ⦄ := by
  unfold Bloom.insert bloom.CountingBloomFilter.insert_hash
  simp only
  step as ⟨first, hfirst, hfirstbound⟩
  have hb1 : counts first.val < 255 := by have := hbound first.val; omega
  step as ⟨firstStorage, hfirstStorage⟩
  step as ⟨second, hsecond, hsecondbound⟩
  have hb2 : Function.update counts first.val (counts first.val + 1) second.val < 255 := by
    have hb := hbound second.val
    simp only [contributions, ← hfirst, ← hsecond] at hb
    by_cases heq : first.val = second.val
    · simp [Function.update, heq] at *; omega
    · simp [Function.update, heq, Ne.symm heq] at *; omega
  step as ⟨finalStorage, hfinalStorage⟩
  convert hfinalStorage using 1
  funext j
  simp only [↓reduceIte, hfirst, hsecond]
  simp [contributions, Function.update]
  split_ifs <;> simp_all

@[step]
theorem remove_exact (filter : Filter) (counts : Nat → Nat) (hash : U32)
    (hexact : Exact filter.storage counts)
    (hbound : ∀ j, counts j < 255)
    (hvalid : ∀ j, contributions hash j ≤ counts j) :
    Bloom.remove filter hash ⦃ f => Exact f.storage
      (fun j => counts j - contributions hash j) ⦄ := by
  unfold Bloom.remove bloom.CountingBloomFilter.remove_hash
  simp only
  step as ⟨first, hfirst, hfirstbound⟩
  have hb1 := hbound first.val
  have hfirstPositive : 0 < counts first.val := by
    have hv := hvalid first.val
    simp [contributions, ← hfirst] at hv
    omega
  step as ⟨firstStorage, hfirstStorage⟩
  step as ⟨second, hsecond, hsecondbound⟩
  have hb2 : Function.update counts first.val (counts first.val - 1) second.val < 255 := by
    have := hbound second.val
    simp [Function.update]; split_ifs <;> omega
  have hsecondPositive : 0 < Function.update counts first.val (counts first.val - 1) second.val := by
    have hv := hvalid second.val
    simp only [contributions, ← hfirst, ← hsecond] at hv
    by_cases heq : second.val = first.val
    · simp [Function.update, heq] at *; omega
    · simp [Function.update, heq] at *; omega
  step as ⟨finalStorage, hfinalStorage⟩
  convert hfinalStorage using 1
  funext j
  simp only [hfirst, hsecond]
  simp [contributions, Function.update]
  split_ifs <;> simp_all
  omega

theorem liveCounts_bound (live : List U32) (j : Nat) :
    liveCounts live j ≤ 2 * live.length := by
  induction live with
  | nil => simp [liveCounts]
  | cons hash rest ih =>
    have : contributions hash j ≤ 2 := by simp only [contributions]; split_ifs <;> omega
    simp only [liveCounts, List.length_cons]
    omega

theorem empty_exact : Exact empty.storage (liveCounts []) := by
  intro j hj
  change ((Array.repeat 4096#usize 0#u8).val[j]!).val = 0
  rw [Array.repeat_val]
  rw [getElem!_pos _ _ (by simp only [List.length_replicate]; scalar_tac)]
  simp only [List.getElem_replicate]
  rfl

inductive HighWaterHistory : Filter → List U32 → Nat → Prop where
  | empty : HighWaterHistory empty [] 0
  | insert {filter next live hash high} :
      HighWaterHistory filter live high → Bloom.insert filter hash = ok next →
      HighWaterHistory next (live ++ [hash]) (max high (live.length + 1))
  | remove {filter next before after hash high} :
      HighWaterHistory filter (before ++ hash :: after) high → Bloom.remove filter hash = ok next →
      HighWaterHistory next (before ++ after) high
  | clear {filter next live high} :
      HighWaterHistory filter live high → Bloom.clear filter = ok next → HighWaterHistory next [] 0

theorem history_length_le {filter live high} (history : HighWaterHistory filter live high) :
    live.length ≤ high := by
  induction history with
  | empty => simp
  | insert _ _ _ => simp
  | remove _ _ ih => simp only [List.length_append, List.length_cons] at *; omega
  | clear _ _ _ => simp

theorem history_exact {filter live high} (history : HighWaterHistory filter live high)
    (hbound : high ≤ 127) : Exact filter.storage (liveCounts live) := by
  induction history with
  | empty => exact empty_exact
  | @insert filter next live hash high history hrun ih =>
    have hlen := history_length_le history
    have hb : ∀ j, liveCounts live j + contributions hash j < 255 := by
      intro j
      have hc := liveCounts_bound (hash :: live) j
      simp only [liveCounts, List.length_cons] at hc
      omega
    have he := insert_exact filter (liveCounts live) hash (ih (by omega)) hb
    rw [hrun] at he
    simp only [WP.spec_ok] at he
    convert he using 1
    funext j
    simp [liveCounts_append, liveCounts]
  | @remove filter next before after hash high history hrun ih =>
    have hlen := history_length_le history
    have hb : ∀ j, liveCounts (before ++ hash :: after) j < 255 := by
      intro j
      have hc := liveCounts_bound (before ++ hash :: after) j
      omega
    have hv : ∀ j, contributions hash j ≤ liveCounts (before ++ hash :: after) j := by
      intro j
      simp only [liveCounts_append, liveCounts]
      omega
    have he := remove_exact filter (liveCounts (before ++ hash :: after)) hash (ih hbound) hb hv
    rw [hrun] at he
    simp only [WP.spec_ok] at he
    convert he using 1
    funext j
    simp only [liveCounts_append, liveCounts]
    omega
  | clear _ hrun _ =>
    rw [clear_eq_empty] at hrun
    have h : ok empty ⦃ f => Exact f.storage (liveCounts []) ⦄ := by
      simpa only [WP.spec_ok] using empty_exact
    rw [hrun] at h
    simpa only [WP.spec_ok] using h

theorem clear_loop_exact (iter : core.slice.iter.Iter U32) (filter : Filter)
    (hlen : iter.slice.val.length ≤ 127)
    (hexact : Exact filter.storage (liveCounts (iter.slice.val.drop iter.i))) :
    style_bloom_filter.clear_filter_loop iter filter ⦃ f => Exact f.storage (liveCounts []) ⦄ := by
  unfold style_bloom_filter.clear_filter_loop
  refine loop.spec_decr_nat (fun (p : core.slice.iter.Iter U32 × Filter) => p.1.slice.val.length - p.1.i)
    (fun p => p.1.slice.val.length ≤ 127 ∧
      Exact p.2.storage (liveCounts (p.1.slice.val.drop p.1.i)))
    (fun f => Exact f.storage (liveCounts []))
    (fun (it, f) => style_bloom_filter.clear_filter_loop.body it f) (iter, filter) ?_ ?_
  · intro p hp
    rcases p with ⟨it, f⟩
    rcases hp with ⟨hl, he⟩
    dsimp only at hl he ⊢
    unfold style_bloom_filter.clear_filter_loop.body core.slice.iter.IteratorSliceIter.next
    split
    · rename_i hnext
      have hi : it.i < it.slice.val.length := hnext
      have hb : ∀ j, liveCounts (it.slice.val.drop it.i) j < 255 := by
        intro j
        have hc := liveCounts_bound (it.slice.val.drop it.i) j
        simp only [List.length_drop] at hc
        omega
      have hv : ∀ j, contributions it.slice[it.i] j ≤ liveCounts (it.slice.val.drop it.i) j := by
        intro j
        change contributions it.slice.val[it.i] j ≤ liveCounts (it.slice.val.drop it.i) j
        rw [List.drop_eq_getElem_cons hi]
        simp [liveCounts]
      have hr := remove_exact f (liveCounts (it.slice.val.drop it.i)) it.slice[it.i] he hb hv
      unfold Bloom.remove at hr
      simp only [bind_ok]
      dsimp! only
      step with hr as ⟨f', hf⟩
      refine ⟨hl, ?_, ?_⟩
      · convert hf using 1
        funext j
        rw [List.drop_eq_getElem_cons hi]
        change liveCounts (it.slice.val.drop (it.i + 1)) j =
          contributions it.slice.val[it.i] j + liveCounts (it.slice.val.drop (it.i + 1)) j -
            contributions it.slice.val[it.i] j
        omega
      · omega
    · rename_i hdone
      have hi : it.slice.val.length ≤ it.i := by exact Nat.le_of_not_gt hdone
      simp only [bind_ok]
      dsimp! only
      simpa only [WP.spec_ok, List.drop_eq_nil_of_le hi, liveCounts] using he
  · exact ⟨hlen, hexact⟩

@[step]
theorem update_high_water_spec (previous length : Usize) :
    style_bloom_filter.update_high_water previous length ⦃ high =>
      high.val = max previous.val length.val ⦄ := by
  simp only [style_bloom_filter.update_high_water, core.cmp.impls.OrdUsize.max, WP.spec_ok]
  split <;> simp_all [max_def]

theorem clear_filter_exact (filter : Filter) (hashes : Slice U32) (high : Usize)
    (history : HighWaterHistory filter hashes.val high.val) :
    style_bloom_filter.clear_filter filter hashes high ⦃ f => Exact f.storage (liveCounts []) ⦄ := by
  unfold style_bloom_filter.clear_filter
  split
  · have h := clear_eq_empty filter
    unfold Bloom.clear at h
    rw [h]
    simpa only [WP.spec_ok] using empty_exact
  · rename_i hsmall
    have hh : high.val ≤ 25 := by simp only [style_bloom_filter.MEMSET_CLEAR_THRESHOLD] at hsmall; scalar_tac
    have hl := history_length_le history
    have he := history_exact history (by omega)
    step as ⟨iter, hslice, hi⟩
    apply clear_loop_exact
    · simp only [hslice]
      omega
    · simpa [hslice, hi] using he

theorem exact_empty_eq (filter : Filter) (h : Exact filter.storage (liveCounts [])) :
    filter = empty := by
  rcases filter with ⟨⟨counters⟩⟩
  have he : counters = Array.repeat 4096#usize 0#u8 := by
    apply Aeneas.Std.Array.ext
    apply List.ext_getElem
    · exact (Aeneas.Std.Array.property counters).trans (Aeneas.Std.Array.property (Array.repeat 4096#usize 0#u8)).symm
    · intro i hi hj
      have hi4096 : i < 4096 := by simpa using hi
      have hc := h i hi4096
      simp only [liveCounts, getElem!_pos counters.val i hi] at hc
      simp only [Array.repeat_val, List.getElem_replicate]
      scalar_tac
  simp only [he, empty]

theorem clear_filter_eq_empty (filter : Filter) (hashes : Slice U32) (high : Usize)
    (history : HighWaterHistory filter hashes.val high.val) :
    style_bloom_filter.clear_filter filter hashes high ⦃ f => f = empty ⦄ := by
  step with clear_filter_exact filter hashes high history as ⟨f, hf⟩
  exact exact_empty_eq f hf

theorem clear_filter_resets_history (filter : Filter) (hashes : Slice U32) (high : Usize)
    (history : HighWaterHistory filter hashes.val high.val) :
    style_bloom_filter.clear_filter filter hashes high ⦃ f => HighWaterHistory f [] 0 ⦄ := by
  step with clear_filter_eq_empty filter hashes high history as ⟨f, hf⟩
  rw [hf]
  exact HighWaterHistory.empty

end StyleBloomProofs

#print axioms StyleBloomProofs.adjust_slot_exact
#print axioms StyleBloomProofs.insert_exact
#print axioms StyleBloomProofs.remove_exact
#print axioms StyleBloomProofs.liveCounts_bound
#print axioms StyleBloomProofs.empty_exact
#print axioms StyleBloomProofs.history_length_le
#print axioms StyleBloomProofs.history_exact
#print axioms StyleBloomProofs.clear_loop_exact
#print axioms StyleBloomProofs.update_high_water_spec
#print axioms StyleBloomProofs.clear_filter_exact
#print axioms StyleBloomProofs.exact_empty_eq
#print axioms StyleBloomProofs.clear_filter_eq_empty

#print axioms StyleBloomProofs.clear_filter_resets_history
