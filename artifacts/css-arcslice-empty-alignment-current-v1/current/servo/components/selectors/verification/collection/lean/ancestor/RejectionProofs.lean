/- This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import Normalized.AncestorFullProofs
import Normalized.PackingBridgeProofs
open Aeneas Aeneas.Std Result
open BloomProofs CollectionInvariantProofs CollectionFrameProofs
set_option maxRecDepth 4096
namespace CollectionRejectionProofs

variable {I A D L N P BN BL C X : Type}
local notation "Inst" => Collection.parser.SelectorImpl I A D L N P BN BL C X
local notation "Selector" => Collection.parser.Selector I A D L N P BN BL C X

theorem ancestor_collection_no_rejection (inst : Inst)
    (quirks : Collection.context.QuirksMode) (depth : Nat) (selector : Selector)
    {filter : Filter} {live : List U32} (history : ValidHistory filter live)
    (good : AncestorContracts.FullGood (fun hash => hash ∈ live.map PackingProofs.masked)
      inst quirks depth selector._0.value.entries 0) :
    (do
      let (hashes, len) ← Collection.parser.collect_ancestors inst selector quirks
      let packed ← Bloom.pack hashes len
      Bloom.may_match packed.packed_hashes filter) ⦃ found => found = true ⦄ := by
  apply WP.spec_bind (AncestorFullProofs.ancestors_required_and_zero
    (fun hash => hash ∈ live.map PackingProofs.masked) inst quirks depth selector good)
  intro result required
  exact array_pack_no_rejection result.1 result.2 history required.2.1 required.2.2

#print axioms ancestor_collection_no_rejection
end CollectionRejectionProofs
