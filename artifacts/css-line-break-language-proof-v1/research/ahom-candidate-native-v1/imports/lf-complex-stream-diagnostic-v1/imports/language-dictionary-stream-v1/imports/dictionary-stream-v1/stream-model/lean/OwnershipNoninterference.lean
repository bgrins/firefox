import CapturedOwnership

namespace LanguageBreak

def PendingEquivalent (a b : StreamState) : Prop :=
  a.policy = b.policy ∧ a.capturedLimits = b.capturedLimits ∧ a.ownedPieces = b.ownedPieces

theorem current_limit_noninterference (state : StreamState) (limits : AuxLimits) :
    PendingEquivalent {state with limits := limits} state := ⟨rfl,rfl,rfl⟩

theorem pending_flush_noninterference (providers : StreamProviders) (a b : StreamState)
    (same : PendingEquivalent a b) :
    (flushStream providers a).events = (flushStream providers b).events ∧
    (flushStream providers a).state.policy = (flushStream providers b).state.policy := by
  simp [flushStream,same.1,same.2.1]

theorem delimiter_whitespace_flush_noninterference (providers : StreamProviders)
    (state : StreamState) (limits : AuxLimits) (inside : Bool) :
    (whitespaceStream providers {state with limits := limits} inside).events =
      (whitespaceStream providers state inside).events ∧
    (whitespaceStream providers {state with limits := limits} inside).state.policy =
      (whitespaceStream providers state inside).state.policy := ⟨rfl,rfl⟩

theorem reset_flush_noninterference (providers : StreamProviders)
    (state : StreamState) (limits : AuxLimits) :
    (resetStream providers {state with limits := limits}).1.events =
      (resetStream providers state).1.events ∧
    (resetStream providers {state with limits := limits}).1.state.policy =
      (resetStream providers state).1.state.policy ∧
    (resetStream providers {state with limits := limits}).2 =
      (resetStream providers state).2 := ⟨rfl,rfl,rfl⟩

theorem empty_append_identity (providers : StreamProviders) (chunk : Chunk) (state : StreamState)
    (empty : chunk.storage.decode = []) :
    appendStream providers chunk state = ⟨state,[]⟩ := by
  cases stored : chunk.storage with
  | utf16 units => simp [appendStream,appendCore,stored,StoredUnits.decode] at empty ⊢; simp_all
  | bytes units =>
    have nil : units = [] := by simpa [stored,StoredUnits.decode] using empty
    subst units
    simp [appendStream,appendCore,stored,StoredUnits.decode,Chunk.widen,StoredUnits.widen]

inductive NoContribution : Operation → Prop where
  | limits (value : AuxLimits) : NoContribution (.limits value)
  | empty (chunk : Chunk) (units : chunk.storage.decode = []) : NoContribution (.append chunk)

theorem no_contribution_preserves_pending (providers : StreamProviders) (state : StreamState)
    (op : Operation) (admitted : NoContribution op) :
    PendingEquivalent (stepStream providers state op).state state ∧
    (stepStream providers state op).events = [] := by
  cases admitted with
  | limits value => exact ⟨⟨rfl,rfl,rfl⟩,rfl⟩
  | empty chunk units => simp [stepStream,empty_append_identity providers chunk state units,PendingEquivalent]

theorem finite_noncontributors_preserve_pending (providers : StreamProviders) (ops : List Operation)
    (input : StreamResult) (admitted : ∀ op ∈ ops, NoContribution op) :
    PendingEquivalent (runStream providers input ops).state input.state ∧
    (runStream providers input ops).events = input.events := by
  induction ops generalizing input with
  | nil => exact ⟨⟨rfl,rfl,rfl⟩,rfl⟩
  | cons op rest ih =>
    have step := no_contribution_preserves_pending providers input.state op (admitted op (by simp))
    have tail := ih ⟨(stepStream providers input.state op).state,input.events++(stepStream providers input.state op).events⟩
      (by intro x hx; exact admitted x (by simp [hx]))
    exact ⟨⟨tail.1.1.trans step.1.1,tail.1.2.1.trans step.1.2.1,tail.1.2.2.trans step.1.2.2⟩,
      by simpa [runStream,step.2] using tail.2⟩

theorem finite_noncontributors_cannot_change_flush (providers : StreamProviders) (ops : List Operation)
    (input : StreamResult) (admitted : ∀ op ∈ ops, NoContribution op) :
    (flushStream providers (runStream providers input ops).state).events =
      (flushStream providers input.state).events :=
  (pending_flush_noninterference providers _ _
    (finite_noncontributors_preserve_pending providers ops input admitted).1).1

end LanguageBreak
