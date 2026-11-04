/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Normalized.FrameProofs
import NormalizationProofs
open Aeneas Aeneas.Std Result
open BloomProofs CollectionInvariantProofs CollectionFrameProofs
set_option maxRecDepth 4096
namespace CollectionRejectionProofs

theorem prefix_members {allowed : U32 → Prop} {hashes : Array U32 4#usize} {len : Nat}
    (h : prefixAllowed allowed hashes len) :
    ∀ hash ∈ hashes.val.take len, allowed hash := by
  intro hash member
  rcases List.mem_iff_getElem.mp member with ⟨i, hi, heq⟩
  have hiLen : i < len := by simp only [List.length_take] at hi; omega
  have hiArray : i < hashes.val.length := by simp only [List.length_take] at hi; omega
  have allowed := h i hiLen
  rw [Array.getElem!_Nat_eq, _root_.getElem!_pos hashes.val i hiArray] at allowed
  simp only [List.getElem_take] at heq
  exact heq ▸ allowed

theorem padding_members {hashes : Array U32 4#usize} {len : Nat}
    (h : zeroTail hashes len) :
    ∀ hash ∈ hashes.val.drop len, hash = 0#u32 := by
  intro hash member
  rcases List.mem_iff_getElem.mp member with ⟨i, hi, heq⟩
  have hlen : hashes.val.length = 4 := by simp
  have hiArray : len + i < hashes.val.length := by simp only [List.length_drop] at hi; omega
  have zero := h (len + i) (by omega) (by omega)
  rw [Array.getElem!_Nat_eq, _root_.getElem!_pos hashes.val (len + i) hiArray] at zero
  simp only [List.getElem_drop] at heq
  exact heq ▸ zero

theorem mask_idempotent (hash : U32) :
    PackingProofs.masked (PackingProofs.masked hash) = PackingProofs.masked hash := by
  apply (UScalar.eq_equiv_bv_eq _ _).mpr
  change ((hash.bv &&& 0xffffff#32) &&& 0xffffff#32) = hash.bv &&& 0xffffff#32
  rw [BitVec.and_assoc, BitVec.and_self]

theorem array_pack_no_rejection (hashes : Array U32 4#usize) (len : Usize)
    {filter : Filter} {live : List U32} (history : ValidHistory filter live)
    (requiredPrefix : prefixAllowed (fun hash => hash ∈ live.map PackingProofs.masked) hashes len.val)
    (padding : zeroTail hashes len.val) :
    (do
      let packed ← Bloom.pack hashes len
      Bloom.may_match packed.packed_hashes filter) ⦃ found => found = true ⦄ := by
  have hsource := prefix_members requiredPrefix
  have hpadding := padding_members padding
  have fixed : ∀ hash ∈ hashes.val, PackingProofs.masked hash = hash := by
    intro hash member
    rw [← List.take_append_drop len.val hashes.val, List.mem_append] at member
    rcases member with hp | hs
    · rcases List.mem_map.mp (hsource hash hp) with ⟨raw, _, rfl⟩
      exact mask_idempotent raw
    · rw [hpadding hash hs]
      rfl
  have hlen : hashes.val.length = 4 := by simp
  rcases List.length_eq_four.mp hlen with ⟨a, b, c, d, hvalues⟩
  have fa : PackingProofs.masked a = a := fixed a (by simp [hvalues])
  have fb : PackingProofs.masked b = b := fixed b (by simp [hvalues])
  have fc : PackingProofs.masked c = c := fixed c (by simp [hvalues])
  have fd : PackingProofs.masked d = d := fixed d (by simp [hvalues])
  have array_eq : Array.make 4#usize [PackingProofs.masked a, PackingProofs.masked b,
      PackingProofs.masked c, PackingProofs.masked d] = hashes := by
    rw [Array.eq_iff]
    simpa [fa, fb, fc, fd] using hvalues.symm
  have spec := NormalizationProofs.pack_match_raw_history a b c d len
    (NormalizationProofs.history_masked history)
    (by simpa [hvalues] using hsource) (by simpa [hvalues] using hpadding)
  simpa only [array_eq] using spec


#print axioms prefix_members
#print axioms padding_members
#print axioms mask_idempotent
#print axioms array_pack_no_rejection
end CollectionRejectionProofs
