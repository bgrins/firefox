import Std

namespace Publication

structure Scratch (α β : Type) where
  declarations : List α
  all : Option β
  deriving DecidableEq, Repr

def empty : Scratch α β := ⟨[], none⟩

def clear (_ : Scratch α β) : Scratch α β := empty

def drain (s : Scratch α β) : Scratch α β × Scratch α β := (s, empty)

theorem drain_exact (s : Scratch α β) : (drain s).1 = s := rfl

theorem drain_empties_both (s : Scratch α β) : (drain s).2 = empty := rfl

theorem repeated_drain_empty (s : Scratch α β) : (drain (drain s).2).1 = empty := rfl

def append (s t : Scratch α β) : Scratch α β :=
  ⟨s.declarations ++ t.declarations, t.all.or s.all⟩

def canonical (key : α → κ) (s : Scratch α β) : Prop :=
  (s.declarations.map key).Nodup ∧ (s.all ≠ none → s.declarations = [])

inductive Attempt (α β : Type) where
  | wide (value : Scratch α β)
  | success (observed : Bool) (value : Scratch α β)
  | failure
  deriving DecidableEq, Repr

structure Action (α β : Type) where
  ordinary : Attempt α β
  fallback : Option (Scratch α β)
  deriving DecidableEq, Repr

structure Outcome (α β : Type) where
  accepted : Bool
  scratch : Scratch α β
  deriving DecidableEq, Repr

def fallbackStep (scratch : Scratch α β) (fallback : Option (Scratch α β)) : Outcome α β :=
  match fallback with
  | none => ⟨false, scratch⟩
  | some replacement => ⟨true, append scratch replacement⟩

def repaired (a : Action α β) : Outcome α β :=
  match a.ordinary with
  | .wide s => ⟨true, s⟩
  | .success false s => ⟨true, s⟩
  | .success true s => fallbackStep (clear s) a.fallback
  | .failure => fallbackStep empty a.fallback

def legacy (a : Action α β) : Outcome α β :=
  match a.ordinary with
  | .wide s => ⟨true, s⟩
  | .success false s => ⟨true, s⟩
  | .success true s => fallbackStep s a.fallback
  | .failure => fallbackStep empty a.fallback

def chosen (a : Action α β) : Option (Scratch α β) :=
  match a.ordinary with
  | .wide s | .success false s => some s
  | .success true _ | .failure => a.fallback

def direct (a : Action α β) : Outcome α β :=
  match chosen a with
  | none => ⟨false, empty⟩
  | some s => ⟨true, s⟩

theorem clear_fields (s : Scratch α β) :
    (clear s).declarations = [] ∧ (clear s).all = none := by
  simp [clear, empty]

theorem append_empty (s : Scratch α β) : append empty s = s := by
  cases s with
  | mk ds all => cases all <;> simp [append, empty, Option.or]

theorem refinement (a : Action α β) : repaired a = direct a := by
  rcases a with ⟨o, f⟩
  cases o with
  | wide s => rfl
  | failure => cases f <;> simp [repaired, direct, chosen, fallbackStep, append_empty]
  | success b s =>
    cases b <;> cases f <;>
      simp [repaired, direct, chosen, fallbackStep, clear, append_empty]

theorem ordinary_preserved (s : Scratch α β) (f) :
    repaired ⟨.success false s, f⟩ = ⟨true, s⟩ := rfl

theorem wide_preserved (s : Scratch α β) (f) :
    repaired ⟨.wide s, f⟩ = ⟨true, s⟩ := rfl

theorem observed_replaced (s t : Scratch α β) :
    repaired ⟨.success true s, some t⟩ = ⟨true, t⟩ := by
  simp [repaired, fallbackStep, clear, append_empty]

theorem failed_fallback_clears_abandoned (s : Scratch α β) :
    repaired ⟨.success true s, none⟩ = ⟨false, empty⟩ := rfl

theorem failed_ordinary_can_fallback (t : Scratch α β) :
    repaired ⟨.failure, some t⟩ = ⟨true, t⟩ := by
  simp [repaired, fallbackStep, append_empty]

theorem all_field_abandoned (ds : List α) (old : β) :
    (repaired ⟨.success true ⟨ds, some old⟩, none⟩).scratch.all = none := rfl

def publication (o : Outcome α β) : Option (Scratch α β) :=
  if o.accepted then some o.scratch else none

theorem publication_exact (a : Action α β) :
    publication (repaired a) = chosen a := by
  rw [refinement]
  unfold direct
  cases chosen a <;> simp [publication]

theorem failure_unpublished (a : Action α β) (h : (repaired a).accepted = false) :
    publication (repaired a) = none := by
  simp [publication, h]

def admitted (key : α → κ) (a : Action α β) : Prop :=
  ∀ s, chosen a = some s → canonical key s

theorem canonical_publication (key : α → κ) (a : Action α β) (h : admitted key a)
    (s : Scratch α β) (hs : publication (repaired a) = some s) : canonical key s := by
  apply h s
  simpa [publication_exact] using hs

theorem ordered_declarations_exact (a : Action α β) (s : Scratch α β)
    (h : chosen a = some s) : (repaired a).scratch.declarations = s.declarations := by
  rw [refinement]
  simp [direct, h]

theorem all_exact (a : Action α β) (s : Scratch α β)
    (h : chosen a = some s) : (repaired a).scratch.all = s.all := by
  rw [refinement]
  simp [direct, h]

def nativeTrace (actions : List (Action α β)) : List (Option (Scratch α β)) :=
  actions.map (fun a => publication (repaired a))

def directTrace (actions : List (Action α β)) : List (Option (Scratch α β)) :=
  actions.map chosen

theorem arbitrary_trace_refinement (actions : List (Action α β)) :
    nativeTrace actions = directTrace actions := by
  simp [nativeTrace, directTrace, publication_exact]

def acceptedHistory (actions : List (Action α β)) : List (Scratch α β) :=
  (nativeTrace actions).filterMap id

theorem arbitrary_history_refinement (actions : List (Action α β)) :
    acceptedHistory actions = actions.filterMap chosen := by
  simp [acceptedHistory, arbitrary_trace_refinement, directTrace, List.filterMap_map]

theorem every_publication_canonical (key : α → κ) (actions : List (Action α β))
    (h : ∀ a ∈ actions, admitted key a) :
    ∀ s ∈ acceptedHistory actions, canonical key s := by
  rw [arbitrary_history_refinement]
  intro s hs
  obtain ⟨a, ha, hex⟩ := List.mem_filterMap.mp hs
  exact h a ha s hex

def commit (previous : Scratch α β) (value : Option (Scratch α β)) : Scratch α β :=
  value.getD previous

def runNative (initial : Scratch α β) (actions : List (Action α β)) : Scratch α β :=
  actions.foldl (fun state a => commit state (publication (repaired a))) initial

def runDirect (initial : Scratch α β) (actions : List (Action α β)) : Scratch α β :=
  actions.foldl (fun state a => commit state (chosen a)) initial

theorem arbitrary_transaction_sequence (initial : Scratch α β) (actions) :
    runNative initial actions = runDirect initial actions := by
  simp [runNative, runDirect, publication_exact]

theorem failed_action_preserves_prior (previous : Scratch α β) (a : Action α β)
    (h : chosen a = none) : commit previous (publication (repaired a)) = previous := by
  simp [publication_exact, h, commit]

theorem every_prefix_refinement (initial : Scratch α β) (actions : List (Action α β)) (n : Nat) :
    runNative initial (actions.take n) = runDirect initial (actions.take n) :=
  arbitrary_transaction_sequence initial (actions.take n)

def one (n : Nat) : Scratch Nat Nat := ⟨[n], none⟩

theorem omission_witness :
    (legacy ⟨.success true (one 7), some (one 7)⟩).scratch.declarations = [7, 7] ∧
    (repaired ⟨.success true (one 7), some (one 7)⟩).scratch.declarations = [7] := by
  decide

theorem legacy_not_canonical :
    ¬ canonical id (legacy ⟨.success true (one 7), some (one 7)⟩).scratch := by
  simp [canonical, legacy, fallbackStep, append, one]

def clearDeclarationsOnly (s : Scratch α β) : Scratch α β := ⟨[], s.all⟩

theorem all_clear_mutant_witness :
    fallbackStep (clearDeclarationsOnly (⟨[], some 9⟩ : Scratch Nat Nat)) none ≠
      repaired ⟨.success true ⟨[], some 9⟩, none⟩ := by
  decide

theorem clear_fast_path_mutant_witness :
    (⟨true, clear (one 7)⟩ : Outcome Nat Nat) ≠
      repaired ⟨.success false (one 7), none⟩ := by
  decide

theorem clear_after_publication_mutant_witness :
    (⟨true, clear (one 7)⟩ : Outcome Nat Nat) ≠
      repaired ⟨.success true (one 9), some (one 7)⟩ := by
  decide

theorem nonvacuous_admission :
    admitted id (⟨.success true (one 9), some (one 7)⟩ : Action Nat Nat) := by
  intro s h
  simp [chosen] at h
  subst s
  simp [canonical, one]

end Publication
