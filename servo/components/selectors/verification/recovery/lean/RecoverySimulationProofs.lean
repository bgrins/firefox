/- This Source Code Form is subject to the terms of the Mozilla Public
   License, v. 2.0. If a copy of the MPL was not distributed with this
   file, You can obtain one at https://mozilla.org/MPL/2.0/. -/

import HashInsertProofs

open Aeneas Aeneas.Std Result Bloom HashInsertProofs

namespace RecoverySimulationProofs

variable {E P : Type}
abbrev Stack := bloom_storage.RecoveryStack E P
abbrev Filter := bloom.CountingBloomFilter bloom.BloomStorageU8
abbrev Elements := smallvec.SmallVec (Array (bloom_storage.PushedElement E) 16#usize)
  (bloom_storage.PushedElement E)
abbrev Hashes := smallvec.SmallVec (Array U32 64#usize) U32
abbrev Pending := smallvec.SmallVec (Array E 16#usize) E
abbrev Fields := Filter × Elements (E := E) × Hashes × Usize
abbrev Back := Filter → Elements (E := E) → Hashes → Usize → Fields (E := E)
abbrev Frame := E × Back (E := E) × Filter × Elements (E := E) × Hashes × Usize ×
  Pending (E := E) × core.marker.PhantomData P
abbrev Output := Filter × Elements (E := E) × Hashes × Usize × Pending (E := E) ×
  core.marker.PhantomData P × Back (E := E)

def frame (back : Back (E := E)) (element : E) (state : Stack (E := E) (P := P)) :
    Frame (E := E) (P := P) :=
  (element, back, state.storage.filter, state.storage.elements, state.storage.pushed_hashes,
    state.storage.max_pushed_hashes, state.pending, state.provider)

def output (back : Back (E := E)) (state : Stack (E := E) (P := P)) :
    Output (E := E) (P := P) :=
  (state.storage.filter, state.storage.elements, state.storage.pushed_hashes,
    state.storage.max_pushed_hashes, state.pending, state.provider, back)

def control (back : Back (E := E)) :
    ControlFlow (E × Stack (E := E) (P := P)) (Stack (E := E) (P := P)) →
    ControlFlow (Frame (E := E) (P := P)) (Output (E := E) (P := P))
  | .cont (element, state) => .cont (frame back element state)
  | .done state => .done (output back state)

structure CollectContract
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E) where
  parent_eq : ∀ element, specialized.parent element = generic.parent element
  pending_push : ∀ before element after,
    generic.pending_push before element = ok after →
    ∃ back, specialized.pending_push before element = ok (after, back) ∧
      ∀ future, (back future).storage = future.storage

theorem collect_body_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : CollectContract generic specialized)
    (element : E) (state : Stack) (back : Back (E := E)) :
    OnSuccess (style_bloom_recovery.rebuild_loop0.body generic element state)
      (fun result => style_bloom_recovery.rebuild_inst260_loop0.body specialized element back
        state.storage.filter state.storage.elements state.storage.pushed_hashes
        state.storage.max_pushed_hashes state.pending state.provider = ok (control back result)) := by
  unfold style_bloom_recovery.rebuild_loop0.body
  refine onSuccess_bind_with _ _ (fun parent => generic.parent element = ok parent) _
    (by intro _ h; exact h) ?_
  intro parent hparent
  have hsparent := (laws.parent_eq element).trans hparent
  cases parent with
  | none =>
    apply onSuccess_ok
    simp only [style_bloom_recovery.rebuild_inst260_loop0.body, hsparent, bind_ok, control, output]
  | some parent =>
    refine onSuccess_bind_with _ _ (fun after => generic.pending_push state parent = ok after) _
      (by intro _ h; exact h) ?_
    intro after hpush
    obtain ⟨pushBack, hspecialized, hstorage⟩ := laws.pending_push state parent after hpush
    apply onSuccess_ok
    simp only [style_bloom_recovery.rebuild_inst260_loop0.body, hsparent, bind_ok,
      hspecialized, control, frame]
    dsimp! only
    simp only [hstorage]

inductive LoopTrace {A B : Type} (body : A → Result (ControlFlow A B)) : A → B → Prop where
  | done {before after} : body before = ok (.done after) → LoopTrace body before after
  | cont {before middle after} : body before = ok (.cont middle) →
      LoopTrace body middle after → LoopTrace body before after

theorem trace_loop {A B : Type} {body : A → Result (ControlFlow A B)} {before : A} {after : B}
    (trace : LoopTrace body before after) : loop body before = ok after := by
  induction trace with
  | done hbody => rw [loop, hbody, bind_ok]
  | cont hbody _ ih => rw [loop, hbody, bind_ok]; exact ih

unseal Result

theorem onSuccess_admissible {A : Type} (post : A → Prop) :
    Lean.Order.admissible (fun run : Result A => OnSuccess run post) := by
  intro chain hchain h result heq
  exact h (ok result) (Aeneas.Data.Coinductive.ITree.csup_ret_mem hchain heq) result rfl

theorem loop_trace {A B : Type} (body : A → Result (ControlFlow A B)) (before : A) :
    OnSuccess (loop body before) (fun after => LoopTrace body before after) := by
  revert before
  apply loop.fixpoint_induct body
    (motive := fun run => ∀ before, OnSuccess (run before) (fun after => LoopTrace body before after))
  · apply Lean.Order.admissible_pi
    intro before
    exact Lean.Order.admissible_apply (fun _ run => OnSuccess run (fun after => LoopTrace body before after))
      before (onSuccess_admissible _)
  · intro run ih before
    refine onSuccess_bind_with _ _ (fun result => body before = ok result) _
      (by intro _ h; exact h) ?_
    intro result hbody
    cases result with
    | done after => exact onSuccess_ok (.done hbody)
    | cont middle =>
      intro after hafter
      exact .cont hbody (ih middle after hafter)

theorem collect_loop_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : CollectContract generic specialized)
    {before : E × Stack (E := E) (P := P)} {after : Stack (E := E) (P := P)}
    (trace : LoopTrace (fun p => style_bloom_recovery.rebuild_loop0.body generic p.1 p.2)
      before after) (back : Back (E := E)) :
    style_bloom_recovery.rebuild_loop0 generic before.1 before.2 = ok after ∧
    style_bloom_recovery.rebuild_inst260_loop0 specialized before.1 back
      before.2.storage.filter before.2.storage.elements before.2.storage.pushed_hashes
      before.2.storage.max_pushed_hashes before.2.pending before.2.provider =
      ok (output back after) := by
  constructor
  · exact trace_loop trace
  · induction trace with
    | @done before after hbody =>
      have hspecialized := collect_body_simulation generic specialized laws before.1 before.2 back _ hbody
      unfold style_bloom_recovery.rebuild_inst260_loop0
      rw [loop]
      simp only [hspecialized, control, bind_ok]
    | @cont before middle after hbody _ ih =>
      have hspecialized := collect_body_simulation generic specialized laws before.1 before.2 back _ hbody
      unfold style_bloom_recovery.rebuild_inst260_loop0
      rw [loop]
      simp only [hspecialized, control, frame, bind_ok]
      exact ih

theorem collect_success_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : CollectContract generic specialized)
    (element : E) (before after : Stack (E := E) (P := P)) (back : Back (E := E))
    (success : style_bloom_recovery.rebuild_loop0 generic element before = ok after) :
    style_bloom_recovery.rebuild_inst260_loop0 specialized element back
      before.storage.filter before.storage.elements before.storage.pushed_hashes
      before.storage.max_pushed_hashes before.pending before.provider = ok (output back after) := by
  have trace := loop_trace
    (fun p : E × Stack (E := E) (P := P) => style_bloom_recovery.rebuild_loop0.body generic p.1 p.2)
    (element, before) after success
  exact (collect_loop_simulation generic specialized laws trace back).2

abbrev FlushFrame := Back (E := E) × Filter × Elements (E := E) × Hashes × Usize ×
  Pending (E := E) × core.marker.PhantomData P
abbrev FlushOutput := Stack (E := E) (P := P) × (Stack (E := E) (P := P) → Fields (E := E))

def flushFrame (back : Back (E := E)) (state : Stack (E := E) (P := P)) :
    FlushFrame (E := E) (P := P) :=
  (back, state.storage.filter, state.storage.elements, state.storage.pushed_hashes,
    state.storage.max_pushed_hashes, state.pending, state.provider)

def flushOutput (back : Back (E := E)) (state : Stack (E := E) (P := P)) :
    FlushOutput (E := E) (P := P) :=
  (state, fun future => back future.storage.filter future.storage.elements
    future.storage.pushed_hashes future.storage.max_pushed_hashes)

def flushControl (back : Back (E := E)) :
    ControlFlow (Stack (E := E) (P := P)) (Stack (E := E) (P := P)) →
    ControlFlow (FlushFrame (E := E) (P := P)) (FlushOutput (E := E) (P := P))
  | .cont state => .cont (flushFrame back state)
  | .done state => .done (flushOutput back state)

structure FlushContract
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E) where
  pending_pop : ∀ before element after,
    generic.pending_pop before = ok (element, after) →
    ∃ back, specialized.pending_pop before = ok (element, after, back) ∧
      ∀ future, (back future).storage = future.storage
  push : ∀ before element after,
    generic.push before element = ok after →
    ∃ back, specialized.push before element = ok (after, back) ∧
      ∀ future, (back future).storage = future.storage

theorem flush_body_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : FlushContract generic specialized) (state : Stack) (back : Back (E := E)) :
    OnSuccess (style_bloom_recovery.rebuild_loop1.body generic state)
      (fun result => style_bloom_recovery.rebuild_inst260_loop1.body specialized back
        state.storage.filter state.storage.elements state.storage.pushed_hashes
        state.storage.max_pushed_hashes state.pending state.provider = ok (flushControl back result)) := by
  unfold style_bloom_recovery.rebuild_loop1.body
  refine onSuccess_bind_with _ _ (fun result => generic.pending_pop state = ok result) _
    (by intro _ h; exact h) ?_
  rintro ⟨element, popped⟩ hpop
  obtain ⟨popBack, hspecialized, hpopStorage⟩ := laws.pending_pop state element popped hpop
  cases element with
  | none =>
    apply onSuccess_ok
    simp only [style_bloom_recovery.rebuild_inst260_loop1.body, hspecialized, bind_ok]
    dsimp! only
    simp only [hpopStorage, flushOutput]
  | some element =>
    refine onSuccess_bind_with _ _ (fun after => generic.push popped element = ok after) _
      (by intro _ h; exact h) ?_
    intro after hpush
    obtain ⟨pushBack, hspecialPush, hpushStorage⟩ := laws.push popped element after hpush
    apply onSuccess_ok
    simp only [style_bloom_recovery.rebuild_inst260_loop1.body, hspecialized, bind_ok]
    dsimp! only
    rw [hspecialPush, bind_ok]
    dsimp! only
    simp only [hpopStorage, hpushStorage, flushFrame]

theorem flush_loop_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : FlushContract generic specialized)
    {before after : Stack (E := E) (P := P)}
    (trace : LoopTrace (style_bloom_recovery.rebuild_loop1.body generic) before after)
    (back : Back (E := E)) :
    style_bloom_recovery.rebuild_loop1 generic before = ok after ∧
    style_bloom_recovery.rebuild_inst260_loop1 specialized back
      before.storage.filter before.storage.elements before.storage.pushed_hashes
      before.storage.max_pushed_hashes before.pending before.provider =
      ok (flushOutput back after) := by
  constructor
  · exact trace_loop trace
  · induction trace with
    | @done before after hbody =>
      have hspecialized := flush_body_simulation generic specialized laws before back _ hbody
      unfold style_bloom_recovery.rebuild_inst260_loop1
      rw [loop]
      simp only [hspecialized, flushControl, bind_ok]
    | @cont before middle after hbody _ ih =>
      have hspecialized := flush_body_simulation generic specialized laws before back _ hbody
      unfold style_bloom_recovery.rebuild_inst260_loop1
      rw [loop]
      simp only [hspecialized, flushControl, flushFrame, bind_ok]
      exact ih

theorem flush_success_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : FlushContract generic specialized)
    (before after : Stack (E := E) (P := P)) (back : Back (E := E))
    (success : style_bloom_recovery.rebuild_loop1 generic before = ok after) :
    style_bloom_recovery.rebuild_inst260_loop1 specialized back
      before.storage.filter before.storage.elements before.storage.pushed_hashes
      before.storage.max_pushed_hashes before.pending before.provider = ok (flushOutput back after) := by
  have trace := loop_trace (style_bloom_recovery.rebuild_loop1.body generic) before after success
  exact (flush_loop_simulation generic specialized laws trace back).2

structure RebuildContract
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    extends CollectContract generic specialized, FlushContract generic specialized where
  clear : ∀ before after,
    generic.clear before = ok after →
    ∃ back, specialized.clear before = ok (after, back) ∧
      ∀ future, (back future).storage = future.storage

theorem rebuild_simulation
    (generic : style_bloom_recovery.RecoveryState (Stack (E := E) (P := P)) E)
    (specialized : style_bloom_recovery.RecoveryState_inst34 E P E)
    (laws : RebuildContract generic specialized) (before : Stack) (element : E) :
    OnSuccess (style_bloom_recovery.rebuild generic before element)
      (fun after => style_bloom_recovery.rebuild_inst260 specialized before element =
        ok (after, fun future => { before with storage := future.storage })) := by
  unfold style_bloom_recovery.rebuild
  refine onSuccess_bind_with _ _ (fun result => generic.clear before = ok result) _
    (by intro _ h; exact h) ?_
  intro cleared hclear
  obtain ⟨clearBack, hspecialized, hclearStorage⟩ := laws.clear before cleared hclear
  refine onSuccess_bind_with _ _
    (fun result => style_bloom_recovery.rebuild_loop0 generic element cleared = ok result) _
    (by intro _ h; exact h) ?_
  intro collected hcollect
  have hc := collect_success_simulation generic specialized laws.toCollectContract
    element cleared collected (fun f e h n => (f, e, h, n)) hcollect
  intro after hflush
  have hf := flush_success_simulation generic specialized laws.toFlushContract
    collected after (fun f e h n => (f, e, h, n)) hflush
  simp only [style_bloom_recovery.rebuild_inst260, hspecialized, bind_ok]
  dsimp! only
  rw [hc, bind_ok]
  simp only [output]
  dsimp! only
  rw [hf, bind_ok]
  simp only [flushOutput]
  dsimp! only
  simp only [hclearStorage]

#print axioms collect_body_simulation
#print axioms trace_loop
#print axioms onSuccess_admissible
#print axioms loop_trace
#print axioms collect_loop_simulation
#print axioms collect_success_simulation
#print axioms flush_body_simulation
#print axioms flush_loop_simulation
#print axioms flush_success_simulation
#print axioms rebuild_simulation

end RecoverySimulationProofs
