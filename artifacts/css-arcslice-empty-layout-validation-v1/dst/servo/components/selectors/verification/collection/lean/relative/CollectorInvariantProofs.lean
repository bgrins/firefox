/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.CollectorStepProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection CollectionStepProofs
set_option linter.unusedSimpArgs false
namespace CollectionInvariantProofs

def masked (hash : U32) : U32 := ⟨hash.bv &&& 16777215#32⟩

theorem store_some (hash : U32) (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) :
    storeHash (some hash) hashes len ⦃ r =>
      r.2.2.val = len.val + 1 ∧
      r.2.1 = hashes.set len (masked hash) ∧
      r.1 = decide (len.val + 1 < 4) ⦄ := by
  unfold storeHash
  simp only [bloom.BLOOM_HASH_MASK]
  step*
  simp_all [CollectionInvariantProofs.masked, UScalar.eq_equiv_bv_eq]
  constructor
  · congr 1
    exact (UScalar.eq_equiv_bv_eq _ _).mpr masked_post1
  · apply Bool.eq_iff_iff.mpr
    simp [bne_iff_ne]
    scalar_tac

def prefixAllowed (allowed : U32 → Prop) (hashes : Array U32 4#usize) (len : Nat) : Prop :=
  ∀ i, i < len → allowed hashes[i]!

theorem store_preserves_allowed (allowed : U32 → Prop)
    (hash : U32) (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : prefixAllowed allowed hashes len.val)
    (required : allowed (masked hash)) :
    storeHash (some hash) hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ prefixAllowed allowed r.2.1 r.2.2.val ⦄ := by
  apply WP.spec_mono (store_some hash hashes len h)
  intro r hr
  rcases hr with ⟨hlen, harray, _⟩
  rw [hlen, harray]
  constructor
  · omega
  · intro i hi
    by_cases heq : len.val = i
    · rw [Array.getElem!_Nat_set_eq hashes len i (masked hash) ⟨heq, by scalar_tac⟩]
      exact required
    · rw [Array.getElem!_Nat_set_ne hashes len i (masked hash) heq]
      exact before i (by omega)

theorem store_some_full (allowed : U32 → Prop)
    (hash : U32) (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : prefixAllowed allowed hashes len.val)
    (required : allowed (masked hash)) :
    storeHash (some hash) hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      prefixAllowed allowed r.2.1 r.2.2.val ⦄ := by
  apply WP.spec_mono (store_some hash hashes len h)
  intro r hr
  rcases hr with ⟨hlen, harray, hflag⟩
  rw [hlen, harray, hflag]
  refine ⟨by omega, by simp, ?_⟩
  intro i hi
  by_cases heq : len.val = i
  · rw [Array.getElem!_Nat_set_eq hashes len i (masked hash) ⟨heq, by scalar_tac⟩]
    exact required
  · rw [Array.getElem!_Nat_set_ne hashes len i (masked hash) heq]
    exact before i (by omega)

variable {I A D L N P BN BL C E Walk : Type}
local notation "Component" => parser.Component I A D L N P BN BL C E
local notation "Instance" => parser.SelectorHashIterator Walk I A D L N P BN BL C E

theorem simple_component_preserves (allowed : U32 → Prop)
    (inst : Instance) (component : Component) (quirks : context.QuirksMode)
    (hashes : Array U32 4#usize) (len : Usize)
    (h : len.val < 4) (before : prefixAllowed allowed hashes len.val)
    (hnested : nested component = false)
    (hash_spec : parser.simple_selector_hash inst.SelectorImplInst component quirks
      ⦃ result => ∀ raw ∈ result, allowed (masked raw) ⦄) :
    parser.collect_component_hashes inst component quirks hashes len ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      prefixAllowed allowed r.2.1 r.2.2.val ⦄ := by
  rw [simple_component_step inst component hnested]
  step as ⟨result, hresult⟩
  cases result with
  | none => simp [storeHash, before]; omega
  | some hash =>
    apply store_some_full allowed hash hashes len h before
    exact hresult hash (by simp)

#print axioms simple_component_preserves
#print axioms store_some_full

#print axioms store_preserves_allowed

#print axioms store_some
end CollectionInvariantProofs
