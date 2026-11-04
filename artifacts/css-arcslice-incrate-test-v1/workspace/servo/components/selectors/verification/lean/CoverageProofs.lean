/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import BloomProofs

open Aeneas Aeneas.Std Result Bloom BloomProofs

namespace CoverageProofs

def Present (filter : Filter) (hash : U32) : Prop :=
  filter.storage.counters.val[hash.val &&& 4095]! ≠ 0#u8 ∧
  filter.storage.counters.val[(hash.val >>> 12) &&& 4095]! ≠ 0#u8

theorem present_lookup (filter : Filter) (hash : U32) (h : Present filter hash) :
    Bloom.contains filter hash ⦃ found => found = true ⦄ :=
  contains_of_nonzero filter hash h.1 h.2

theorem insert_preserves_nonzero (filter : Filter) (hash : U32) :
    Bloom.insert filter hash ⦃ next =>
      ∀ j : Nat, j < 4096 → filter.storage.counters.val[j]! ≠ 0#u8 →
        next.storage.counters.val[j]! ≠ 0#u8 ⦄ := by
  let counts := fun (j : Nat) => (filter.storage.counters.val[j]!).val
  have hrep : Represents filter.storage counts := fun _ _ => Or.inr rfl
  step with insert_represents filter counts hash hrep as ⟨next, hnext⟩
  rename_i j hj hbefore
  intro hzero
  have hc := hnext j hj
  rw [hzero] at hc
  change 0 = 255 ∨ 0 = (filter.storage.counters.val[j]!).val + contributions hash j at hc
  have hz : (filter.storage.counters.val[j]!).val = 0 := by
    omega
  have : filter.storage.counters.val[j]! = 0#u8 := by scalar_tac
  exact hbefore this

theorem insert_preserves_present (filter : Filter) (hash existing : U32)
    (h : Present filter existing) :
    Bloom.insert filter hash ⦃ next => Present next existing ⦄ := by
  step with insert_preserves_nonzero filter hash as ⟨next, hnext⟩
  constructor
  · apply hnext _ (by have := Nat.and_le_right (n := existing.val) (m := 4095); omega) h.1
  · apply hnext _ (by have := Nat.and_le_right (n := existing.val >>> 12) (m := 4095); omega) h.2

theorem insert_establishes_present (filter : Filter) (hash : U32) :
    Bloom.insert filter hash ⦃ next => Present next hash ⦄ := by
  let counts := fun (j : Nat) => (filter.storage.counters.val[j]!).val
  have hrep : Represents filter.storage counts := fun _ _ => Or.inr rfl
  step with insert_represents filter counts hash hrep as ⟨next, hnext⟩
  have hn : ∀ j : Nat, j < 4096 → 0 < contributions hash j →
      next.storage.counters.val[j]! ≠ 0#u8 := by
    intro j hj hpositive hzero
    have hc := hnext j hj
    rw [hzero] at hc
    change 0 = 255 ∨ 0 = (filter.storage.counters.val[j]!).val + contributions hash j at hc
    omega
  constructor
  · apply hn
    · have := Nat.and_le_right (n := hash.val) (m := 4095)
      omega
    · simp [contributions]
  · apply hn
    · have := Nat.and_le_right (n := hash.val >>> 12) (m := 4095)
      omega
    · simp [contributions]

inductive Insertions : Filter → List U32 → Filter → Prop where
  | nil (filter : Filter) : Insertions filter [] filter
  | cons {before after final hash rest} :
      Bloom.insert before hash = ok after → Insertions after rest final →
      Insertions before (hash :: rest) final

theorem insertions_coverage {before final : Filter} {hashes : List U32}
    (steps : Insertions before hashes final) :
    (∀ hash, Present before hash → Present final hash) ∧
    (∀ hash ∈ hashes, Present final hash) := by
  induction steps with
  | nil filter => exact ⟨fun _ h => h, by simp⟩
  | @cons before after final inserted rest hrun _ ih =>
    have hnew := insert_establishes_present before inserted
    rw [hrun] at hnew
    simp only [WP.spec_ok] at hnew
    constructor
    · intro hash hp
      have hkeep := insert_preserves_present before inserted hash hp
      rw [hrun] at hkeep
      simp only [WP.spec_ok] at hkeep
      exact ih.1 hash hkeep
    · intro hash hm
      rcases List.mem_cons.mp hm with rfl | hm
      · exact ih.1 hash hnew
      · exact ih.2 hash hm

end CoverageProofs

#print axioms CoverageProofs.present_lookup
#print axioms CoverageProofs.insert_preserves_nonzero
#print axioms CoverageProofs.insert_preserves_present
#print axioms CoverageProofs.insert_establishes_present
#print axioms CoverageProofs.insertions_coverage
