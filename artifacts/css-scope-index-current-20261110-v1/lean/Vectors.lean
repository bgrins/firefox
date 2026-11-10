import Scope

namespace ScopeCache

structure VectorKey where
  contents : List Nat
  positions : List Nat
  hostContexts : List Bool
  deriving DecidableEq, Repr

def collectVectorsFrom : Nat → List Sheet → VectorKey
  | _, [] => ⟨[], [], []⟩
  | i, s :: ss =>
    let tail := collectVectorsFrom (i + 1) ss
    if s.active then
      ⟨s.content :: tail.contents, i :: tail.positions,
        s.shadowHost :: tail.hostContexts⟩
    else tail

def collectVectors (sheets : List Sheet) := collectVectorsFrom 0 sheets

def projectVectors (key : List (Nat × Nat × Bool)) : VectorKey :=
  ⟨key.map (fun (_, c, _) => c), key.map (fun (i, _, _) => i),
    key.map (fun (_, _, b) => b)⟩

def joinVectors (key : VectorKey) : List (Nat × Nat × Bool) :=
  key.positions.zip (key.contents.zip key.hostContexts)

theorem collection_projects_context (sheets : List Sheet) (i : Nat) :
    collectVectorsFrom i sheets = projectVectors (contextKeyFrom i sheets) := by
  induction sheets generalizing i with
  | nil => rfl
  | cons s ss ih =>
    cases h : s.active <;>
      simp [collectVectorsFrom, contextKeyFrom, projectVectors, h, ih]

theorem projected_vectors_rejoin (key : List (Nat × Nat × Bool)) :
    joinVectors (projectVectors key) = key := by
  induction key with
  | nil => rfl
  | cons entry rest ih =>
    rcases entry with ⟨i, c, b⟩
    simp_all [joinVectors, projectVectors]

theorem actual_vectors_rejoin (sheets : List Sheet) :
    joinVectors (collectVectors sheets) = contextKey sheets := by
  simp [collectVectors, collection_projects_context, contextKey,
    projected_vectors_rejoin]

theorem vector_lengths_aligned (sheets : List Sheet) :
    (collectVectors sheets).contents.length =
      (collectVectors sheets).positions.length ∧
    (collectVectors sheets).contents.length =
      (collectVectors sheets).hostContexts.length := by
  simp [collectVectors, collection_projects_context, projectVectors]

theorem vector_equality_context (donor receiver : List Sheet)
    (h : collectVectors donor = collectVectors receiver) :
    contextKey donor = contextKey receiver := by
  simpa only [actual_vectors_rejoin] using congrArg joinVectors h

theorem vector_reuse_sound (donor receiver : List Sheet)
    (h : collectVectors donor = collectVectors receiver) :
    interpret receiver (compile donor) = reference receiver :=
  reuse_sound donor receiver (vector_equality_context donor receiver h)

theorem vector_dispatch_sound (dispatch : Nat → Bool → Bucket)
    (donor receiver : List Sheet)
    (h : collectVectors donor = collectVectors receiver) :
    dispatchAll dispatch (interpret receiver (compile donor)) =
      dispatchAll dispatch (reference receiver) :=
  reuse_dispatch_sound dispatch donor receiver
    (vector_equality_context donor receiver h)

theorem inactive_prefix_changes_only_position :
    (collectVectors donor).contents = (collectVectors shifted).contents ∧
    (collectVectors donor).hostContexts = (collectVectors shifted).hostContexts ∧
    (collectVectors donor).positions ≠ (collectVectors shifted).positions := by
  decide +kernel

theorem host_change_changes_only_context :
    (collectVectors donor).contents = (collectVectors hostReceiver).contents ∧
    (collectVectors donor).positions = (collectVectors hostReceiver).positions ∧
    (collectVectors donor).hostContexts ≠
      (collectVectors hostReceiver).hostContexts := by
  decide +kernel

theorem root_identity_still_shareable :
    collectVectors donor = collectVectors otherRoot := by decide +kernel

theorem trailing_inactive_still_shareable :
    collectVectors donor = collectVectors (donor ++ [inactivePrefix]) := by
  decide +kernel

theorem inactive_contents_ignored :
    collectVectors shifted =
      collectVectors [Sheet.mk 123 false 999 true, shiftedActive] := by
  decide +kernel

end ScopeCache
