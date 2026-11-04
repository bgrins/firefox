/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import CoverageProofs
import CacheProofs
import RelativeGenerated.StyloRelativeVerification

open Aeneas Aeneas.Std Result

namespace RelativeBridgeProofs

abbrev RelativeFilter := Relative.bloom.CountingBloomFilter Relative.bloom.BloomStorageU8

def toBloom (filter : RelativeFilter) : BloomProofs.Filter :=
  ⟨⟨filter.storage.counters⟩⟩

theorem contains_eq (filter : RelativeFilter) (hash : U32) :
    Relative.contains filter hash = Bloom.contains (toBloom filter) hash := by
  with_unfolding_all rfl

theorem bind_if {α β : Type} (p : Prop) [Decidable p]
    (yes no : Result α) (f : α → Result β) :
    Aeneas.Std.bind (if p then yes else no) f =
      if p then Aeneas.Std.bind yes f else Aeneas.Std.bind no f := by
  split <;> rfl

theorem insert_eq (filter : RelativeFilter) (hash : U32) :
    (do let next ← Relative.insert filter hash; ok (toBloom next)) = Bloom.insert (toBloom filter) hash := by
  simp only [Relative.insert, Relative.bloom.CountingBloomFilter.insert_hash,
    Bloom.insert, Bloom.bloom.CountingBloomFilter.insert_hash,
    Relative.bloom.BloomStorageU8.Insts.Stylo_relative_verificationBloomBloomStorage.adjust_slot,
    Bloom.bloom.BloomStorageU8.Insts.Stylo_bloom_verificationBloomBloomStorage.adjust_slot,
    toBloom, Aeneas.Std.bind_assoc, bind_ok, ite_true]
  dsimp! only
  simp only [bind_if, Aeneas.Std.bind_assoc, bind_ok]
  with_unfolding_all rfl

def Present (filter : RelativeFilter) (hash : U32) : Prop :=
  CoverageProofs.Present (toBloom filter) hash

theorem present_lookup (filter : RelativeFilter) (hash : U32) (h : Present filter hash) :
    Relative.contains filter hash ⦃ found => found = true ⦄ := by
  rw [contains_eq]
  exact CoverageProofs.present_lookup _ _ h

inductive Insertions : RelativeFilter → List U32 → RelativeFilter → Prop where
  | nil (filter : RelativeFilter) : Insertions filter [] filter
  | cons {before after final hash rest} :
      Relative.insert before hash = ok after → Insertions after rest final →
      Insertions before (hash :: rest) final

theorem insertions_to_bloom {before final : RelativeFilter} {hashes : List U32}
    (steps : Insertions before hashes final) :
    CoverageProofs.Insertions (toBloom before) hashes (toBloom final) := by
  induction steps with
  | nil filter => exact CoverageProofs.Insertions.nil _
  | @cons before after final hash rest hrun _ ih =>
    have h := insert_eq before hash
    rw [hrun] at h
    simp only [bind_ok] at h
    exact CoverageProofs.Insertions.cons h.symm ih

theorem insertions_coverage {before final : RelativeFilter} {hashes : List U32}
    (steps : Insertions before hashes final) :
    (∀ hash, Present before hash → Present final hash) ∧
    (∀ hash ∈ hashes, Present final hash) :=
  CoverageProofs.insertions_coverage (insertions_to_bloom steps)

def InRegion {size : Nat} (forest : RelativeProofs.PreorderForest size)
    (root : Fin size) (kind : RelativeProofs.Kind) (element : Fin size) : Prop :=
  match kind with
  | .Children => forest.parent element = some root
  | .Descendants => RelativeProofs.Descendant forest root element

def Provider {E : Type} (ops : Relative.tree.Element E) (hashes : E → List U32) : Prop :=
  ∀ element filter, ops.add_element_unique_hashes element filter ⦃ result =>
    result.1 = true → Insertions filter (hashes element) result.2 ⦄

theorem build_coverage {size : Nat} (forest : RelativeProofs.PreorderForest size)
    (ops : Relative.tree.Element (Fin size)) (nav : RelativeProofs.Navigation forest ops)
    (hashes : Fin size → List U32) (provider : Provider ops hashes)
    (root : Fin size) (kind : RelativeProofs.Kind) (initial : RelativeFilter) :
    Relative.relative_filter.add_to_filter ops root initial kind ⦃ result =>
      result.1 = true → ∀ element, InRegion forest root kind element →
        ∀ hash ∈ hashes element, Present result.2 hash ⦄ := by
  let callback := fun element before (result : Bool × RelativeFilter) =>
    result.1 = true → Insertions before (hashes element) result.2
  have hhashes : ∀ element before after, callback element before (true, after) →
      (∀ hash, Present before hash → Present after hash) ∧
      (∀ hash, hash ∈ hashes element → Present after hash) := by
    intro element before after h
    exact insertions_coverage (h rfl)
  cases kind with
  | Children =>
    exact RelativeProofs.children_coverage forest ops nav callback
      (fun element hash => hash ∈ hashes element) Present provider hhashes root initial
  | Descendants =>
    exact RelativeProofs.descendants_coverage forest ops nav callback
      (fun element hash => hash ∈ hashes element) Present provider hhashes root initial

def Covers {size : Nat} (forest : RelativeProofs.PreorderForest size)
    (identity : Fin size → Usize) (hashes : Fin size → List U32)
    (key : CacheProofs.Key) (filter : RelativeFilter) : Prop :=
  ∀ root, identity root = key.1 → ∀ element, InRegion forest root key.2 element →
    ∀ hash ∈ hashes element, Present filter hash

theorem get_filter_no_false_negatives {size : Nat}
    (forest : RelativeProofs.PreorderForest size)
    (ops : Relative.tree.Element (Fin size)) (nav : RelativeProofs.Navigation forest ops)
    (hashes : Fin size → List U32) (provider : Provider ops hashes)
    (root : Fin size) (kind : RelativeProofs.Kind)
    (view : CacheProofs.Map → CacheProofs.View) (contract : CacheProofs.MapContract view)
    (map : Relative.relative_filter.RelativeSelectorFilterMap)
    (epoch : CacheProofs.EpochSound view (Covers forest nav.identity hashes) map.map) :
    Relative.relative_filter.RelativeSelectorFilterMap.get_filter ops map root kind ⦃ result =>
      CacheProofs.EpochSound view (Covers forest nav.identity hashes) result.2.map ∧
      ∀ filter, result.1 = some filter → ∀ element, InRegion forest root kind element →
        ∀ hash ∈ hashes element, Relative.contains filter hash ⦃ found => found = true ⦄ ⦄ := by
  have hbuild : Relative.relative_filter.add_to_filter ops root RelativeProofs.empty kind ⦃ result =>
      result.1 = true → Covers forest nav.identity hashes (nav.identity root, kind) result.2 ⦄ := by
    apply WP.spec_mono (build_coverage forest ops nav hashes provider root kind RelativeProofs.empty)
    intro result hcoverage hsuccess other hidentity element hregion hash hmem
    have heq : other = root := nav.identity_injective hidentity
    subst other
    exact hcoverage hsuccess element hregion hash hmem
  apply WP.spec_mono (CacheProofs.get_filter_preserves_epoch ops root (nav.identity root)
    (nav.opaque_eq root) kind view contract (Covers forest nav.identity hashes) hbuild map epoch)
  intro result hresult
  refine ⟨hresult.1, ?_⟩
  intro filter hreturned element hregion hash hmem
  exact present_lookup filter hash (hresult.2 filter hreturned root rfl element hregion hash hmem)

end RelativeBridgeProofs

#print axioms RelativeBridgeProofs.contains_eq
#print axioms RelativeBridgeProofs.insert_eq
#print axioms RelativeBridgeProofs.bind_if
#print axioms RelativeBridgeProofs.present_lookup
#print axioms RelativeBridgeProofs.insertions_to_bloom
#print axioms RelativeBridgeProofs.insertions_coverage
#print axioms RelativeBridgeProofs.build_coverage
#print axioms RelativeBridgeProofs.get_filter_no_false_negatives
