/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import HashInsertProofs

open Aeneas Aeneas.Std Result Bloom BloomProofs StyleBloomProofs StorageHistoryProofs
open HashInsertProofs

namespace StoragePopProofs

structure PopModel where
  hashes : HashVec → List U32
  pop_hash : ∀ before rest hash, hashes before = rest ++ [hash] →
    smallvec.SmallVec.pop (ArrayT64.Insts.SmallvecArray U32) before
      ⦃ result => result.1 = some hash ∧ hashes result.2 = rest ⦄
  pop_expected : ∀ (before : alloc.vec.Vec U32) rest hash, before.val = rest ++ [hash] →
    alloc.vec.Vec.pop Global before ⦃ result => result.1 = some hash ∧ result.2.val = rest ⦄

theorem spec_with_eq {A : Type} {run : Result A} {post : A → Prop}
    (correct : run ⦃ post ⦄) : run ⦃ result => run = ok result ∧ post result ⦄ := by
  cases run with
  | ret value => simpa using correct
  | vis effect continuation => simp at correct
  | div => simp at correct

theorem remove_history {filter : Filter} {live : List U32} {hash : U32} {high : Nat}
    (history : HighWaterHistory filter (live ++ [hash]) high) :
    Bloom.remove filter hash ⦃ next => HighWaterHistory next live high ⦄ := by
  have hvalid : ∀ j, contributions hash j ≤ liveCounts (live ++ [hash]) j := by
    intro j
    simp [liveCounts_append, liveCounts]
  have hr := spec_with_eq (remove_represents filter (liveCounts (live ++ [hash])) hash
    (history_represents history) hvalid)
  apply WP.spec_mono hr
  intro next hnext
  simpa only [List.append_nil] using HighWaterHistory.remove history hnext.1

theorem pop_loop_history (model : PopModel) (filter : Filter) (hashes : HashVec)
    (expected : alloc.vec.Vec U32) (remaining : Usize) (livePrefix : List U32) (high : Nat)
    (history : HighWaterHistory filter (model.hashes hashes) high)
    (hh : model.hashes hashes = livePrefix ++ expected.val)
    (hc : remaining.val = expected.val.length) :
    bloom_storage.Storage.pop_loop filter hashes expected remaining ⦃ result =>
      HighWaterHistory result.1 (model.hashes result.2) high ∧ model.hashes result.2 = livePrefix ⦄ := by
  unfold bloom_storage.Storage.pop_loop
  refine loop.spec_decr_nat
    (fun (state : Filter × HashVec × alloc.vec.Vec U32 × Usize) => state.2.2.2.val)
    (fun state => HighWaterHistory state.1 (model.hashes state.2.1) high ∧
      model.hashes state.2.1 = livePrefix ++ state.2.2.1.val ∧
      state.2.2.2.val = state.2.2.1.val.length)
    (fun result => HighWaterHistory result.1 (model.hashes result.2) high ∧
      model.hashes result.2 = livePrefix)
    (fun (f, h, e, r) => bloom_storage.Storage.pop_loop.body f h e r)
    (filter, hashes, expected, remaining) ?_ ⟨history, hh, hc⟩
  rintro ⟨filter, hashes, expected, remaining⟩ ⟨history, hh, hc⟩
  dsimp only at history hh hc ⊢
  unfold bloom_storage.Storage.pop_loop.body
  split
  · rename_i hnonzero
    have hpos : 0 < remaining.val := by scalar_tac
    have hne : expected.val ≠ [] := by intro he; simp only [he, List.length_nil] at hc; omega
    let rest := expected.val.dropLast
    let hash := expected.val.getLast hne
    have hexpected : expected.val = rest ++ [hash] :=
      (List.dropLast_concat_getLast hne).symm
    have hhashes : model.hashes hashes = (livePrefix ++ rest) ++ [hash] := by
      rw [hh, hexpected, List.append_assoc]
    step as ⟨nextRemaining, hremaining⟩
    step with model.pop_hash hashes (livePrefix ++ rest) hash hhashes as ⟨someHash, nextHashes, hSome, hHashes⟩
    subst someHash
    simp only [core.option.Option.unwrap, ofOption, bind_ok]
    step with model.pop_expected expected rest hash hexpected as ⟨someExpected, nextExpected, hSome, hExpected⟩
    subst someExpected
    simp only [bind_ok]
    step
    have hhistory : HighWaterHistory filter ((livePrefix ++ rest) ++ [hash]) high := by
      simpa only [hhashes] using history
    have hremove := remove_history hhistory
    unfold Bloom.remove at hremove
    step with hremove as ⟨nextFilter, hFilter⟩
    refine ⟨?_, ?_, ?_, ?_⟩
    · simpa only [hHashes] using hFilter
    · rw [hHashes, hExpected]
    · rw [hExpected]
      have hlen := congrArg List.length hexpected
      simp only [List.length_append, List.length_singleton] at hlen
      dsimp only [rest] at *
      omega
    · omega
  · rename_i hzero
    have hrem : remaining.val = 0 := by scalar_tac
    have hempty : expected.val = [] := by simpa using hc.symm.trans hrem
    simp only [WP.spec_ok]
    exact ⟨history, by simpa only [hempty, List.append_nil] using hh⟩

abbrev ElementVec (E : Type) :=
  smallvec.SmallVec (Array (bloom_storage.PushedElement E) 16#usize) (bloom_storage.PushedElement E)

structure ElementPopModel (E : Type) where
  elements : ElementVec E → List (bloom_storage.PushedElement E)
  pop_some : ∀ before rest element, elements before = rest ++ [element] →
    smallvec.SmallVec.pop (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E)) before
      ⦃ result => result.1 = some element ∧ elements result.2 = rest ⦄
  pop_none : ∀ before, elements before = [] →
    smallvec.SmallVec.pop (ArrayT16.Insts.SmallvecArray (bloom_storage.PushedElement E)) before
      ⦃ result => result.1 = none ∧ elements result.2 = [] ⦄

structure OptionModel (E : Type) where
  branch_some : ∀ element : bloom_storage.PushedElement E,
    core.option.Option.Insts.CoreOpsTry_traitTry.branch (some element) =
      ok (core.ops.control_flow.ControlFlow.Continue element)
  branch_none : core.option.Option.Insts.CoreOpsTry_traitTry.branch
    (none : Option (bloom_storage.PushedElement E)) =
      ok (core.ops.control_flow.ControlFlow.Break none)
  residual_none : core.option.Option.Insts.CoreOpsTry_traitFromResidualOptionNever.from_residual
    E none = ok none

theorem pop_some_history {E P : Type} (elementOps : dom.TElement E)
    (provider : bloom_storage.HashProvider P E) (model : PopModel)
    (elementModel : ElementPopModel E) (optionModel : OptionModel E)
    (before : bloom_storage.Storage E) (rest : List (bloom_storage.PushedElement E))
    (pushed : bloom_storage.PushedElement E) (livePrefix elementHashes : List U32)
    (helements : elementModel.elements before.elements = rest ++ [pushed])
    (hhashes : model.hashes before.pushed_hashes = livePrefix ++ elementHashes)
    (hcount : pushed.num_hashes.val = elementHashes.length)
    (history : HighWaterHistory before.filter (model.hashes before.pushed_hashes)
      before.max_pushed_hashes.val)
    (expectedSpec : provider.expected pushed.element ⦃ expected => expected.val = elementHashes ⦄) :
    bloom_storage.Storage.pop elementOps provider before ⦃ result =>
      result.1 = some pushed.element ∧
      HighWaterHistory result.2.1.filter (model.hashes result.2.1.pushed_hashes)
        result.2.1.max_pushed_hashes.val ∧
      model.hashes result.2.1.pushed_hashes = livePrefix ∧
      elementModel.elements result.2.1.elements = rest ∧
      result.2.1.max_pushed_hashes = before.max_pushed_hashes ∧ result.2.2 = id ⦄ := by
  unfold bloom_storage.Storage.pop
  step with elementModel.pop_some before.elements rest pushed helements as ⟨popped, elements, hpopped, helements⟩
  subst popped
  simp only [optionModel.branch_some, bind_ok, dom.SendElement.Insts.CoreOpsDerefDeref.deref]
  step with expectedSpec as ⟨expected, hexpected⟩
  have hh : model.hashes before.pushed_hashes = livePrefix ++ expected.val := by
    rw [hexpected]; exact hhashes
  have hc : pushed.num_hashes.val = expected.val.length := by
    rw [hexpected]; exact hcount
  step with pop_loop_history model before.filter before.pushed_hashes expected pushed.num_hashes
    livePrefix before.max_pushed_hashes.val history hh hc as ⟨filter, hashes, hhistory, hhashes⟩
  exact ⟨hhistory, hhashes, helements, rfl⟩

theorem pop_none_history {E P : Type} (elementOps : dom.TElement E)
    (provider : bloom_storage.HashProvider P E) (model : PopModel)
    (elementModel : ElementPopModel E) (optionModel : OptionModel E)
    (before : bloom_storage.Storage E)
    (helements : elementModel.elements before.elements = [])
    (history : HighWaterHistory before.filter (model.hashes before.pushed_hashes)
      before.max_pushed_hashes.val) :
    bloom_storage.Storage.pop elementOps provider before ⦃ result =>
      result.1 = none ∧ result.2.1.filter = before.filter ∧
      result.2.1.pushed_hashes = before.pushed_hashes ∧
      HighWaterHistory result.2.1.filter (model.hashes result.2.1.pushed_hashes)
        result.2.1.max_pushed_hashes.val ∧
      elementModel.elements result.2.1.elements = [] ∧
      result.2.1.max_pushed_hashes = before.max_pushed_hashes ∧ result.2.2 = id ⦄ := by
  unfold bloom_storage.Storage.pop
  step with elementModel.pop_none before.elements helements as ⟨popped, elements, hpopped, helements⟩
  subst popped
  simp only [optionModel.branch_none, optionModel.residual_none, bind_ok, WP.spec_ok]
  exact ⟨trivial, trivial, trivial, history, helements, trivial, rfl⟩

#print axioms remove_history
#print axioms pop_loop_history
#print axioms pop_some_history
#print axioms pop_none_history

end StoragePopProofs
