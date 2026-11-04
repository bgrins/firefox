/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import StorageContractProofs
import StorageBackProofs
import RecoverySimulationProofs

open Aeneas Aeneas.Std Result Bloom HashInsertProofs StorageContractProofs RecoverySimulationProofs

namespace StorageProductionProofs

variable {E P : Type}
abbrev Stack := bloom_storage.RecoveryStack E P

theorem projection_inv {A B : Type} (run : Result A) (project : A → B) :
    OnSuccess (do let result ← run; ok (project result))
      (fun result => ∃ value, run = ok value ∧ project value = result) := by
  refine onSuccess_bind_with run _ (fun value => run = ok value) _ (by intro _ h; exact h) ?_
  intro value hrun
  exact onSuccess_ok ⟨value, hrun, rfl⟩

theorem unary_relation (run : Result (Stack (E := E) (P := P) × (Stack (E := E) (P := P) → Stack (E := E) (P := P))))
    (backwards : OnSuccess run (fun result => ∀ future, (result.2 future).storage = future.storage))
    (after : Stack) (success : (do let result ← run; ok result.1) = ok after) :
    ∃ back, run = ok (after, back) ∧ ∀ future, (back future).storage = future.storage := by
  obtain ⟨⟨value, back⟩, hrun, hvalue⟩ := projection_inv run Prod.fst after success
  change value = after at hvalue
  subst value
  exact ⟨back, hrun, backwards _ hrun⟩

theorem option_relation (run : Result (Option E × Stack (E := E) (P := P) × (Stack (E := E) (P := P) → Stack (E := E) (P := P))))
    (backwards : OnSuccess run (fun result => ∀ future, (result.2.2 future).storage = future.storage))
    (element : Option E) (after : Stack)
    (success : (do let result ← run; ok (result.1, result.2.1)) = ok (element, after)) :
    ∃ back, run = ok (element, after, back) ∧ ∀ future, (back future).storage = future.storage := by
  obtain ⟨⟨value, state, back⟩, hrun, hvalue⟩ := projection_inv run
    (fun result => (result.1, result.2.1)) (element, after) success
  have heq : value = element ∧ state = after := Prod.mk.inj hvalue
  rcases heq with ⟨rfl, rfl⟩
  exact ⟨back, hrun, backwards _ hrun⟩

theorem rebuild_contract (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E) :
    RebuildContract (forwardOps (actual dom provider)) (actual dom provider) :=
  { parent_eq := fun _ => rfl,
    pending_push := fun before element after success =>
      unary_relation _ (StorageBackProofs.pending_push_back dom provider before element) after success,
    pending_pop := fun before element after success =>
      option_relation _ (StorageBackProofs.pending_pop_back dom provider before) element after success,
    push := fun before element after success =>
      unary_relation _ (StorageBackProofs.stack_push_back dom provider before element) after success,
    clear := fun before after success =>
      unary_relation _ (StorageBackProofs.stack_clear_back dom provider before) after success }

theorem successful_spec {A : Type} {run : Result A} {post : A → Prop}
    (success : run ⦃ post ⦄) : ∃ value, run = ok value ∧ post value := by
  cases run with
  | ret value => exact ⟨value, rfl, by simpa only [WP.spec_ok] using success⟩
  | vis effect continuation => simp at success
  | div => simp at success

theorem rebuild_ancestors (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (options : StoragePopProofs.OptionModel E)
    (hashes : E → List U32) (providerModel : ProviderModel dom provider model hashes)
    (forest : RecoveryProofs.Forest E)
    (parents : ∀ element, dom.traversal_parent element = ok (forest.parent element))
    (before : Stack) (element : E) (valid : (view model hashes).valid before)
    (pending : (view model hashes).pending before = [])
    (budget : (forest.ancestors element).length ≤ capacity) :
    style_bloom_recovery.rebuild_inst260 (actual dom provider) before element ⦃ result =>
      (view model hashes).valid result.1 ∧ (view model hashes).pending result.1 = [] ∧
      (view model hashes).chain result.1 = forest.ancestors element ∧
      result.2 = (fun future => { before with storage := future.storage }) ⦄ := by
  have generic := RecoveryProofs.rebuild_ancestors (forwardOps (actual dom provider))
    (view model hashes) (contract dom provider model options hashes providerModel)
    forest parents before element valid pending budget
  obtain ⟨after, hrun, hvalid, hpending, hchain⟩ := successful_spec generic
  have specialized := rebuild_simulation (forwardOps (actual dom provider)) (actual dom provider)
    (rebuild_contract dom provider) before element after hrun
  rw [specialized]
  simp only [WP.spec_ok]
  exact ⟨hvalid, hpending, hchain, trivial⟩

theorem valid_hash_lookup (model : StorageInvariantProofs.SequenceModel E)
    (hashes : E → List U32) (storage : bloom_storage.Storage E)
    (valid : StorageInvariantProofs.Valid model hashes storage)
    (element : E) (member : element ∈ StorageInvariantProofs.chain model storage)
    (hash : U32) (hashMember : hash ∈ hashes element) :
    Bloom.contains storage.filter hash ⦃ found => found = true ⦄ := by
  apply StorageHistoryProofs.history_lookup valid.1
  rw [valid.2.1]
  simp only [StorageInvariantProofs.chain, List.mem_reverse, List.mem_map] at member
  obtain ⟨pushed, hpushed, helement⟩ := member
  apply List.mem_flatMap.mpr
  refine ⟨pushed, hpushed, ?_⟩
  simpa only [helement] using hashMember

theorem rebuild_retains_hashes (dom : dom.TElement E) (provider : bloom_storage.HashProvider P E)
    (model : LibraryModel E capacity) (options : StoragePopProofs.OptionModel E)
    (hashes : E → List U32) (providerModel : ProviderModel dom provider model hashes)
    (forest : RecoveryProofs.Forest E)
    (parents : ∀ element, dom.traversal_parent element = ok (forest.parent element))
    (before : Stack) (element : E) (valid : (view model hashes).valid before)
    (pending : (view model hashes).pending before = [])
    (budget : (forest.ancestors element).length ≤ capacity) :
    style_bloom_recovery.rebuild_inst260 (actual dom provider) before element ⦃ result =>
      ∀ ancestor ∈ forest.ancestors element, ∀ hash ∈ hashes ancestor,
        Bloom.contains result.1.storage.filter hash ⦃ found => found = true ⦄ ⦄ := by
  apply WP.spec_mono (rebuild_ancestors dom provider model options hashes providerModel
    forest parents before element valid pending budget)
  rintro result ⟨hvalid, _, hchain, _⟩ ancestor hancestor hash hhash
  apply valid_hash_lookup model.sequence hashes result.1.storage hvalid ancestor _ hash hhash
  change ancestor ∈ (view model hashes).chain result.1
  rw [hchain]
  exact hancestor

#print axioms valid_hash_lookup
#print axioms rebuild_retains_hashes
#print axioms projection_inv
#print axioms unary_relation
#print axioms option_relation
#print axioms rebuild_contract
#print axioms successful_spec
#print axioms rebuild_ancestors

end StorageProductionProofs
