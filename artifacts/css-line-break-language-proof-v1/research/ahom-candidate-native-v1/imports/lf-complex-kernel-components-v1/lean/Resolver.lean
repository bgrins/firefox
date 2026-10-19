import Std

namespace LanguageBreak

inductive Script where
  | hans | hant | jpan | hrkt | other
  deriving DecidableEq, Repr

def Script.isCjk : Script → Bool
  | .hans | .hant | .jpan | .hrkt => true
  | .other => false

inductive Tag where
  | absent
  | atom (identity : Nat) (text : String)
  deriving DecidableEq, Repr

inductive Resolution where
  | invalid | providerError | script (value : Script)
  deriving DecidableEq, Repr

def Resolution.answer : Resolution → Bool
  | .script s => s.isCjk
  | _ => false

structure Providers where
  parseAndResolve : String → Resolution

def reference (p : Providers) : Tag → Bool
  | .absent => false
  | .atom _ text => (p.parseAndResolve text).answer

structure Cache where
  retained : Option (Nat × String) := none
  value : Bool := false
  initialized : Bool := false
  deriving DecidableEq, Repr

def Cache.Valid (p : Providers) (c : Cache) : Prop :=
  ∀ id text, c.retained = some (id,text) →
    c.value = (p.parseAndResolve text).answer ∧
    ∃ s, p.parseAndResolve text = .script s

def StableIdentity (c : Cache) (tag : Tag) : Prop :=
  ∀ old text id, c.retained = some (id,old) → tag = .atom id text → old = text

def resolve (p : Providers) (c : Cache) (tag : Tag) : Bool × Cache :=
  match tag with
  | .absent => (false,c)
  | .atom id text =>
    let initialized := { c with initialized := true }
    if c.retained.map Prod.fst = some id then (c.value,initialized)
    else match p.parseAndResolve text with
      | .script script => (script.isCjk,{ retained := some (id,text), value := script.isCjk, initialized := true })
      | _ => (false,initialized)

theorem empty_valid (p : Providers) : ({} : Cache).Valid p := by
  simp [Cache.Valid]

theorem absent_preserves (p : Providers) (c : Cache) :
    resolve p c .absent = (false,c) := rfl

theorem resolve_correct (p : Providers) (c : Cache) (tag : Tag)
    (valid : c.Valid p) (identity : StableIdentity c tag) :
    (resolve p c tag).1 = reference p tag := by
  cases tag with
  | absent => rfl
  | atom id text =>
    simp only [resolve,reference]
    split
    next hit =>
      cases old : c.retained with
      | none => simp [old] at hit
      | some pair =>
        rcases pair with ⟨oldId,oldText⟩
        simp [old] at hit
        subst oldId
        have same := identity oldText text id old rfl
        subst oldText
        exact (valid id text old).1
    next miss =>
      cases h : p.parseAndResolve text <;> simp [Resolution.answer]

theorem resolve_valid (p : Providers) (c : Cache) (tag : Tag)
    (valid : c.Valid p) : (resolve p c tag).2.Valid p := by
  cases tag with
  | absent => exact valid
  | atom id text =>
    simp only [resolve]
    split
    next hit => exact valid
    next miss =>
      cases h : p.parseAndResolve text with
      | invalid => exact valid
      | providerError => exact valid
      | script s =>
        intro id' text' same
        simp only [Option.some.injEq,Prod.mk.injEq] at same
        rcases same with ⟨rfl,rfl⟩
        exact ⟨by simp [h,Resolution.answer],s,h⟩

structure Request where
  owner : Nat
  tag : Tag
  deriving DecidableEq, Repr

def execute (p : Providers) (c : Cache) : List Request → List Bool × Cache
  | [] => ([],c)
  | request :: rest =>
    let step := resolve p c request.tag
    let tail := execute p step.2 rest
    (step.1 :: tail.1,tail.2)

def StableCalls (p : Providers) (c : Cache) : List Request → Prop
  | [] => True
  | request :: rest => StableIdentity c request.tag ∧
      StableCalls p (resolve p c request.tag).2 rest

theorem arbitrary_owner_interleaving (p : Providers) (c : Cache) (requests : List Request)
    (valid : c.Valid p) (stable : StableCalls p c requests) :
    (execute p c requests).1 = requests.map (fun r => reference p r.tag) ∧
    (execute p c requests).2.Valid p := by
  induction requests generalizing c with
  | nil => exact ⟨rfl,valid⟩
  | cons request rest ih =>
    rcases stable with ⟨identity,tailStable⟩
    have nextValid := resolve_valid p c request.tag valid
    have tail := ih (resolve p c request.tag).2 nextValid tailStable
    constructor
    · simp only [execute,List.map]
      rw [resolve_correct p c request.tag valid identity,tail.1]
    · exact tail.2

theorem invalid_does_not_replace (p : Providers) (c : Cache) (id : Nat) (text : String)
    (miss : c.retained.map Prod.fst ≠ some id)
    (invalid : p.parseAndResolve text = .invalid) :
    (resolve p c (.atom id text)).2.retained = c.retained := by
  simp [resolve,miss,invalid]

def shutdown (c : Cache) : Cache := { c with retained := none }

theorem shutdown_valid (p : Providers) (c : Cache) : (shutdown c).Valid p := by
  simp [Cache.Valid,shutdown]

end LanguageBreak
