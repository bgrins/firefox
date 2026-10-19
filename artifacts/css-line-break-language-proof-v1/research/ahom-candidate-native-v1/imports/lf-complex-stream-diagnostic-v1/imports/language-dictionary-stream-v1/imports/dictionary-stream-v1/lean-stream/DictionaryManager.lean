import Std

namespace HyphenDictionaryManager

abbrev Key := List UInt8
abbrev Resource := Nat

structure Handle where
  resource : Resource
  capitalized : Bool
  deriving DecidableEq, Repr

structure State where
  patterns : Key → Option Resource
  aliases : Key → Option Key
  cache : Key → Option Handle
  capitalized : Key → Bool

inductive Event where
  | load (selected : Key) (resource : Resource) (capitalized : Bool)
  | remove (selected : Key)
  deriving DecidableEq, Repr

structure Result where
  state : State
  answer : Option Handle
  events : List Event

inductive Selection where
  | cached (key : Key) (handle : Handle)
  | resource (key : Key) (resource : Resource)
  | missing
  deriving DecidableEq, Repr

def select (state : State) (key : Key) : Selection :=
  match state.cache key with
  | some handle => .cached key handle
  | none => match state.patterns key with
    | some resource => .resource key resource
    | none => match state.aliases key with
      | none => .missing
      | some alias => match state.cache alias with
        | some handle => .cached alias handle
        | none => match state.patterns alias with
          | some resource => .resource alias resource
          | none => .missing

def referenceSelection (state : State) (key : Key) : Selection :=
  if let some handle := state.cache key then .cached key handle
  else
    let selected := if (state.patterns key).isSome then some key else state.aliases key
    match selected with
    | none => .missing
    | some locale => match state.cache locale with
      | some handle => .cached locale handle
      | none => match state.patterns locale with
        | some resource => .resource locale resource
        | none => .missing

theorem selected_exact (state : State) (key : Key) :
    select state key = referenceSelection state key := by
  cases cached : state.cache key with
  | some handle => simp [select,referenceSelection,cached]
  | none =>
    cases pattern : state.patterns key with
    | some resource => simp [select,referenceSelection,cached,pattern]
    | none => simp [select,referenceSelection,cached,pattern]

def replace {Value : Type} (table : Key → Option Value) (key : Key) (value : Option Value) : Key → Option Value :=
  fun queried => if queried = key then value else table queried

def load (valid : Resource → Bool) (state : State) (key : Key) (resource : Resource) : Result :=
  let handle := Handle.mk resource (state.capitalized key)
  let event := Event.load key resource handle.capitalized
  if valid resource then
    ⟨{state with cache := replace state.cache key (some handle)},some handle,[event]⟩
  else
    ⟨{state with patterns := replace state.patterns key none},none,[event,.remove key]⟩

def nativeGet (valid : Resource → Bool) (fallback : Key → Option Key) : Nat → State → Key → Result
  | 0,state,_ => ⟨state,none,[]⟩
  | fuel+1,state,key =>
    match select state key with
    | .cached _ handle => ⟨state,some handle,[]⟩
    | .resource selected resource => load valid state selected resource
    | .missing => match fallback key with
      | none => ⟨state,none,[]⟩
      | some next => nativeGet valid fallback fuel state next

def candidateKeys (fallback : Key → Option Key) : Nat → Key → List Key
  | 0,_ => []
  | fuel+1,key => key :: (match fallback key with
    | none => []
    | some next => candidateKeys fallback fuel next)

def referenceGet (valid : Resource → Bool) : State → List Key → Result
  | state,[] => ⟨state,none,[]⟩
  | state,key::rest =>
    match referenceSelection state key with
    | .cached _ handle => ⟨state,some handle,[]⟩
    | .resource selected resource => load valid state selected resource
    | .missing => referenceGet valid state rest

theorem all_candidates_exact (valid : Resource → Bool) (fallback : Key → Option Key)
    (fuel : Nat) (state : State) (key : Key) :
    nativeGet valid fallback fuel state key = referenceGet valid state (candidateKeys fallback fuel key) := by
  induction fuel generalizing key with
  | zero => rfl
  | succ fuel ih =>
    simp only [nativeGet,candidateKeys,referenceGet,selected_exact]
    split
    · rfl
    · rfl
    · split
      · rfl
      · exact ih _

def SelectionAdmitted (state : State) (requested : Key) : Selection → Prop
  | .cached selected handle => state.cache selected = some handle ∧
      (selected = requested ∨ (state.cache requested = none ∧ state.patterns requested = none ∧
        state.aliases requested = some selected))
  | .resource selected resource => state.patterns selected = some resource ∧ state.cache selected = none ∧
      (selected = requested ∨ (state.cache requested = none ∧ state.patterns requested = none ∧
        state.aliases requested = some selected))
  | .missing => state.cache requested = none ∧ state.patterns requested = none ∧
      (∀ alias, state.aliases requested = some alias → state.cache alias = none ∧ state.patterns alias = none)

theorem selection_admitted (state : State) (requested : Key) : SelectionAdmitted state requested (select state requested) := by
  unfold select
  split
  next handle cached => exact ⟨cached,Or.inl rfl⟩
  next noCache =>
    split
    next resource pattern => exact ⟨pattern,noCache,Or.inl rfl⟩
    next noPattern =>
      split
      next noAlias =>
        exact ⟨noCache,noPattern,by intro alias found;rw [noAlias] at found;cases found⟩
      next alias found =>
        split
        next handle cached => exact ⟨cached,Or.inr ⟨noCache,noPattern,found⟩⟩
        next noAliasCache =>
          split
          next resource pattern => exact ⟨pattern,noAliasCache,Or.inr ⟨noCache,noPattern,found⟩⟩
          next noAliasPattern =>
            refine ⟨noCache,noPattern,?_⟩
            intro other equal
            have same : alias = other := Option.some.inj (found.symm.trans equal)
            subst other
            exact ⟨noAliasCache,noAliasPattern⟩

theorem failed_load_stops (valid : Resource → Bool) (fallback : Key → Option Key)
    (fuel : Nat) (state : State) (requested selected : Key) (resource : Resource)
    (selectedResource : select state requested = .resource selected resource) (invalid : valid resource = false) :
    (nativeGet valid fallback (fuel+1) state requested).answer = none ∧
    (nativeGet valid fallback (fuel+1) state requested).events =
      [.load selected resource (state.capitalized selected),.remove selected] ∧
    (nativeGet valid fallback (fuel+1) state requested).state.patterns selected = none := by
  simp [nativeGet,selectedResource,load,invalid,replace]

theorem loaded_handle_selected_preference (valid : Resource → Bool) (state : State)
    (selected : Key) (resource : Resource) (loaded : valid resource = true) :
    (load valid state selected resource).answer = some ⟨resource,state.capitalized selected⟩ ∧
    (load valid state selected resource).state.cache selected = some ⟨resource,state.capitalized selected⟩ := by
  simp [load,loaded,replace]

def pressure (state : State) : State := {state with cache := fun _ => none}

theorem pressure_clears_only_cache (state : State) :
    (∀ key, (pressure state).cache key = none) ∧
    (pressure state).patterns = state.patterns ∧ (pressure state).aliases = state.aliases ∧
    (pressure state).capitalized = state.capitalized := ⟨fun _ => rfl,rfl,rfl,rfl⟩

def HasProvenance (history : List Event) (handle : Handle) : Prop :=
  ∃ selected, Event.load selected handle.resource handle.capitalized ∈ history

def CacheProvenance (history : List Event) (state : State) : Prop :=
  ∀ key handle, state.cache key = some handle → HasProvenance history handle

theorem provenance_append (history later : List Event) (handle : Handle)
    (known : HasProvenance history handle) : HasProvenance (history++later) handle := by
  obtain ⟨selected,present⟩ := known
  exact ⟨selected,List.mem_append_left later present⟩

theorem load_provenance (valid : Resource → Bool) (state : State) (history : List Event)
    (selected : Key) (resource : Resource) (admitted : CacheProvenance history state) :
    let result := load valid state selected resource
    CacheProvenance (history++result.events) result.state ∧
    (∀ handle, result.answer = some handle → HasProvenance (history++result.events) handle) := by
  unfold load
  split
  · constructor
    · intro key handle found
      dsimp only [replace] at found
      split at found
      · cases found
        exact ⟨selected,by simp⟩
      · exact provenance_append history _ handle (admitted key handle found)
    · intro handle found
      cases found
      exact ⟨selected,by simp⟩
  · exact ⟨fun key handle found => provenance_append history _ handle (admitted key handle found),by simp⟩

theorem get_provenance (valid : Resource → Bool) (fallback : Key → Option Key)
    (fuel : Nat) (state : State) (history : List Event) (requested : Key)
    (admitted : CacheProvenance history state) :
    let result := nativeGet valid fallback fuel state requested
    CacheProvenance (history++result.events) result.state ∧
    (∀ handle, result.answer = some handle → HasProvenance (history++result.events) handle) := by
  induction fuel generalizing requested with
  | zero =>
    refine ⟨by simpa [nativeGet] using admitted,?_⟩
    intro handle found
    cases found
  | succ fuel ih =>
    have selected := selection_admitted state requested
    dsimp only [nativeGet]
    split
    next key handle cached =>
      rw [cached] at selected
      refine ⟨by simpa using admitted,?_⟩
      intro returned found
      cases found
      simpa using admitted key handle selected.1
    next key resource loaded => exact load_provenance valid state history key resource admitted
    · split
      · refine ⟨by simpa using admitted,?_⟩
        intro handle found
        cases found
      · exact ih _

end HyphenDictionaryManager
