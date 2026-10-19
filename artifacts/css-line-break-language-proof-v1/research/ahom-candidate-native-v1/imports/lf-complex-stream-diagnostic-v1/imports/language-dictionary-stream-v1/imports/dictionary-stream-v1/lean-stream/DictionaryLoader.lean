import DictionaryResourceIdentity

namespace HyphenDictionaryLoader

open HyphenDictionaryManager

inductive Kind where
  | rawSpan | parentHandle | childMapping | mappedFile
  deriving DecidableEq, Repr

structure Stored where
  origin : Resource
  kind : Kind
  deriving DecidableEq, Repr

structure Inputs where
  parent : Bool
  precompiled : Bool
  jar : Bool
  file : Bool
  jarItem : Option Resource
  rawValid : Resource → Bool
  compileJar : Resource → Option Resource
  loadChannel : Bool → Option Resource
  loadFile : Bool → Option Resource
  requestParent : Option Resource

def store (kind : Kind) (resource : Option Resource) : Option Stored :=
  resource.map fun origin => ⟨origin,kind⟩

def fileBranch (input : Inputs) : Option Stored :=
  if input.file then
    store (if input.precompiled then .mappedFile else .parentHandle)
      (input.loadFile input.precompiled)
  else none

def jarBranch (input : Inputs) : Option Stored :=
  if input.jar then
    match input.jarItem with
    | some source =>
      if input.precompiled then
        if input.rawValid source then some ⟨source,.rawSpan⟩ else none
      else store .parentHandle (input.compileJar source)
    | none =>
      if input.parent then store .parentHandle (input.loadChannel input.precompiled)
      else store .childMapping input.requestParent
  else none

def construct (input : Inputs) : Option Stored :=
  if !input.precompiled && !input.parent then store .childMapping input.requestParent
  else
    match jarBranch input with
    | some result => some result
    | none => fileBranch input

def jarAttempts (input : Inputs) : List (Option Stored) :=
  if !input.jar then [] else
    match input.jarItem with
    | some source =>
      if input.precompiled then
        [if input.rawValid source then some ⟨source,.rawSpan⟩ else none]
      else [store .parentHandle (input.compileJar source)]
    | none =>
      [if input.parent then store .parentHandle (input.loadChannel input.precompiled)
       else store .childMapping input.requestParent]

def fileAttempts (input : Inputs) : List (Option Stored) :=
  if input.file then
    [store (if input.precompiled then .mappedFile else .parentHandle)
      (input.loadFile input.precompiled)] else []

def attempts (input : Inputs) : List (Option Stored) :=
  if !input.precompiled && !input.parent then [store .childMapping input.requestParent]
  else jarAttempts input ++ fileAttempts input

def firstAvailable : List (Option Stored) → Option Stored
  | [] => none
  | some value :: _ => some value
  | none :: rest => firstAvailable rest

@[simp] theorem singleton_available (value : Option Stored) :
    firstAvailable [value] = value := by cases value <;> rfl

theorem append_available (first rest : List (Option Stored)) :
    firstAvailable (first ++ rest) =
      match firstAvailable first with
      | some value => some value
      | none => firstAvailable rest := by
  induction first with
  | nil => rfl
  | cons head tail ih => cases head <;> simp_all [firstAvailable]

theorem jar_dispatch_exact (input : Inputs) :
    firstAvailable (jarAttempts input) = jarBranch input := by
  cases jar : input.jar
  · simp [jarAttempts,jarBranch,jar,firstAvailable]
  · cases item : input.jarItem with
    | none =>
      cases parent : input.parent <;> simp [jarAttempts,jarBranch,jar,item,parent]
    | some source =>
      cases precompiled : input.precompiled <;> simp [jarAttempts,jarBranch,jar,item,precompiled]

theorem file_dispatch_exact (input : Inputs) :
    firstAvailable (fileAttempts input) = fileBranch input := by
  cases file : input.file <;> simp [fileAttempts,fileBranch,file,firstAvailable]

theorem complete_dispatch_exact (input : Inputs) :
    construct input = firstAvailable (attempts input) := by
  unfold construct attempts
  split
  · exact (singleton_available _).symm
  · rw [append_available,jar_dispatch_exact,file_dispatch_exact]

def IsOrigin (requested : Resource) (stored : Option Stored) : Prop :=
  ∀ value, stored = some value → value.origin = requested

def ResourceOrigin (requested : Resource) (result : Option Resource) : Prop :=
  ∀ value, result = some value → value = requested

structure Admission (requested : Resource) (input : Inputs) : Prop where
  jar : ResourceOrigin requested input.jarItem
  compile : ∀ source, input.jarItem = some source →
    ResourceOrigin requested (input.compileJar source)
  channel : ResourceOrigin requested (input.loadChannel input.precompiled)
  file : ResourceOrigin requested (input.loadFile input.precompiled)
  parent : ResourceOrigin requested input.requestParent

theorem store_origin (kind : Kind) (result : Option Resource) (requested : Resource)
    (admitted : ResourceOrigin requested result) : IsOrigin requested (store kind result) := by
  intro value found
  cases result with
  | none => cases found
  | some origin => cases found;exact admitted origin rfl

theorem jar_preserves_origin (requested : Resource) (input : Inputs)
    (admitted : Admission requested input) : IsOrigin requested (jarBranch input) := by
  unfold jarBranch
  split
  · split
    next source found =>
      split
      · split
        · intro value same;cases same;exact admitted.jar source found
        · intro value found;cases found
      · exact store_origin _ _ _ (admitted.compile source found)
    · split
      · exact store_origin _ _ _ admitted.channel
      · exact store_origin _ _ _ admitted.parent
  · intro value found;cases found

theorem constructor_preserves_origin (requested : Resource) (input : Inputs)
    (admitted : Admission requested input) : IsOrigin requested (construct input) := by
  unfold construct
  split
  · exact store_origin _ _ _ admitted.parent
  · have jar := jar_preserves_origin requested input admitted
    split
    next value found =>
      intro result same;cases same;exact jar value found
    · unfold fileBranch
      split
      · exact store_origin _ _ _ admitted.file
      · intro value found;cases found

theorem uncompressed_compiled_resource (input : Inputs) (resource : Resource)
    (compiled : input.precompiled = true) (jar : input.jar = true)
    (item : input.jarItem = some resource) (valid : input.rawValid resource = true) :
    construct input = some ⟨resource,.rawSpan⟩ := by
  simp [construct,jarBranch,compiled,jar,item,valid]

theorem child_uncompiled_failure_stops (input : Inputs)
    (child : input.parent = false) (uncompiled : input.precompiled = false)
    (unavailable : input.requestParent = none) : construct input = none := by
  simp [construct,child,uncompiled,unavailable,store]

def cloneHandle (stored : Option Stored) : Option Resource :=
  match stored with
  | some ⟨origin,.parentHandle⟩ => some origin
  | _ => none

theorem clone_preserves_origin (stored : Option Stored) (requested : Resource)
    (admitted : IsOrigin requested stored) : ResourceOrigin requested (cloneHandle stored) := by
  intro resource found
  cases stored with
  | none => cases found
  | some value =>
    cases value with
    | mk origin kind =>
      cases kind <;> simp only [cloneHandle] at found
      · cases found
      · cases found;exact admitted _ rfl
      · cases found
      · cases found

theorem clone_requires_parent_handle (stored : Option Stored) (resource : Resource)
    (found : cloneHandle stored = some resource) : stored = some ⟨resource,.parentHandle⟩ := by
  cases stored with
  | none => cases found
  | some value =>
    cases value with
    | mk origin kind =>
      cases kind <;> simp only [cloneHandle] at found
      · cases found
      · cases found;rfl
      · cases found
      · cases found

def loaderValidity (inputs : Resource → Inputs) (resource : Resource) : Bool :=
  (construct (inputs resource)).isSome

theorem successful_manager_load_has_storage (inputs : Resource → Inputs)
    (state : State) (key : Key) (resource : Resource) (handle : Handle)
    (admitted : Admission resource (inputs resource))
    (found : (load (loaderValidity inputs) state key resource).answer = some handle) :
    ∃ stored, construct (inputs resource) = some stored ∧ stored.origin = resource ∧
      handle.resource = resource := by
  cases storage : construct (inputs resource) with
  | none => simp [load,loaderValidity,storage] at found
  | some stored =>
    have origin := constructor_preserves_origin resource (inputs resource) admitted stored storage
    simp only [load,loaderValidity,storage,Option.isSome_some,ite_true] at found
    cases found
    exact ⟨stored,rfl,origin,rfl⟩

end HyphenDictionaryLoader
