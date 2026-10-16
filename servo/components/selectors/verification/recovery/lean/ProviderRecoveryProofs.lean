/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import ProviderModelProofs
import StorageRecoverProofs
open Aeneas Aeneas.Std Result Bloom HashInsertProofs StorageContractProofs ProviderModelProofs
noncomputable section
namespace ProviderRecoveryProofs
variable {E : Type}

theorem rebuild_retains_hashes (dom : dom.TElement E) 
    (model : LibraryModel E capacity) (options : StoragePopProofs.OptionModel E)
    (hashes : E → List U32) (enumeration : Enumeration dom hashes)
    (limit hashCapacity : Nat) (bounded : ∀ node, (hashes node).length ≤ limit)
    (elementFits : limit ≤ Usize.max) (fits : capacity * limit ≤ hashCapacity)
    (allocation : StorageResourceProofs.AllocationModel model.sequence.hashPush hashCapacity)
    (forest : RecoveryProofs.Forest E)
    (parents : ∀ element, dom.traversal_parent element = ok (forest.parent element))
    (before : bloom_storage.RecoveryStack E bloom_hashes.DomHashes) (element : E) (valid : (view model hashes).valid before)
    (pending : (view model hashes).pending before = [])
    (budget : (forest.ancestors element).length ≤ capacity) :
    style_bloom_recovery.rebuild_inst260 (StorageContractProofs.actual dom (ProviderModelProofs.actual dom)) before element ⦃ result =>
      ∀ ancestor ∈ forest.ancestors element, ∀ hash ∈ hashes ancestor,
        Bloom.contains result.1.storage.filter hash ⦃ found => found = true ⦄ ⦄ := by
  exact StorageProductionProofs.rebuild_retains_hashes dom (ProviderModelProofs.actual dom) model options hashes
    (actual_model dom model hashes enumeration limit hashCapacity bounded elementFits fits allocation)
    forest parents before element valid pending budget

theorem recover_retains_hashes [DecidableEq E]
    (dom : dom.TElement E) 
    (model : LibraryModel E capacity) (options : StoragePopProofs.OptionModel E)
    (hashes : E → List U32) (enumeration : Enumeration dom hashes)
    (limit hashCapacity : Nat) (bounded : ∀ node, (hashes node).length ≤ limit)
    (elementFits : limit ≤ Usize.max) (fits : capacity * limit ≤ hashCapacity)
    (allocation : StorageResourceProofs.AllocationModel model.sequence.hashPush hashCapacity)
    (forest : RecoveryProofs.Forest E)
    (parents : ∀ element, dom.traversal_parent element = ok (forest.parent element))
    (equal : ∀ a b, dom.corecmpEqInst.partialEqInst.eq a b = ok (decide (a = b)))
    (unequal : ∀ a b, dom.corecmpEqInst.partialEqInst.ne a b = ok (decide (a ≠ b)))
    (before : bloom_storage.RecoveryStack E bloom_hashes.DomHashes) (element : E) (depth : Usize) (separate : Bool)
    (valid : (view model hashes).valid before)
    (chain : RecoveryProofs.Chain forest ((view model hashes).chain before))
    (pending : (view model hashes).pending before = [])
    (depthExact : depth.val = (forest.ancestors element).length)
    (budget : (forest.ancestors element).length ≤ capacity)
    (roots : separate = true ∨ (view model hashes).chain before = [] ∨
      forest.parent element = none ∨
      ((view model hashes).chain before).getLast? = (forest.ancestors element).getLast?) :
    style_bloom_recovery.recover_inst259 (StorageContractProofs.actual dom (ProviderModelProofs.actual dom)) before element depth separate ⦃ result =>
      ∀ ancestor ∈ forest.ancestors element, ∀ hash ∈ hashes ancestor,
        Bloom.contains result.1.storage.filter hash ⦃ found => found = true ⦄ ⦄ := by
  exact StorageRecoverProofs.recover_retains_hashes dom (ProviderModelProofs.actual dom) model options hashes
    (actual_model dom model hashes enumeration limit hashCapacity bounded elementFits fits allocation)
    forest parents equal unequal before element depth separate valid chain pending depthExact budget roots

#print axioms rebuild_retains_hashes
#print axioms recover_retains_hashes
end ProviderRecoveryProofs
