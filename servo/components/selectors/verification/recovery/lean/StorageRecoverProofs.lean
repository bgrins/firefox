/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import StorageProductionProofs
import RecoverSimulationProofs

open Aeneas Aeneas.Std Result Bloom HashInsertProofs StorageContractProofs StorageProductionProofs

namespace StorageRecoverProofs

variable {E P : Type}
abbrev Stack := bloom_storage.RecoveryStack E P

theorem recover_contract (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E) :
    RecoverSimulationProofs.Contract (forwardOps (actual dom provider)) (actual dom provider) :=
  { toRebuildContract := rebuild_contract dom provider,
    len_eq := fun _ => rfl, current_parent_eq := fun _ => rfl,
    eq_eq := fun _ _ => rfl, ne_eq := fun _ _ => rfl,
    pop := fun before element after success =>
      option_relation _ (StorageBackProofs.stack_pop_back dom provider before) element after success }

theorem recover_ancestors [DecidableEq E]
    (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (options : StoragePopProofs.OptionModel E)
    (hashes : E → List U32) (providerModel : ProviderModel dom provider model hashes)
    (forest : RecoveryProofs.Forest E)
    (parents : ∀ element, dom.traversal_parent element = ok (forest.parent element))
    (equal : ∀ a b, dom.corecmpEqInst.partialEqInst.eq a b = ok (decide (a = b)))
    (unequal : ∀ a b, dom.corecmpEqInst.partialEqInst.ne a b = ok (decide (a ≠ b)))
    (before : Stack) (element : E) (depth : Usize) (separate : Bool)
    (valid : (view model hashes).valid before)
    (chain : RecoveryProofs.Chain forest ((view model hashes).chain before))
    (pending : (view model hashes).pending before = [])
    (depthExact : depth.val = (forest.ancestors element).length)
    (budget : (forest.ancestors element).length ≤ capacity)
    (roots : separate = true ∨ (view model hashes).chain before = [] ∨
      forest.parent element = none ∨
      ((view model hashes).chain before).getLast? = (forest.ancestors element).getLast?) :
    style_bloom_recovery.recover_inst259 (actual dom provider) before element depth separate ⦃ result =>
      (view model hashes).valid result.1 ∧ (view model hashes).pending result.1 = [] ∧
      (view model hashes).chain result.1 = forest.ancestors element ∧
      result.2 = (fun future => { before with storage := future.storage }) ⦄ := by
  have generic := RecoveryProofs.recover_ancestors (forwardOps (actual dom provider))
    (view model hashes) (contract dom provider model options hashes providerModel)
    forest parents equal unequal before element depth separate valid chain pending depthExact budget roots
  obtain ⟨after, hrun, hvalid, hpending, hchain⟩ := successful_spec generic
  have specialized := RecoverSimulationProofs.recover_simulation (forwardOps (actual dom provider))
    (actual dom provider) (recover_contract dom provider) before element depth separate after hrun
  rw [specialized]
  simp only [WP.spec_ok]
  exact ⟨hvalid, hpending, hchain, trivial⟩

theorem recover_retains_hashes [DecidableEq E]
    (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (options : StoragePopProofs.OptionModel E)
    (hashes : E → List U32) (providerModel : ProviderModel dom provider model hashes)
    (forest : RecoveryProofs.Forest E)
    (parents : ∀ element, dom.traversal_parent element = ok (forest.parent element))
    (equal : ∀ a b, dom.corecmpEqInst.partialEqInst.eq a b = ok (decide (a = b)))
    (unequal : ∀ a b, dom.corecmpEqInst.partialEqInst.ne a b = ok (decide (a ≠ b)))
    (before : Stack) (element : E) (depth : Usize) (separate : Bool)
    (valid : (view model hashes).valid before)
    (chain : RecoveryProofs.Chain forest ((view model hashes).chain before))
    (pending : (view model hashes).pending before = [])
    (depthExact : depth.val = (forest.ancestors element).length)
    (budget : (forest.ancestors element).length ≤ capacity)
    (roots : separate = true ∨ (view model hashes).chain before = [] ∨
      forest.parent element = none ∨
      ((view model hashes).chain before).getLast? = (forest.ancestors element).getLast?) :
    style_bloom_recovery.recover_inst259 (actual dom provider) before element depth separate ⦃ result =>
      ∀ ancestor ∈ forest.ancestors element, ∀ hash ∈ hashes ancestor,
        Bloom.contains result.1.storage.filter hash ⦃ found => found = true ⦄ ⦄ := by
  apply WP.spec_mono (recover_ancestors dom provider model options hashes providerModel forest
    parents equal unequal before element depth separate valid chain pending depthExact budget roots)
  rintro result ⟨hvalid, _, hchain, _⟩ ancestor hancestor hash hhash
  apply valid_hash_lookup model.sequence hashes result.1.storage hvalid ancestor _ hash hhash
  change ancestor ∈ (view model hashes).chain result.1
  rw [hchain]
  exact hancestor

#print axioms recover_contract
#print axioms recover_ancestors
#print axioms recover_retains_hashes

end StorageRecoverProofs
