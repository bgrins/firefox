/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import RecoverySimulationProofs

open Aeneas Aeneas.Std Result Bloom HashInsertProofs RecoverySimulationProofs

namespace RecoverSimulationProofs

variable {E P : Type}

structure Contract
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    extends RebuildContract generic specialized where
  len_eq : ∀ state, specialized.len state = generic.len state
  current_parent_eq : ∀ state, specialized.current_parent state = generic.current_parent state
  eq_eq : ∀ a b, specialized.corecmpEqInst.partialEqInst.eq a b = generic.corecmpEqInst.partialEqInst.eq a b
  ne_eq : ∀ a b, specialized.corecmpEqInst.partialEqInst.ne a b = generic.corecmpEqInst.partialEqInst.ne a b
  pop : ∀ before element after,
    generic.pop before = ok (element, after) →
    ∃ back, specialized.pop before = ok (element, after, back) ∧
      ∀ future, (back future).storage = future.storage

theorem loop_transport {A B C D : Type} (generic : A → Result (ControlFlow A B))
    (specialized : C → Result (ControlFlow C D)) (encode : A → C) (finish : B → D)
    (body : ∀ before, OnSuccess (generic before) (fun result => specialized (encode before) =
      ok (match result with | .cont next => .cont (encode next) | .done last => .done (finish last))))
    (before : A) (after : B) (success : loop generic before = ok after) :
    loop specialized (encode before) = ok (finish after) := by
  have trace := loop_trace generic before after success
  clear success
  induction trace with
  | @done before after hbody =>
    rw [loop, body before _ hbody, bind_ok]
  | @cont before middle after hbody _ ih =>
    rw [loop, body before _ hbody, bind_ok]
    exact ih

def stackBack (back : Back (E := E)) (state : Stack (E := E) (P := P)) : Fields (E := E) :=
  back state.storage.filter state.storage.elements state.storage.pushed_hashes state.storage.max_pushed_hashes

abbrev TrimOutput := Filter × Elements (E := E) × Hashes × Usize × Pending (E := E) ×
  core.marker.PhantomData P × Usize × Back (E := E)

def trimOutput (back : Back (E := E)) (result : Stack (E := E) (P := P) × Usize) :
    TrimOutput (E := E) (P := P) :=
  (result.1.storage.filter, result.1.storage.elements, result.1.storage.pushed_hashes,
    result.1.storage.max_pushed_hashes, result.1.pending, result.1.provider, result.2, back)

theorem trim_body_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : Contract generic specialized) (depth : Usize) (state : Stack) (current : Usize)
    (back : Back (E := E)) :
    OnSuccess (style_bloom_recovery.recover_loop0.body generic depth state current)
      (fun result => style_bloom_recovery.recover_inst259_loop0.body specialized depth
        (stackBack back) state current = ok (match result with
          | .cont next => .cont (stackBack back, next.1, next.2)
          | .done result => .done (trimOutput back result))) := by
  unfold style_bloom_recovery.recover_loop0.body
  refine onSuccess_bind_with _ _ (fun bound => depth - 1#usize = ok bound) _
    (by intro _ h; exact h) ?_
  intro bound hbound
  split
  · rename_i hmore
    refine onSuccess_bind_with _ _ (fun result => generic.pop state = ok result) _
      (by intro _ h; exact h) ?_
    rintro ⟨element, popped⟩ hpop
    obtain ⟨popBack, hspecial, hstorage⟩ := laws.pop state element popped hpop
    refine onSuccess_bind_with _ _ (fun result => massert (core.option.Option.is_some element) = ok result) _
      (by intro _ h; exact h) ?_
    intro assertion hassert
    cases assertion
    refine onSuccess_bind_with _ _ (fun next => current - 1#usize = ok next) _
      (by intro _ h; exact h) ?_
    intro next hnext
    apply onSuccess_ok
    simp only [style_bloom_recovery.recover_inst259_loop0.body, hbound, bind_ok, hmore,
      ↓reduceIte, hspecial]
    dsimp! only
    rw [hassert, bind_ok, hnext, bind_ok]
    simp only [stackBack, hstorage]
    rfl
  · rename_i hdone
    apply onSuccess_ok
    simp only [style_bloom_recovery.recover_inst259_loop0.body, hbound, bind_ok, hdone,
      ↓reduceIte, trimOutput, stackBack]

theorem trim_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : Contract generic specialized) (depth : Usize) (state : Stack) (current : Usize)
    (after : Stack (E := E) (P := P) × Usize) (back : Back (E := E))
    (success : style_bloom_recovery.recover_loop0 generic state depth current = ok after) :
    style_bloom_recovery.recover_inst259_loop0 specialized (stackBack back) state depth current =
      ok (trimOutput back after) := by
  exact loop_transport
    (fun p => style_bloom_recovery.recover_loop0.body generic depth p.1 p.2)
    (fun p => style_bloom_recovery.recover_inst259_loop0.body specialized depth p.1 p.2.1 p.2.2)
    (fun p => (stackBack back, p.1, p.2)) (trimOutput back)
    (fun p result h => by
      have hs := trim_body_simulation generic specialized laws depth p.1 p.2 back result h
      cases result <;> exact hs)
    (state, current) after success

abbrev AscendOutput := Filter × Elements (E := E) × Hashes × Usize × Pending (E := E) ×
  core.marker.PhantomData P × E × Usize × Back (E := E)

def ascendOutput (back : Back (E := E)) (result : Stack (E := E) (P := P) × E × Usize) :
    AscendOutput (E := E) (P := P) :=
  (result.1.storage.filter, result.1.storage.elements, result.1.storage.pushed_hashes,
    result.1.storage.max_pushed_hashes, result.1.pending, result.1.provider, result.2.1, result.2.2, back)

def ascendFrame (back : Back (E := E)) (result : Stack (E := E) (P := P) × E × Usize) :=
  (back, result.1.storage.filter, result.1.storage.elements, result.1.storage.pushed_hashes,
    result.1.storage.max_pushed_hashes, result.1.pending, result.1.provider, result.2.1, result.2.2)

theorem ascend_body_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : Contract generic specialized) (current : Usize) (state : Stack)
    (parent : E) (depth : Usize) (back : Back (E := E)) :
    OnSuccess (style_bloom_recovery.recover_loop1.body generic current state parent depth)
      (fun result => style_bloom_recovery.recover_inst259_loop1.body specialized current back
        state.storage.filter state.storage.elements state.storage.pushed_hashes
        state.storage.max_pushed_hashes state.pending state.provider parent depth =
        ok (match result with | .cont next => .cont (ascendFrame back next)
                              | .done last => .done (ascendOutput back last))) := by
  unfold style_bloom_recovery.recover_loop1.body
  split
  · rename_i hmore
    refine onSuccess_bind_with _ _ (fun next => generic.pending_push state parent = ok next) _
      (by intro _ h; exact h) ?_
    intro pushed hpush
    obtain ⟨pushBack, hspecial, hstorage⟩ := laws.pending_push state parent pushed hpush
    refine onSuccess_bind_with _ _ (fun next => generic.parent parent = ok next) _
      (by intro _ h; exact h) ?_
    intro next hparent
    have hspecialParent := (laws.parent_eq parent).trans hparent
    cases next with
    | none =>
      intro result hresult
      have hmatch := congrArg Result.match hresult
      simp only [Result.match.fail, Result.match.ok] at hmatch
      cases hmatch
    | some next =>
      refine onSuccess_bind_with _ _ (fun nextDepth => depth - 1#usize = ok nextDepth) _
        (by intro _ h; exact h) ?_
      intro nextDepth hdepth
      apply onSuccess_ok
      simp only [style_bloom_recovery.recover_inst259_loop1.body, hmore, ↓reduceIte,
        hspecial, bind_ok]
      dsimp! only
      simp only [hspecialParent, bind_ok, hdepth]
      simp only [hstorage, ascendFrame]
  · rename_i hdone
    apply onSuccess_ok
    simp only [style_bloom_recovery.recover_inst259_loop1.body, hdone, ↓reduceIte, ascendOutput]

theorem ascend_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : Contract generic specialized) (current : Usize) (state : Stack)
    (parent : E) (depth : Usize) (after : Stack (E := E) (P := P) × E × Usize)
    (back : Back (E := E))
    (success : style_bloom_recovery.recover_loop1 generic state current parent depth = ok after) :
    style_bloom_recovery.recover_inst259_loop1 specialized back
      state.storage.filter state.storage.elements state.storage.pushed_hashes
      state.storage.max_pushed_hashes state.pending state.provider current parent depth =
      ok (ascendOutput back after) := by
  exact loop_transport
    (fun p => style_bloom_recovery.recover_loop1.body generic current p.1 p.2.1 p.2.2)
    (fun p => style_bloom_recovery.recover_inst259_loop1.body specialized current
      p.1 p.2.1 p.2.2.1 p.2.2.2.1 p.2.2.2.2.1 p.2.2.2.2.2.1 p.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.1 p.2.2.2.2.2.2.2.2)
    (ascendFrame back) (ascendOutput back)
    (fun p result h => by
      have hs := ascend_body_simulation generic specialized laws current p.1 p.2.1 p.2.2 back result h
      cases result <;> exact hs)
    (state, parent, depth) after success

theorem common_body_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : Contract generic specialized) (separate : Bool) (state : Stack)
    (parent : E) (back : Back (E := E)) :
    OnSuccess (style_bloom_recovery.recover_loop2.body generic separate state parent)
      (fun result => style_bloom_recovery.recover_inst259_loop2.body specialized separate
        (stackBack back) state parent = ok (match result with
          | .cont next => .cont (stackBack back, next.1, next.2)
          | .done last => .done (output back last))) := by
  unfold style_bloom_recovery.recover_loop2.body
  refine onSuccess_bind_with _ _ (fun result => generic.current_parent state = ok result) _
    (by intro _ h; exact h) ?_
  intro current hcurrent
  simp only [style_bloom_recovery.recover_inst259_loop2.body, laws.current_parent_eq,
    hcurrent, bind_ok]
  refine onSuccess_bind_with _ _ (fun result => core.option.Option.unwrap current = ok result) _
    (by intro _ h; exact h) ?_
  intro element helement
  simp only [helement, bind_ok]
  refine onSuccess_bind_with _ _
    (fun result => generic.corecmpEqInst.partialEqInst.ne element parent = ok result) _
    (by intro _ h; exact h) ?_
  intro different hdifferent
  simp only [laws.ne_eq, hdifferent, bind_ok]
  cases different with
  | false =>
    apply onSuccess_ok
    simp only [Bool.false_eq_true, ↓reduceIte, output, stackBack]
  | true =>
    simp only [↓reduceIte]
    refine onSuccess_bind_with _ _ (fun result => generic.pending_push state parent = ok result) _
      (by intro _ h; exact h) ?_
    intro pushed hpush
    obtain ⟨pushBack, hspecialPush, hpushStorage⟩ := laws.pending_push state parent pushed hpush
    simp only [hspecialPush, bind_ok]
    dsimp! only
    refine onSuccess_bind_with _ _ (fun result => generic.pop pushed = ok result) _
      (by intro _ h; exact h) ?_
    rintro ⟨popped, after⟩ hpop
    obtain ⟨popBack, hspecialPop, hpopStorage⟩ := laws.pop pushed popped after hpop
    simp only [hspecialPop, bind_ok]
    dsimp! only
    refine onSuccess_bind_with _ _ (fun result => core.option.Option.unwrap popped = ok result) _
      (by intro _ h; exact h) ?_
    intro ignored hignored
    simp only [hignored, bind_ok]
    refine onSuccess_bind_with _ _ (fun result => generic.parent parent = ok result) _
      (by intro _ h; exact h) ?_
    intro next hparent
    simp only [laws.parent_eq, hparent, bind_ok]
    cases next with
    | some next =>
      apply onSuccess_ok
      simp only [stackBack, hpushStorage, hpopStorage]
      rfl
    | none =>
      refine onSuccess_bind_with _ _ (fun result => generic.len after = ok result) _
        (by intro _ h; exact h) ?_
      intro size hsize
      simp only [laws.len_eq, hsize, bind_ok]
      refine onSuccess_bind_with _ _ (fun result => massert (size = 0#usize) = ok result) _
        (by intro _ h; exact h) ?_
      intro assertion hassert
      cases assertion
      simp only [hassert, bind_ok]
      refine onSuccess_bind_with _ _ (fun result => massert separate = ok result) _
        (by intro _ h; exact h) ?_
      intro assertion hseparate
      cases assertion
      apply onSuccess_ok
      simp only [hseparate, bind_ok, stackBack, hpushStorage, hpopStorage, output]

theorem common_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : Contract generic specialized) (separate : Bool) (state : Stack)
    (parent : E) (after : Stack (E := E) (P := P)) (back : Back (E := E))
    (success : style_bloom_recovery.recover_loop2 generic state separate parent = ok after) :
    style_bloom_recovery.recover_inst259_loop2 specialized (stackBack back) state separate parent =
      ok (output back after) := by
  exact loop_transport
    (fun p => style_bloom_recovery.recover_loop2.body generic separate p.1 p.2)
    (fun p => style_bloom_recovery.recover_inst259_loop2.body specialized separate p.1 p.2.1 p.2.2)
    (fun p => (stackBack back, p.1, p.2)) (output back)
    (fun p result h => by
      have hs := common_body_simulation generic specialized laws separate p.1 p.2 back result h
      cases result <;> exact hs)
    (state, parent) after success


theorem recover_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : Contract generic specialized) (before : Stack) (element : E)
    (depth : Usize) (separate : Bool) :
    OnSuccess (style_bloom_recovery.recover generic before element depth separate)
      (fun after => style_bloom_recovery.recover_inst259 specialized before element depth separate =
        ok (after, fun future => { before with storage := future.storage })) := by
  have g4 : style_bloom_recovery.recover_loop4 generic = style_bloom_recovery.recover_loop0 generic := rfl
  have g5 : style_bloom_recovery.recover_loop5 generic = style_bloom_recovery.recover_loop1 generic := rfl
  have g6 : style_bloom_recovery.recover_loop6 generic = style_bloom_recovery.recover_loop2 generic := rfl
  have g3 : style_bloom_recovery.recover_loop3 generic = style_bloom_recovery.rebuild_loop1 generic := rfl
  have g7 : style_bloom_recovery.recover_loop7 generic = style_bloom_recovery.rebuild_loop1 generic := rfl
  have s4 : style_bloom_recovery.recover_inst259_loop4 specialized = style_bloom_recovery.recover_inst259_loop0 specialized := rfl
  have s5 : style_bloom_recovery.recover_inst259_loop5 specialized = style_bloom_recovery.recover_inst259_loop1 specialized := rfl
  have s6 : style_bloom_recovery.recover_inst259_loop6 specialized = style_bloom_recovery.recover_inst259_loop2 specialized := rfl
  have s3 : style_bloom_recovery.recover_inst259_loop3 specialized = style_bloom_recovery.rebuild_inst260_loop1 specialized := rfl
  have s7 : style_bloom_recovery.recover_inst259_loop7 specialized = style_bloom_recovery.rebuild_inst260_loop1 specialized := rfl
  have clearCase : OnSuccess (generic.clear before) (fun after =>
      (do
        let (cleared, back) ← specialized.clear before
        ok (cleared, fun (future : Stack (E := E) (P := P)) => { before with storage := (back { cleared with storage := future.storage }).storage })) =
      ok (after, fun (future : Stack (E := E) (P := P)) => { before with storage := future.storage })) := by
    intro after hclear
    obtain ⟨back, hspecial, hstorage⟩ := laws.clear before after hclear
    rw [hspecial, bind_ok]
    dsimp! only
    simp only [hstorage]
  unfold style_bloom_recovery.recover
  refine onSuccess_bind_with _ _ (fun result => generic.len before = ok result) _
    (by intro _ h; exact h) ?_
  intro size hsize
  simp only [style_bloom_recovery.recover_inst259, laws.len_eq, hsize, bind_ok,
    g4, g5, g6, g3, g7, s4, s5, s6, s3, s7]
  split
  · rename_i hempty
    intro after hrebuilt
    have hspecial := rebuild_simulation generic specialized laws.toRebuildContract before element after hrebuilt
    simp only [hspecial, bind_ok]
    dsimp! only
  · rename_i hnonempty
    refine onSuccess_bind_with _ _ (fun result => generic.parent element = ok result) _
      (by intro _ h; exact h) ?_
    intro parent hparent
    simp only [laws.parent_eq, hparent, bind_ok]
    cases parent with
    | none => exact clearCase
    | some parent =>
      refine onSuccess_bind_with _ _ (fun result => generic.current_parent before = ok result) _
        (by intro _ h; exact h) ?_
      intro current hcurrent
      simp only [laws.current_parent_eq, hcurrent, bind_ok]
      cases current with
      | none =>
        refine onSuccess_bind_with _ _ (fun result => massert ((depth = 0#usize) || (depth != 0#usize)) = ok result) _
          (by intro _ h; exact h) ?_
        intro assertion hassert1
        cases assertion
        simp only [hassert1, bind_ok]
        refine onSuccess_bind_with _ _ (fun result => massert ((depth = 0#usize) || (size != 0#usize)) = ok result) _
          (by intro _ h; exact h) ?_
        intro assertion hassert2
        cases assertion
        simp only [hassert2, bind_ok]
        split
        · rename_i hzero
          exact clearCase
        · rename_i hpositive
          refine onSuccess_bind_with _ _ (fun result => size - 1#usize = ok result) _
            (by intro _ h; exact h) ?_
          intro current hcurrentDepth
          simp only [hcurrentDepth, bind_ok]
          refine onSuccess_bind_with _ _
            (fun result => style_bloom_recovery.recover_loop0 generic before depth current = ok result) _
            (by intro _ h; exact h) ?_
          rintro ⟨trimmed, currentAfter⟩ htrim
          dsimp! only
          have ht := trim_simulation generic specialized laws depth before current
            (trimmed, currentAfter) (fun f e h n => (f, e, h, n)) htrim
          change style_bloom_recovery.recover_inst259_loop0 specialized
            (fun rs => let ⟨⟨f, e, h, n⟩, _, _⟩ := rs; (f, e, h, n)) before depth current = _ at ht
          rw [ht]
          simp only [bind_ok, trimOutput]
          dsimp! only
          refine onSuccess_bind_with _ _ (fun result => depth - 1#usize = ok result) _
            (by intro _ h; exact h) ?_
          intro parentDepth hparentDepth
          simp only [hparentDepth, bind_ok]
          refine onSuccess_bind_with _ _
            (fun result => style_bloom_recovery.recover_loop1 generic trimmed currentAfter parent parentDepth = ok result) _
            (by intro _ h; exact h) ?_
          rintro ⟨ascended, commonParent, commonDepth⟩ hascend
          have ha := ascend_simulation generic specialized laws currentAfter trimmed parent parentDepth
            (ascended, commonParent, commonDepth) (fun f e h n => (f, e, h, n)) hascend
          rw [ha]
          simp only [bind_ok, ascendOutput]
          dsimp! only
          refine onSuccess_bind_with _ _ (fun result => massert (commonDepth = currentAfter) = ok result) _
            (by intro _ h; exact h) ?_
          intro assertion hdepthAssert
          cases assertion
          simp only [hdepthAssert, bind_ok]
          refine onSuccess_bind_with _ _
            (fun result => style_bloom_recovery.recover_loop2 generic ascended separate commonParent = ok result) _
            (by intro _ h; exact h) ?_
          intro common hcommon
          have hc := common_simulation generic specialized laws separate ascended commonParent common
            (fun f e h n => (f, e, h, n)) hcommon
          change style_bloom_recovery.recover_inst259_loop2 specialized
            (fun rs => let ⟨⟨f, e, h, n⟩, _, _⟩ := rs; (f, e, h, n))
            ⟨⟨ascended.storage.filter, ascended.storage.elements, ascended.storage.pushed_hashes, ascended.storage.max_pushed_hashes⟩, ascended.pending, ascended.provider⟩ separate commonParent = _ at hc
          rw [hc]
          simp only [bind_ok, output]
          dsimp! only
          refine onSuccess_bind_with _ _
            (fun result => style_bloom_recovery.rebuild_loop1 generic common = ok result) _
            (by intro _ h; exact h) ?_
          intro flushed hflush
          have hf := flush_success_simulation generic specialized laws.toFlushContract common flushed
            (fun f e h n => (f, e, h, n)) hflush
          rw [hf]
          simp only [bind_ok, flushOutput]
          dsimp! only
          refine onSuccess_bind_with _ _ (fun result => generic.len flushed = ok result) _
            (by intro _ h; exact h) ?_
          intro finalSize hfinalSize
          simp only [hfinalSize, bind_ok]
          refine onSuccess_bind_with _ _ (fun result => massert (finalSize = depth) = ok result) _
            (by intro _ h; exact h) ?_
          intro assertion hfinalAssert
          cases assertion
          apply onSuccess_ok
          simp only [hfinalAssert, bind_ok]

      | some current =>
        refine onSuccess_bind_with _ _
          (fun result => generic.corecmpEqInst.partialEqInst.eq current parent = ok result) _
          (by intro _ h; exact h) ?_
        intro same hsame
        simp only [laws.eq_eq, hsame, bind_ok]
        refine onSuccess_bind_with _ _
          (fun result => massert (same || ((depth = 0#usize) || (depth != 0#usize))) = ok result) _
          (by intro _ h; exact h) ?_
        intro assertion hassert1
        cases assertion
        simp only [hassert1, bind_ok]
        refine onSuccess_bind_with _ _
          (fun result => massert (same || ((depth = 0#usize) || (size != 0#usize))) = ok result) _
          (by intro _ h; exact h) ?_
        intro assertion hassert2
        cases assertion
        simp only [hassert2, bind_ok]
        cases same with
        | true =>
          apply onSuccess_ok
          rfl
        | false =>
          simp only [Bool.false_eq_true, ↓reduceIte]
          split
          · rename_i hzero
            exact clearCase
          · rename_i hpositive
            refine onSuccess_bind_with _ _ (fun result => size - 1#usize = ok result) _
              (by intro _ h; exact h) ?_
            intro current hcurrentDepth
            simp only [hcurrentDepth, bind_ok]
            refine onSuccess_bind_with _ _
              (fun result => style_bloom_recovery.recover_loop0 generic before depth current = ok result) _
              (by intro _ h; exact h) ?_
            rintro ⟨trimmed, currentAfter⟩ htrim
            dsimp! only
            have ht := trim_simulation generic specialized laws depth before current
              (trimmed, currentAfter) (fun f e h n => (f, e, h, n)) htrim
            change style_bloom_recovery.recover_inst259_loop0 specialized
              (fun rs => let ⟨⟨f, e, h, n⟩, _, _⟩ := rs; (f, e, h, n)) before depth current = _ at ht
            rw [ht]
            simp only [bind_ok, trimOutput]
            dsimp! only
            refine onSuccess_bind_with _ _ (fun result => depth - 1#usize = ok result) _
              (by intro _ h; exact h) ?_
            intro parentDepth hparentDepth
            simp only [hparentDepth, bind_ok]
            refine onSuccess_bind_with _ _
              (fun result => style_bloom_recovery.recover_loop1 generic trimmed currentAfter parent parentDepth = ok result) _
              (by intro _ h; exact h) ?_
            rintro ⟨ascended, commonParent, commonDepth⟩ hascend
            have ha := ascend_simulation generic specialized laws currentAfter trimmed parent parentDepth
              (ascended, commonParent, commonDepth) (fun f e h n => (f, e, h, n)) hascend
            rw [ha]
            simp only [bind_ok, ascendOutput]
            dsimp! only
            refine onSuccess_bind_with _ _ (fun result => massert (commonDepth = currentAfter) = ok result) _
              (by intro _ h; exact h) ?_
            intro assertion hdepthAssert
            cases assertion
            simp only [hdepthAssert, bind_ok]
            refine onSuccess_bind_with _ _
              (fun result => style_bloom_recovery.recover_loop2 generic ascended separate commonParent = ok result) _
              (by intro _ h; exact h) ?_
            intro common hcommon
            have hc := common_simulation generic specialized laws separate ascended commonParent common
              (fun f e h n => (f, e, h, n)) hcommon
            change style_bloom_recovery.recover_inst259_loop2 specialized
              (fun rs => let ⟨⟨f, e, h, n⟩, _, _⟩ := rs; (f, e, h, n))
              ⟨⟨ascended.storage.filter, ascended.storage.elements, ascended.storage.pushed_hashes, ascended.storage.max_pushed_hashes⟩, ascended.pending, ascended.provider⟩ separate commonParent = _ at hc
            rw [hc]
            simp only [bind_ok, output]
            dsimp! only
            refine onSuccess_bind_with _ _
              (fun result => style_bloom_recovery.rebuild_loop1 generic common = ok result) _
              (by intro _ h; exact h) ?_
            intro flushed hflush
            have hf := flush_success_simulation generic specialized laws.toFlushContract common flushed
              (fun f e h n => (f, e, h, n)) hflush
            rw [hf]
            simp only [bind_ok, flushOutput]
            dsimp! only
            refine onSuccess_bind_with _ _ (fun result => generic.len flushed = ok result) _
              (by intro _ h; exact h) ?_
            intro finalSize hfinalSize
            simp only [hfinalSize, bind_ok]
            refine onSuccess_bind_with _ _ (fun result => massert (finalSize = depth) = ok result) _
              (by intro _ h; exact h) ?_
            intro assertion hfinalAssert
            cases assertion
            apply onSuccess_ok
            simp only [hfinalAssert, bind_ok]


#print axioms recover_simulation
#print axioms loop_transport
#print axioms trim_body_simulation
#print axioms trim_simulation
#print axioms ascend_body_simulation
#print axioms ascend_simulation
#print axioms common_body_simulation
#print axioms common_simulation

end RecoverSimulationProofs
