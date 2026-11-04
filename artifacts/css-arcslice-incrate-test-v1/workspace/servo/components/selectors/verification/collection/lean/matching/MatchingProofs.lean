/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

module
public import Normalized.RecursiveCollectorProofs
@[expose] public section
open Aeneas Aeneas.Std Result Collection
open CollectionInvariantProofs CollectionLoopProofs RecursiveCollectionProofs
set_option linter.unusedSimpArgs false
namespace MatchingProofs
variable {E I A D L N P BN BL C X : Type} [DecidableEq L]
local notation "Inst" => tree.Element E I A D L N P BN BL C X
local notation "Name" => parser.LocalName I A D L N P BN BL C X
local notation "Component" => parser.Component I A D L N P BN BL C X
local notation "Selector" => parser.Selector I A D L N P BN BL C X

def masked (hash : U32) : U32 := ⟨hash.bv &&& 16777215#32⟩

theorem local_name_requires_hash
    (inst : Inst) (element : E) (localName : Name) (quirks : context.QuirksMode)
    (hashName : L → U32) (borrowName : L → BL) (allowed : U32 → Prop)
    (name_eq : ∀ a b, inst.parserSelectorImplInst.corecmpEqInst2.partialEqInst.eq a b = ok (decide (a = b)))
    (name_ne : ∀ a b, inst.parserSelectorImplInst.corecmpEqInst2.partialEqInst.ne a b = ok (decide (a ≠ b)))
    (name_hash : ∀ a, inst.parserSelectorImplInst.precomputed_hashPrecomputedHashInst1.precomputed_hash a = ok (hashName a))
    (name_borrow : ∀ a, inst.parserSelectorImplInst.coreborrowBorrowInst.borrow a = ok (borrowName a))
    (hash_alignment : ∀ a, inst.has_local_name element (borrowName a) = ok true → allowed (masked (hashName a)))
    (matched : matching.matches_local_name inst element localName = ok true)
    (hash : U32)
    (collected : parser.simple_selector_hash inst.parserSelectorImplInst (.LocalName localName) quirks = ok (some hash)) :
    allowed (masked hash) := by
  by_cases equal : localName.name = localName.lower_name
  · have hash_eq : hash = hashName localName.name := by
      simpa [parser.simple_selector_hash, core.cmp.impls.PartialEqShared.ne,
        name_ne, name_hash, equal] using collected.symm
    subst hash
    apply hash_alignment localName.name
    simpa [matching.matches_local_name, matching.select_name,
      core.cmp.impls.PartialEqShared.eq, name_eq, name_borrow, equal] using matched
  · simp [parser.simple_selector_hash, core.cmp.impls.PartialEqShared.ne,
      name_ne, equal] at collected

structure HashAlignment (inst : Inst) (element : E) (allowed : U32 → Prop) where
  hashName : L → U32
  borrowName : L → BL
  name_eq : ∀ a b, inst.parserSelectorImplInst.corecmpEqInst2.partialEqInst.eq a b = ok (decide (a = b))
  name_ne : ∀ a b, inst.parserSelectorImplInst.corecmpEqInst2.partialEqInst.ne a b = ok (decide (a ≠ b))
  name_hash : ∀ a, inst.parserSelectorImplInst.precomputed_hashPrecomputedHashInst1.precomputed_hash a = ok (hashName a)
  name_borrow : ∀ a, inst.parserSelectorImplInst.coreborrowBorrowInst.borrow a = ok (borrowName a)
  alignment : ∀ a, inst.has_local_name element (borrowName a) = ok true → allowed (masked (hashName a))

def LocalNameMatch (inst : Inst) (element : E) : Component → Prop
  | .LocalName localName => matching.matches_local_name inst element localName = ok true
  | .Combinator _ => True
  | _ => False

theorem local_name_component_good (inst : Inst) (element : E) (allowed : U32 → Prop)
    (contract : HashAlignment inst element allowed) (quirks : context.QuirksMode)
    (component : Component) (matched : LocalNameMatch inst element component) :
    Good allowed inst.parserSelectorImplInst quirks 0 component := by
  cases component <;> simp only [LocalNameMatch] at matched
  case Combinator => simp [Good, CollectionStepProofs.nested, parser.simple_selector_hash]
  case LocalName localName =>
    simp only [Good]
    constructor
    · rfl
    · by_cases equal : localName.name = localName.lower_name
      · have collected : parser.simple_selector_hash inst.parserSelectorImplInst (.LocalName localName) quirks = ok (some (contract.hashName localName.name)) := by
          simp [parser.simple_selector_hash, core.cmp.impls.PartialEqShared.ne, contract.name_ne, contract.name_hash, equal]
        have required := local_name_requires_hash inst element localName quirks contract.hashName contract.borrowName allowed
          contract.name_eq contract.name_ne contract.name_hash contract.name_borrow contract.alignment matched
          (contract.hashName localName.name) collected
        simpa [collected, masked, CollectionInvariantProofs.masked] using required
      · simp [parser.simple_selector_hash, core.cmp.impls.PartialEqShared.ne, contract.name_ne, equal]

theorem local_name_compound_requires_hash (inst : Inst) (element : E) (allowed : U32 → Prop)
    (contract : HashAlignment inst element allowed) (quirks : context.QuirksMode)
    (selector : Selector)
    (matched : goodSuffix (LocalNameMatch inst element) selector._0.value.entries 0)
    (hashes : Array U32 4#usize) (len : Usize) (h : len.val < 4)
    (before : prefixAllowed allowed hashes len.val) :
    (do
      let iter ← parser.Selector.iter selector
      parser.collect_selector_hashes
        (parser.SelectorIter.Insts.SelectorsParserSelectorHashIterator inst.parserSelectorImplInst)
        iter quirks hashes len) ⦃ r =>
      r.2.2.val ≤ 4 ∧ (r.1 = true → r.2.2.val < 4) ∧
      prefixAllowed allowed r.2.1 r.2.2.val ⦄ := by
  apply selector_preserves allowed inst.parserSelectorImplInst quirks 0 selector _ hashes len h before
  intro i hi hbound hnoCombinator
  exact local_name_component_good inst element allowed contract quirks _ (matched i hi hbound hnoCombinator)

theorem local_name_relative_collection (inst : Inst) (element : E) (allowed : U32 → Prop)
    (contract : HashAlignment inst element allowed) (quirks : context.QuirksMode)
    (selector : Selector)
    (matched : goodSuffix (LocalNameMatch inst element) selector._0.value.entries 0) :
    parser.collect_relative_compound inst.parserSelectorImplInst selector quirks ⦃ r =>
      r.2.val ≤ 4 ∧ prefixAllowed allowed r.1 r.2.val ⦄ := by
  have spec := local_name_compound_requires_hash inst element allowed contract quirks selector matched
    (Array.repeat 4#usize 0#u32) 0#usize (by decide) (by simp [prefixAllowed])
  unfold parser.collect_relative_compound
  simp only [CollectionIteratorProofs.selector_iter, bind_ok] at spec ⊢
  step as ⟨cont, hashes, len, hbound, hflag, hall⟩
  simp [hbound, hall]

#print axioms local_name_relative_collection
#print axioms local_name_requires_hash
#print axioms local_name_component_good
#print axioms local_name_compound_requires_hash
end MatchingProofs
