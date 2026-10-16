/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import StyleBloomProofs
import CoverageProofs

open Aeneas Aeneas.Std Result Bloom BloomProofs StyleBloomProofs CoverageProofs

namespace StorageHistoryProofs

theorem history_represents {filter : Filter} {live : List U32} {high : Nat}
    (history : HighWaterHistory filter live high) : Represents filter.storage (liveCounts live) := by
  induction history with
  | empty => exact empty_represents
  | @insert filter next live hash high _ hrun ih =>
    have h := insert_represents filter (liveCounts live) hash ih
    rw [hrun] at h
    simp only [WP.spec_ok] at h
    convert h using 1
    funext j
    simp [liveCounts_append, liveCounts, Nat.add_comm]
  | @remove filter next before after hash high _ hrun ih =>
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

theorem history_present {filter : Filter} {live : List U32} {high : Nat}
    (history : HighWaterHistory filter live high) (hash : U32) (hmem : hash ∈ live) :
    Present filter hash := by
  have hrep := history_represents history
  have hnonzero : ∀ j, j < 4096 → 0 < contributions hash j →
      filter.storage.counters.val[j]! ≠ 0#u8 := by
    intro j hj hpositive hzero
    have hc := member_contributions hash live j hmem
    have hr := hrep j hj
    rw [hzero] at hr
    change 0 = 255 ∨ 0 = liveCounts live j at hr
    omega
  constructor
  · apply hnonzero
    · have := Nat.and_le_right (n := hash.val) (m := 4095)
      omega
    · simp [contributions]
  · apply hnonzero
    · have := Nat.and_le_right (n := hash.val >>> 12) (m := 4095)
      omega
    · simp [contributions]

theorem history_lookup {filter : Filter} {live : List U32} {high : Nat}
    (history : HighWaterHistory filter live high) (hash : U32) (hmem : hash ∈ live) :
    Bloom.contains filter hash ⦃ found => found = true ⦄ :=
  present_lookup filter hash (history_present history hash hmem)

theorem insertion_history {before final : Filter} {live hashes : List U32} {high : Nat}
    (history : HighWaterHistory before live high) (steps : Insertions before hashes final) :
    HighWaterHistory final (live ++ hashes) (max high (live.length + hashes.length)) := by
  induction steps generalizing live high with
  | nil filter =>
    have hle := history_length_le history
    simpa only [List.append_nil, List.length_nil, Nat.add_zero, Nat.max_eq_left hle] using history
  | @cons before after final inserted rest hrun _ ih =>
    have h := ih (HighWaterHistory.insert history hrun)
    convert h using 1
    · simp only [List.append_assoc, List.singleton_append]
    · simp only [List.length_append, List.length_cons, List.length_nil]
      omega

end StorageHistoryProofs

#print axioms StorageHistoryProofs.history_represents
#print axioms StorageHistoryProofs.history_present
#print axioms StorageHistoryProofs.history_lookup
#print axioms StorageHistoryProofs.insertion_history
