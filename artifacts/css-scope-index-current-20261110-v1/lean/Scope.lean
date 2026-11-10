import Std

namespace ScopeCache

structure Sheet where
  content : Nat
  active : Bool
  root : Nat
  shadowHost : Bool
  deriving DecidableEq, Repr

structure Compiled where
  index : Nat
  content : Nat
  dispatchHostContext : Bool
  deriving DecidableEq, Repr

structure Meaning where
  content : Nat
  root : Nat
  receiverShadowHost : Bool
  dispatchHostContext : Bool
  deriving DecidableEq, Repr

def lookup : Nat → List Sheet → Option Sheet
  | _, [] => none
  | 0, s :: _ => some s
  | n + 1, _ :: ss => lookup n ss

def contentKey (sheets : List Sheet) : List Nat :=
  sheets.filterMap fun s => if s.active then some s.content else none

def compileFrom : Nat → List Sheet → List Compiled
  | _, [] => []
  | i, s :: ss =>
    let tail := compileFrom (i + 1) ss
    if s.active then ⟨i, s.content, s.shadowHost⟩ :: tail else tail

def compile (sheets : List Sheet) := compileFrom 0 sheets

def interpretOne (receiver : List Sheet) (c : Compiled) : Option Meaning :=
  (lookup c.index receiver).map fun s =>
    ⟨c.content, s.root, s.shadowHost, c.dispatchHostContext⟩

def interpret (receiver : List Sheet) (compiled : List Compiled) :=
  compiled.map (interpretOne receiver)

def reference (sheets : List Sheet) : List (Option Meaning) :=
  sheets.filterMap fun s =>
    if s.active then some (some ⟨s.content, s.root, s.shadowHost, s.shadowHost⟩)
    else none

theorem lookup_prefix (pre sheets : List Sheet) (i : Nat) :
    lookup (pre.length + i) (pre ++ sheets) = lookup i sheets := by
  induction pre with
  | nil => simp [lookup]
  | cons s ps ih => simpa [lookup, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using ih

theorem fresh_suffix (sheets pre : List Sheet) :
    interpret (pre ++ sheets) (compileFrom pre.length sheets) = reference sheets := by
  induction sheets generalizing pre with
  | nil => simp [compileFrom, interpret, reference]
  | cons s ss ih =>
    have tail := ih (pre ++ [s])
    have eq : (pre ++ [s]) ++ ss = pre ++ s :: ss := by simp
    simp only [eq, List.length_append, List.length_singleton] at tail
    have first : lookup pre.length (pre ++ s :: ss) = some s := by
      simpa [lookup] using lookup_prefix pre (s :: ss) 0
    cases h : s.active <;>
      simp [compileFrom, h, interpret, reference, interpretOne, first] at tail ⊢ <;>
      exact tail

theorem fresh_compilation (sheets : List Sheet) :
    interpret sheets (compile sheets) = reference sheets := by
  simpa [compile] using fresh_suffix sheets []

def contextKeyFrom : Nat → List Sheet → List (Nat × Nat × Bool)
  | _, [] => []
  | i, s :: ss =>
    if s.active then (i, s.content, s.shadowHost) :: contextKeyFrom (i + 1) ss
    else contextKeyFrom (i + 1) ss

def contextKey (sheets : List Sheet) := contextKeyFrom 0 sheets

def decodeKey (key : List (Nat × Nat × Bool)) : List Compiled :=
  key.map fun (i, c, b) => ⟨i, c, b⟩

theorem compile_key (sheets : List Sheet) (i : Nat) :
    compileFrom i sheets = decodeKey (contextKeyFrom i sheets) := by
  induction sheets generalizing i with
  | nil => rfl
  | cons s ss ih => cases h : s.active <;> simp [compileFrom, contextKeyFrom, decodeKey, h, ih]

theorem equal_context_key (donor receiver : List Sheet)
    (h : contextKey donor = contextKey receiver) :
    compile donor = compile receiver := by
  simpa [compile, compile_key, contextKey] using congrArg decodeKey h

theorem reuse_sound (donor receiver : List Sheet)
    (h : contextKey donor = contextKey receiver) :
    interpret receiver (compile donor) = reference receiver := by
  rw [equal_context_key donor receiver h, fresh_compilation]

theorem receiver_kind_recomputed (receiver : List Sheet) (c : Compiled) (s : Sheet)
    (h : lookup c.index receiver = some s) :
    (interpretOne receiver c).map Meaning.receiverShadowHost = some s.shadowHost := by
  simp [interpretOne, h]

theorem cached_dispatch_context_retained (receiver : List Sheet) (c : Compiled) (s : Sheet)
    (h : lookup c.index receiver = some s) :
    (interpretOne receiver c).map Meaning.dispatchHostContext = some c.dispatchHostContext := by
  simp [interpretOne, h]

def activeNormal : Sheet := ⟨7, true, 10, false⟩
def inactivePrefix : Sheet := ⟨99, false, 20, false⟩
def shiftedActive : Sheet := ⟨7, true, 30, false⟩
def donor := [activeNormal]
def shifted := [inactivePrefix, shiftedActive]
def hostReceiver := [Sheet.mk 7 true 40 true]
def otherRoot := [Sheet.mk 7 true 50 false]

theorem inactive_prefix_same_key : contentKey donor = contentKey shifted := by decide +kernel

theorem inactive_prefix_wrong_root :
    interpret shifted (compile donor) = [some ⟨7, 20, false, false⟩] := by decide +kernel

theorem inactive_prefix_reference :
    reference shifted = [some ⟨7, 30, false, false⟩] := by decide +kernel

theorem inactive_prefix_mismatch :
    interpret shifted (compile donor) ≠ reference shifted := by decide +kernel

theorem same_index_same_content : contentKey donor = contentKey hostReceiver := by decide +kernel

theorem same_index_receiver_kind_fresh :
    interpret hostReceiver (compile donor) = [some ⟨7, 40, true, false⟩] := by decide +kernel

theorem same_index_dispatch_context_mismatch :
    interpret hostReceiver (compile donor) ≠ reference hostReceiver := by decide +kernel

theorem stronger_key_separates_index : contextKey donor ≠ contextKey shifted := by decide +kernel

theorem stronger_key_separates_kind : contextKey donor ≠ contextKey hostReceiver := by decide +kernel

theorem root_identity_not_required :
    contextKey donor = contextKey otherRoot ∧
    interpret otherRoot (compile donor) = reference otherRoot := by decide +kernel

inductive Bucket where
  | normal | featureless | both
  deriving DecidableEq, Repr

structure Dispatched where
  content : Nat
  root : Nat
  receiverShadowHost : Bool
  bucket : Bucket
  deriving DecidableEq, Repr

def dispatchMeaning (dispatch : Nat → Bool → Bucket) (m : Meaning) : Dispatched :=
  ⟨m.content, m.root, m.receiverShadowHost, dispatch m.content m.dispatchHostContext⟩

def dispatchAll (dispatch : Nat → Bool → Bucket) (meanings : List (Option Meaning)) :=
  meanings.map (Option.map (dispatchMeaning dispatch))

theorem reuse_dispatch_sound (dispatch : Nat → Bool → Bucket) (donor receiver : List Sheet)
    (h : contextKey donor = contextKey receiver) :
    dispatchAll dispatch (interpret receiver (compile donor)) =
      dispatchAll dispatch (reference receiver) := by rw [reuse_sound donor receiver h]

def scopeDispatch (_ : Nat) (host : Bool) : Bucket :=
  if host then .featureless else .normal

theorem same_index_dispatch_witness :
    dispatchAll scopeDispatch (interpret hostReceiver (compile donor)) ≠
      dispatchAll scopeDispatch (reference hostReceiver) := by decide +kernel

theorem positional_key_alone_aliases_kind :
    (contextKey donor).map (fun (i, c, _) => (i, c)) =
    (contextKey hostReceiver).map (fun (i, c, _) => (i, c)) := by decide +kernel

theorem missing_receiver_is_none : interpret [] (compile donor) = [none] := by decide +kernel

end ScopeCache
