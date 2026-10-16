/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Normalized.MatchingProofs
import Normalized.PackingBridgeProofs
open Aeneas Aeneas.Std Result
open BloomProofs CollectionInvariantProofs CollectionFrameProofs
set_option maxRecDepth 4096
namespace CollectionRejectionProofs

variable {E I A D L N P BN BL C X : Type} [DecidableEq L]
local notation "Inst" => Collection.tree.Element E I A D L N P BN BL C X
local notation "Selector" => Collection.parser.Selector I A D L N P BN BL C X

theorem local_name_no_false_rejection (inst : Inst) (element : E)
    (quirks : Collection.context.QuirksMode) (selector : Selector)
    {filter : Filter} {live : List U32} (history : ValidHistory filter live)
    (contract : MatchingProofs.HashAlignment inst element (fun hash => hash ∈ live.map PackingProofs.masked))
    (matched : CollectionLoopProofs.goodSuffix (MatchingProofs.LocalNameMatch inst element)
      selector._0.value.entries 0) :
    (do
      let (hashes, len) ← Collection.parser.collect_relative_compound inst.parserSelectorImplInst selector quirks
      let packed ← Bloom.pack hashes len
      Bloom.may_match packed.packed_hashes filter) ⦃ found => found = true ⦄ := by
  have required := MatchingProofs.local_name_relative_collection inst element
    (fun hash => hash ∈ live.map PackingProofs.masked) contract quirks selector matched
  have good : CollectionLoopProofs.goodSuffix
      (RecursiveCollectionProofs.Good (fun hash => hash ∈ live.map PackingProofs.masked)
        inst.parserSelectorImplInst quirks 0) selector._0.value.entries 0 := by
    intro i hi hbound hnoCombinator
    exact MatchingProofs.local_name_component_good inst element _ contract quirks _
      (matched i hi hbound hnoCombinator)
  have zero := relative_zero_tail (fun hash => hash ∈ live.map PackingProofs.masked)
    inst.parserSelectorImplInst quirks 0 selector good
  apply WP.spec_bind (WP.spec_and required zero)
  intro result hresult
  exact array_pack_no_rejection result.1 result.2 history hresult.1.2 hresult.2.2

#print axioms local_name_no_false_rejection
end CollectionRejectionProofs
