import AtomProvider
namespace TypeObservation
open OrderedTypes TypeMutations
variable {α : Type} [DecidableEq α]

structure Element where
  document : Nat
  isRoot : Bool
  activeState : Bool
  deriving Repr, DecidableEq

structure World (α : Type) where
  active : Nat → Option Nat
  types : Nat → List α

def query (xs names : List α) : Bool := names.any (fun x => decide (x ∈ xs))

def nativeQuery (xs names : List α) (valid : α → Bool) : Bool :=
  names.any (fun x => decide (x ∈ xs) && valid x)

def nativeMatch (world : World α) (element : Element) (names : List α)
    (valid : α → Bool) : Bool :=
  element.activeState && match world.active element.document with
    | none => false
    | some tid => nativeQuery (world.types tid) names valid

def specMatch (world : World α) (element : Element) (names : List α) : Bool :=
  element.isRoot && match world.active element.document with
    | none => false
    | some tid => query (world.types tid) names

theorem nativeQuery_valid (xs names : List α) (valid : α → Bool)
    (hvalid : ∀ x, x ∈ names → valid x = true) : nativeQuery xs names valid = query xs names := by
  induction names with
  | nil => rfl
  | cons x names ih =>
    have hx := hvalid x (by simp)
    have ht := ih (by intro a ha; exact hvalid a (by simp [ha]))
    simpa [nativeQuery, query, hx] using congrArg (fun b => decide (x ∈ xs) || b) ht

theorem nativeQuery_exists (xs names : List α) (valid : α → Bool) :
    nativeQuery xs names valid = true ↔ ∃ x, x ∈ names ∧ x ∈ xs ∧ valid x = true := by
  simp [nativeQuery, List.any_eq_true, Bool.and_eq_true, and_assoc]

theorem query_exists (xs names : List α) :
    query xs names = true ↔ ∃ x, x ∈ names ∧ x ∈ xs := by
  simp [query, List.any_eq_true]

theorem inactive_false (world : World α) (element : Element) (names : List α)
    (valid : α → Bool) (h : world.active element.document = none) :
    nativeMatch world element names valid = false ∧ specMatch world element names = false := by
  simp [nativeMatch, specMatch, h]

theorem flag_false (world : World α) (element : Element) (names : List α)
    (valid : α → Bool) (h : element.activeState = false) :
    nativeMatch world element names valid = false := by
  simp [nativeMatch, h]

theorem root_state_refines (world : World α) (element : Element) (names : List α)
    (valid : α → Bool)
    (state : element.activeState = (element.isRoot && (world.active element.document).isSome))
    (hvalid : ∀ x, x ∈ names → valid x = true) :
    nativeMatch world element names valid = specMatch world element names := by
  cases ha : world.active element.document <;>
    simp [nativeMatch, specMatch, state, ha, nativeQuery_valid _ _ valid hvalid]

theorem owned_transition_observation (s : State α) (world : World α)
    (element : Element) (names : List α) (valid : α → Bool)
    (good : Good s) (owner : element.document = s.document)
    (active : world.active s.document = some s.transition)
    (installed : world.types s.transition = s.native)
    (root : element.isRoot = true) (state : element.activeState = true)
    (hvalid : ∀ x, x ∈ names → valid x = true) :
    nativeMatch world element names valid = query (observed s) names ∧
    specMatch world element names = query (observed s) names := by
  simp [nativeMatch, specMatch, owner, active, installed, root, state,
    nativeQuery_valid _ _ valid hvalid, public_native s good]

theorem successful_history_observation (input : List α) (ops : List (Op α))
    (tid doc : Nat) (world : World α) (element : Element) (names : List α)
    (valid : α → Bool) (owner : element.document = doc)
    (active : world.active doc = some tid)
    (installed : world.types tid = (history (start input tid doc) ops).1.native)
    (root : element.isRoot = true) (state : element.activeState = true)
    (hvalid : ∀ x, x ∈ names → valid x = true) :
    nativeMatch world element names valid =
      query (referenceHistory tid (firsts [] input) ops).1 names := by
  have hg := history_good (start input tid doc) ops (start_good input tid doc)
  have hf := history_frame (start input tid doc) ops
  have ht : (history (start input tid doc) ops).1.transition = tid := hf.1
  have hd : (history (start input tid doc) ops).1.document = doc := hf.2
  have hr := arbitrary_successful_observations input ops tid doc
  have ho := owned_transition_observation (history (start input tid doc) ops).1
    world element names valid hg
    (owner.trans hd.symm)
    (by rw [hd, ht]; exact active)
    (by rw [ht]; exact installed) root state hvalid
  exact ho.1.trans (congrArg (fun xs => query xs names) hr.1)

end TypeObservation
